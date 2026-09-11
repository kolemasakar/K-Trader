#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib

BASE_PATH = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_1_backtest.py')
sp = importlib.util.spec_from_file_location('candidate_v2_1_base', BASE_PATH)
v = importlib.util.module_from_spec(sp)
sp.loader.exec_module(v)

b = v.b
ROOT = v.ROOT

SWING_RADIUS = 2
LEVEL_TOL_ATR = 0.20
MIN_LEVEL_TOUCHES = 2
MIN_STRUCTURAL_SPACE_R = 3.0


def _confirmed_pivots(h1, decision_idx):
    """Return causal H1 swing points known by decision_idx."""
    out = []
    # k+2 must already be closed, so k <= decision_idx-2.
    for k in range(SWING_RADIUS, max(SWING_RADIUS, decision_idx - SWING_RADIUS + 1)):
        if k + SWING_RADIUS > decision_idx:
            break
        hi = h1[k]['high']
        lo = h1[k]['low']
        if (
            hi > h1[k - 1]['high']
            and hi > h1[k - 2]['high']
            and hi >= h1[k + 1]['high']
            and hi >= h1[k + 2]['high']
        ):
            out.append((hi, 'H', k))
        if (
            lo < h1[k - 1]['low']
            and lo < h1[k - 2]['low']
            and lo <= h1[k + 1]['low']
            and lo <= h1[k + 2]['low']
        ):
            out.append((lo, 'L', k))
    return out


def _cluster_levels(points, tolerance):
    points = sorted(points, key=lambda x: x[0])
    clusters = []
    for price, pivot_type, k in points:
        if not clusters or abs(price - clusters[-1]['price']) > tolerance:
            clusters.append({'price': price, 'items': [(price, pivot_type, k)]})
        else:
            c = clusters[-1]
            c['items'].append((price, pivot_type, k))
            c['price'] = sum(x[0] for x in c['items']) / len(c['items'])

    for c in clusters:
        c['touch_count'] = len(c['items'])
        c['high_touches'] = sum(1 for x in c['items'] if x[1] == 'H')
        c['low_touches'] = sum(1 for x in c['items'] if x[1] == 'L')
        c['mirror_role_change'] = c['high_touches'] > 0 and c['low_touches'] > 0
        c['last_pivot_index'] = max(x[2] for x in c['items'])
    return clusters


def level_features(h1, hx, decision_idx, entry, stop, side):
    atr = hx['atr14'][decision_idx]
    if atr is None or atr <= 0:
        return None

    risk = abs(entry - stop)
    if risk <= 0:
        return None

    points = _confirmed_pivots(h1, decision_idx)
    clusters = _cluster_levels(points, LEVEL_TOL_ATR * atr)
    confirmed = [c for c in clusters if c['touch_count'] >= MIN_LEVEL_TOUCHES]

    ahead = [c for c in confirmed if side * (c['price'] - entry) > 0]
    behind = [c for c in confirmed if side * (c['price'] - entry) < 0]

    next_level = (
        min(ahead, key=lambda c: side * (c['price'] - entry))
        if ahead
        else None
    )
    anchor = (
        min(behind, key=lambda c: abs(c['price'] - entry))
        if behind
        else None
    )

    start = max(0, decision_idx - 7)
    recent = h1[start:decision_idx + 1]
    near_closes = sum(1 for x in recent if abs(x['close'] - entry) <= 0.35 * atr)
    recent_width_atr = (
        (max(x['high'] for x in recent) - min(x['low'] for x in recent)) / atr
        if recent
        else None
    )
    floating_zone = bool(
        recent
        and near_closes >= 4
        and recent_width_atr is not None
        and recent_width_atr <= 3.0
    )

    next_r = (
        side * (next_level['price'] - entry) / risk
        if next_level is not None
        else None
    )
    anchor_r = (
        abs(anchor['price'] - entry) / risk
        if anchor is not None
        else None
    )

    return {
        'level_detector_version': 'h1_pivot_cluster_v1',
        'level_tolerance_atr': LEVEL_TOL_ATR,
        'min_level_touches': MIN_LEVEL_TOUCHES,
        'confirmed_level_count': len(confirmed),
        'next_confirmed_level_R': next_r,
        'open_space': next_level is None,
        'next_level_touch_count': next_level['touch_count'] if next_level else 0,
        'next_level_mirror': next_level['mirror_role_change'] if next_level else False,
        'anchor_level_R': anchor_r,
        'anchor_touch_count': anchor['touch_count'] if anchor else 0,
        'anchor_mirror': anchor['mirror_role_change'] if anchor else False,
        'floating_zone_flag': floating_zone,
        'recent_near_closes': near_closes,
        'recent_width_atr': recent_width_atr,
        'structural_space_gate_pass': next_r is None or next_r >= MIN_STRUCTURAL_SPACE_R,
    }


