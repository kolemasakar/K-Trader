#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, hashlib, json, pathlib, statistics
from collections import defaultdict
from datetime import datetime, timezone

BASE = pathlib.Path('/data/research/phase11g')
LEDGER = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
PRIOR = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes'
OUTROOT = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1'
TARGET_R = 3.0
MAX_HOLD = 32
FEE_BPS = 5.0
SLIP_BPS = 2.0


def utc(s):
    d = datetime.fromisoformat(s[:-1] + '+00:00' if s.endswith('Z') else s)
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds() != 0:
        raise ValueError('UTC required')
    return d.astimezone(timezone.utc)


def z(d):
    return d.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_jsonl(p):
    if not p.exists():
        return []
    with p.open() as f:
        return [json.loads(x) for x in f if x.strip()]


def load_bars(p):
    out = []
    with p.open() as f:
        m = json.loads(next(f))
        if m.get('record_type') != 'manifest':
            raise RuntimeError(f'missing manifest: {p}')
        for line in f:
            d = json.loads(line)
            out.append({'open_time': utc(d['open_time']), 'close_time': utc(d['close_time']),
                        'open': float(d['open']), 'high': float(d['high']),
                        'low': float(d['low']), 'close': float(d['close'])})
    return out


def adverse(raw, side, entry):
    s = SLIP_BPS / 10000
    if entry:
        return raw * (1 + s) if side == 1 else raw * (1 - s)
    return raw * (1 - s) if side == 1 else raw * (1 + s)


def raw_entry(executed, side):
    s = SLIP_BPS / 10000
    return executed / (1 + s) if side == 1 else executed / (1 - s)


def latest_snapshot(as_of):
    xs = []
    for raw in glob.glob(str(BASE / 'v2_2_shadow_*/shadow_v1_1/summary.json')):
        p = pathlib.Path(raw)
        d = json.loads(p.read_text())
        prov = d.get('bundle_provenance') or {}
        if d.get('missing_symbols') or len(prov) != int(d.get('panel_size') or 0):
            continue
        times = [utc(x['as_of']) for x in prov.values() if x.get('as_of')]
        if times and min(times) <= as_of:
            xs.append((min(times), p, d))
    if not xs:
        raise RuntimeError('no valid snapshot')
    xs.sort(key=lambda x: (x[0], str(x[1])))
    _, p, d = xs[-1]
    return p.parent.parent / 'bundles', d


def obs_key(e):
    return (e['setup_family_id'], e['symbol'], e['side'], e['entry_time'],
            f"{float(e['entry_price']):.18g}", f"{float(e['stop_price']):.18g}")