def backtest_symbol(symbol, m15, h1, funding, start, end, bps):
    mx = b.indicators(m15)
    hx = b.indicators(h1)
    h1cts = [x['close_dt'] for x in h1]

    trades = []
    pos = None
    pending = None
    pending_exit = False
    last_episode = set()
    censored = 0

    for i in range(max(1, start - 1), end):
        bar = m15[i]

        if pos is not None and pending_exit:
            trades.append(
                b.finish(symbol, pos, i, bar['open_dt'], bar['open'], 'TIME_EXIT', bps, funding)
            )
            pos = None
            pending_exit = False

        if pos is None and pending is not None and i >= start:
            side = pending['side']
            ep = b.adverse(bar['open'], side, True, bps)
            stop = pending['stop_raw']
            dist = side * (ep - stop)
            risk_pct = dist / ep if ep > 0 else 0.0

            if dist > 0 and risk_pct >= v.MIN_RISK_PCT and pending['episode_key'] not in last_episode:
                decision_idx = int(pending['features']['h1_index'])
                lf = level_features(h1, hx, decision_idx, ep, stop, side)
                if lf is not None and lf['structural_space_gate_pass']:
                    features = dict(pending['features'])
                    features.update(lf)
                    pos = {
                        'side': side,
                        'entry_i': i,
                        'entry_time': bar['open_dt'],
                        'entry': ep,
                        'stop': stop,
                        'target': ep + side * b.TARGET_R * dist,
                        'risk_pct': risk_pct,
                        'episode_key': pending['episode_key'],
                        'features': features,
                    }
                    last_episode.add(pending['episode_key'])
            pending = None

        if pos is not None:
            gap_stop = (
                (pos['side'] == 1 and bar['open'] <= pos['stop'])
                or (pos['side'] == -1 and bar['open'] >= pos['stop'])
            )
            gap_target = (
                (pos['side'] == 1 and bar['open'] >= pos['target'])
                or (pos['side'] == -1 and bar['open'] <= pos['target'])
            )
            if gap_stop:
                trades.append(
                    b.finish(symbol, pos, i, bar['open_dt'], bar['open'], 'GAP_STOP', bps, funding)
                )
                pos = None
            elif gap_target:
                trades.append(
                    b.finish(symbol, pos, i, bar['open_dt'], bar['open'], 'GAP_TARGET', bps, funding)
                )
                pos = None
            else:
                stop_hit = (
                    (pos['side'] == 1 and bar['low'] <= pos['stop'])
                    or (pos['side'] == -1 and bar['high'] >= pos['stop'])
                )
                target_hit = (
                    (pos['side'] == 1 and bar['high'] >= pos['target'])
                    or (pos['side'] == -1 and bar['low'] <= pos['target'])
                )
                if stop_hit:
                    trades.append(
                        b.finish(symbol, pos, i, bar['close_dt'], pos['stop'], 'STOP', bps, funding)
                    )
                    pos = None
                elif target_hit:
                    trades.append(
                        b.finish(symbol, pos, i, bar['close_dt'], pos['target'], 'TARGET', bps, funding)
                    )
                    pos = None

        if i >= end - 1:
            continue

        if pos is not None:
            if i - pos['entry_i'] + 1 >= b.MAX_HOLD_BARS:
                pending_exit = True
        elif pending is None:
            s = v.signal_at(i, m15, mx, h1, hx, h1cts)
            if s is not None and s['episode_key'] not in last_episode:
                pending = s

    if pos is not None:
        censored += 1

    return trades, censored


def run_segment(m15s, h1s, funds, segment, bps):
    alltr = []
    cens = 0
    syms = sorted(m15s)
    for s in syms:
        n = len(m15s[s])
        d, vv = b.split(n)
        if segment == 'development':
            a, z = 0, d
        elif segment == 'validation':
            a, z = d, vv
        elif segment == 'non_holdout':
            a, z = 0, vv
        elif segment == 'holdout':
            a, z = vv, n
        else:
            raise ValueError(segment)
        tr, c = backtest_symbol(s, m15s[s], h1s[s], funds[s], a, z, bps)
        alltr.extend(tr)
        cens += c
    return v.metrics(alltr, syms, cens), alltr


def main():
    manifest = json.loads((ROOT / 'sources/sources_manifest.json').read_text())
    protocol = json.loads((ROOT / 'protocol.json').read_text())
    syms = protocol['primary_panel']['symbols']

    m15s = {}
    h1s = {}
    funds = {}
    for s in syms:
        m15s[s] = b.load_bars(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
        h1s[s] = b.load_bars(pathlib.Path(manifest['merged_histories'][s]['1h']['path']))
        funds[s] = b.load_funding(pathlib.Path(manifest['funding'][s]['path']))

    out = {
        'schema_version': 'ktrader.candidate_rule_set_v2_2_preholdout.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'holdout_opened': False,
        'parameters': {
            'target_r': b.TARGET_R,
            'max_hold_bars_m15': b.MAX_HOLD_BARS,
            'buffer_atr': b.BUFFER_ATR,
            'pullback_window': b.PULLBACK_WINDOW,
            'min_h1_ema_sep_atr': v.MIN_H1_SEP_ATR,
            'max_signal_body_fraction': v.MAX_SIGNAL_BODY_FRAC,
            'min_risk_pct': v.MIN_RISK_PCT,
            'level_detector_version': 'h1_pivot_cluster_v1',
            'swing_radius': SWING_RADIUS,
            'level_tolerance_atr': LEVEL_TOL_ATR,
            'min_level_touches': MIN_LEVEL_TOUCHES,
            'min_structural_space_r': MIN_STRUCTURAL_SPACE_R,
            'fee_bps_per_side': b.FEE_BPS,
            'slippage_bps_base': 2.0,
            'slippage_bps_stress': 5.0,
        },
        'segments': {},
    }

    trade_dir = ROOT / 'combined_rules/v2_2_trades'
    trade_dir.mkdir(parents=True, exist_ok=True)

    for seg in ('development', 'validation', 'non_holdout'):
        m, tr = run_segment(m15s, h1s, funds, seg, b.SLIPPAGE_BPS['base'])
        out['segments'][seg] = m
        with (trade_dir / f'{seg}.jsonl').open('w') as f:
            for t in sorted(tr, key=lambda x: (x['entry_time'], x['symbol'])):
                f.write(json.dumps(t, sort_keys=True) + '\n')

    stress, _ = run_segment(m15s, h1s, funds, 'non_holdout', b.SLIPPAGE_BPS['stress'])
    out['stress_non_holdout'] = stress

    val = out['segments']['validation']
    non = out['segments']['non_holdout']
    reasons = []

    if non['completed_trades'] < 100:
        reasons.append('NON_HOLDOUT_SAMPLE_LT_100')
    if val['completed_trades'] < 30:
        reasons.append('VALIDATION_SAMPLE_LT_30')

    for label, m in [('NON_HOLDOUT', non), ('VALIDATION', val)]:
        if m['win_rate'] is None or m['win_rate'] < 0.50:
            reasons.append(label + '_WIN_RATE_LT_50')
        if m['expectancy_R'] is None or m['expectancy_R'] <= 0:
            reasons.append(label + '_EXPECTANCY_R_NONPOSITIVE')
        if m['profit_factor_R'] is None or m['profit_factor_R'] <= 1:
            reasons.append(label + '_PF_R_LE_1')

    if stress['expectancy_R'] is None or stress['expectancy_R'] <= 0:
        reasons.append('STRESS_EXPECTANCY_R_NONPOSITIVE')

    out['promotion_gate'] = {
        'pass': not reasons,
        'reasons': reasons,
        'holdout_authorized': not reasons,
    }

    report = ROOT / 'combined_rules/v2_2_preholdout_report.json'
    report.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')

    candidate = {
        'schema_version': 'ktrader.candidate_rule_set.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'status': 'PREHOLDOUT_EVALUATED' if reasons else 'PREHOLDOUT_PROMOTION_GATE_PASS',
        'production_approved': False,
        'holdout_authorized': not reasons,
        'report_path': str(report),
        'report_sha256': b.sha_file(report),
        'parameters': out['parameters'],
        'promotion_gate': out['promotion_gate'],
    }
    candidate_path = ROOT / 'combined_rules/candidate_rule_set_v2_2.json'
    candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + '\n')

    print('REPORT', report, b.sha_file(report))
    print('CANDIDATE', candidate_path, b.sha_file(candidate_path))
    print(json.dumps(out['promotion_gate'], sort_keys=True))
    for k, m in out['segments'].items():
        print(k, json.dumps(m, sort_keys=True))
    print('stress_non_holdout', json.dumps(stress, sort_keys=True))


if __name__ == '__main__':
    main()