def terminal_path(e, bars, as_of):
    side = 1 if e['side'] == 'LONG' else -1
    entry = float(e['entry_price']); stop = float(e['stop_price']); et = utc(e['entry_time'])
    risk = side * (entry - stop); target = entry + side * TARGET_R * risk
    if risk <= 0:
        raise RuntimeError('bad risk')
    idx = {b['open_time']: i for i, b in enumerate(bars)}
    if et not in idx:
        return {'setup_family_id': e['setup_family_id'], 'status': 'SOURCE_ENTRY_BAR_UNAVAILABLE', 'resolved': False}
    ei = idx[et]
    avail = [b for b in bars[ei:] if b['open_time'] < as_of and b['close_time'] < as_of]
    mfe = mae = 0.0; times = {k: None for k in ('0.5R', '1R', '2R', '3R')}
    term = rx = xt = xi = None
    for off, b in enumerate(avail):
        j = ei + off
        if off >= MAX_HOLD:
            term, rx, xt, xi = 'TIME_EXIT', b['open'], b['open_time'], j; break
        if side == 1:
            fav = max(0, (b['high'] - entry) / risk); adv = max(0, (entry - b['low']) / risk)
            gs, gt, sh, th = b['open'] <= stop, b['open'] >= target, b['low'] <= stop, b['high'] >= target
        else:
            fav = max(0, (entry - b['low']) / risk); adv = max(0, (b['high'] - entry) / risk)
            gs, gt, sh, th = b['open'] >= stop, b['open'] <= target, b['high'] >= stop, b['low'] <= target
        mfe = max(mfe, fav); mae = max(mae, adv)
        for v in (.5, 1, 2, 3):
            k = f'{v:g}R'
            if times[k] is None and fav >= v:
                times[k] = z(b['close_time'])
        if gs: term, rx, xt, xi = 'GAP_STOP', b['open'], b['open_time'], j; break
        if gt: term, rx, xt, xi = 'GAP_TARGET', b['open'], b['open_time'], j; break
        if sh: term, rx, xt, xi = 'STOP', stop, b['close_time'], j; break
        if th: term, rx, xt, xi = 'TARGET', target, b['close_time'], j; break
    return {'side_i': side, 'entry': entry, 'stop': stop, 'risk': risk, 'target': target,
            'entry_i': ei, 'bars_observed': len(avail), 'mfe_R': mfe, 'mae_R': mae,
            'time_to_R': times, 'terminal_state': term, 'raw_exit_price': rx,
            'exit_time_dt': xt, 'exit_i': xi, 'resolved': term is not None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--as-of', required=True)
    ap.add_argument('--prior-outcomes', default=str(PRIOR))
    args = ap.parse_args(); as_of = utc(args.as_of)
    events = [x for x in load_jsonl(LEDGER / 'deduplicated_events.jsonl') if x.get('status') == 'ELIGIBLE_SHADOW_SETUP']
    if any(utc(e['entry_time']) >= as_of for e in events):
        raise SystemExit('LEDGER_CONTAINS_FUTURE_OR_EQUAL_ENTRY_FOR_ASOF')
    groups = defaultdict(list)
    for e in events: groups[e['setup_family_id']].append(e)
    for rows in groups.values(): rows.sort(key=lambda e: (e.get('entry_time') or '', e.get('signal_bar_open_time') or '', e.get('symbol') or '', e.get('side') or ''))
    prior_rows = load_jsonl(pathlib.Path(args.prior_outcomes) / 'observations.jsonl')
    cache = {obs_key(r): r for r in prior_rows if r.get('resolved') and all(k in r for k in ('entry_price','stop_price'))}
    bundle_root, snap = latest_snapshot(as_of); bars_cache = {}; obs = []; reused = 0; unresolved = 0
    for fid in sorted(groups):
        for i, e in enumerate(groups[fid]):
            s = e['symbol']
            if s not in bars_cache: bars_cache[s] = load_bars(bundle_root / s / '15m.jsonl')
            path = terminal_path(e, bars_cache[s], as_of); key = obs_key(e)
            base = {'schema_version':'ktrader.candidate_v2_2.prospective_outcome.v1','strategy_id':'candidate_rule_set_v2_2',
                    'symbol':s,'side':e['side'],'setup_family_id':fid,'signal_bar_open_time':e['signal_bar_open_time'],
                    'entry_time':e['entry_time'],'entry_price':float(e['entry_price']),'stop_price':float(e['stop_price']),
                    'target_price_3R':path['target'],'initial_risk_pct':path['risk']/path['entry'],'bars_observed':path['bars_observed'],
                    'mfe_R':path['mfe_R'],'mae_R':path['mae_R'],'time_to_R':path['time_to_R'],'terminal_state':path['terminal_state'],
                    'resolved':path['resolved'],'as_of':z(as_of),'holdout_opened':False,'production_action':False,
                    'clean_break_no_revisit':e.get('clean_break_no_revisit'),'level_v2_h1_open_space':e.get('level_v2_h1_open_space'),
                    'level_v2_h1_next_level_R':e.get('level_v2_h1_next_level_R')}
            if path['resolved']:
                old = cache.get(key)
                if old is None:
                    raise SystemExit('NEWLY_RESOLVED_REQUIRES_FUNDING_SNAPSHOT ' + json.dumps({'symbol':s,'entry_time':e['entry_time'],'family':fid}))
                if old.get('terminal_state') != path['terminal_state'] or old.get('exit_time') != z(path['exit_time_dt']):
                    raise SystemExit('RESOLVED_CACHE_PATH_MISMATCH ' + json.dumps({'family':fid,'entry_time':e['entry_time']}))
                for k in ('outcome_status','exit_time','raw_exit_price','executed_exit_price','hold_bars','gross_return_pct','fee_pct','funding_pct','slippage_return_drag_pct','net_return_pct','realized_R','win_net'):
                    base[k] = old[k]
                reused += 1
            else:
                base['outcome_status'] = 'CENSORED_OPEN'; unresolved += 1
            base['family_role'] = 'PRIMARY_REPRESENTATIVE' if i == 0 else 'CORRELATED_DIAGNOSTIC_ONLY'
            base['counts_as_independent_family_evidence'] = i == 0
            obs.append(base)
    families = []
    for fid in sorted(groups):
        members = [x for x in obs if x['setup_family_id'] == fid]
        p = next(x for x in members if x['family_role'] == 'PRIMARY_REPRESENTATIVE')
        families.append({'setup_family_id':fid,'primary_symbol':p['symbol'],'primary_side':p['side'],'primary_entry_time':p['entry_time'],
                         'observation_count':len(members),'resolved':p['resolved'],'terminal_state':p.get('terminal_state'),
                         'realized_R':p.get('realized_R'),'mfe_R':p.get('mfe_R'),'mae_R':p.get('mae_R'),
                         'family_evidence_status':'RESOLVED_PRIMARY' if p['resolved'] else 'UNRESOLVED_PRIMARY'})
    stamp = as_of.strftime('%Y%m%dT%H%M%SZ'); out = OUTROOT / stamp
    out.mkdir(parents=True, exist_ok=False); op = out / 'observations.jsonl'; fp = out / 'families.jsonl'
    op.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in sorted(obs,key=lambda x:(x.get('entry_time',''),x.get('symbol','')))))
    fp.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in families))
    resolved = [x for x in families if x['resolved']]; rs = [x['realized_R'] for x in resolved if x.get('realized_R') is not None]; wins = sum(x > 0 for x in rs)
    ls = json.loads((LEDGER / 'ledger_summary.json').read_text())
    report = {'schema_version':'ktrader.candidate_v2_2.prospective_family_outcomes.offline_incremental.v1','strategy_id':'candidate_rule_set_v2_2',
              'as_of':z(as_of),'holdout_opened':False,'production_action':False,'network_used':False,
              'family_semantics':'earliest eligible entry is immutable primary representative','target_R':TARGET_R,'max_hold_bars_m15':MAX_HOLD,
              'fee_bps_per_side':FEE_BPS,'slippage_bps_per_execution_side':SLIP_BPS,'latest_bundle_root':str(bundle_root),
              'latest_bundle_set_sha256':snap.get('bundle_set_sha256'),'frozen_harness_sha256_values':ls.get('frozen_harness_sha256_values'),
              'protocol_sha256_values':ls.get('protocol_sha256_values'),'eligible_observation_count':len(obs),'unique_family_count':len(families),
              'resolved_primary_family_count':len(resolved),'unresolved_primary_family_count':len(families)-len(resolved),
              'resolved_win_count':wins,'resolved_loss_count':len(rs)-wins,'resolved_win_rate':wins/len(rs) if rs else None,
              'resolved_expectancy_R':statistics.fmean(rs) if rs else None,'cached_resolved_observation_reuse_count':reused,
              'unresolved_observation_count':unresolved,'prior_outcomes_path':str(pathlib.Path(args.prior_outcomes)),
              'observation_sha256':sha(op),'family_sha256':sha(fp),
              'evidence_status':'OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES' if len(resolved)<30 else ('DIAGNOSTIC_30_49_RESOLVED_FAMILIES' if len(resolved)<50 else ('HYPOTHESIS_ONLY_50_99_RESOLVED_FAMILIES' if len(resolved)<100 else 'RECALIBRATION_PROPOSAL_ELIGIBLE_BY_SAMPLE_ONLY'))}
    sp = out / 'summary.json'; sp.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True)); print('REPORT',sp,sha(sp))

if __name__ == '__main__': main()
