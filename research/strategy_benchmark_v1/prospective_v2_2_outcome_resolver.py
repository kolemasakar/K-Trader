#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import pathlib
import statistics
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

BASE = pathlib.Path('/data/research/phase11g')
LEDGER_ROOT = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
OUTPUT_ROOT = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes'
FUNDING_ENDPOINT = 'https://fapi.binance.com/fapi/v1/fundingRate'
TARGET_R = 3.0
MAX_HOLD_BARS = 32
FEE_BPS = 5.0
SLIPPAGE_BPS = 2.0


def utc(value: str) -> datetime:
    text = value.strip()
    dt = datetime.fromisoformat(text[:-1] + '+00:00' if text.endswith('Z') else text)
    if dt.tzinfo is None or dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError('UTC timestamp required')
    return dt.astimezone(timezone.utc)


def z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def load_bars(path: pathlib.Path) -> list[dict]:
    out = []
    with path.open() as f:
        first = json.loads(next(f))
        if first.get('record_type') != 'manifest':
            raise RuntimeError(f'missing manifest in {path}')
        for line in f:
            d = json.loads(line)
            out.append({
                'open_time': utc(d['open_time']),
                'close_time': utc(d['close_time']),
                'open': float(d['open']),
                'high': float(d['high']),
                'low': float(d['low']),
                'close': float(d['close']),
            })
    return out


def adverse(raw: float, side: int, entry: bool) -> float:
    s = SLIPPAGE_BPS / 10000.0
    if entry:
        return raw * (1 + s) if side == 1 else raw * (1 - s)
    return raw * (1 - s) if side == 1 else raw * (1 + s)


def derive_raw_entry(executed_entry: float, side: int) -> float:
    s = SLIPPAGE_BPS / 10000.0
    return executed_entry / (1 + s) if side == 1 else executed_entry / (1 - s)


def funding_page(symbol: str, start_ms: int, end_ms: int) -> list[dict]:
    query = urllib.parse.urlencode({
        'symbol': symbol,
        'startTime': start_ms,
        'endTime': end_ms,
        'limit': 1000,
    })
    req = urllib.request.Request(
        FUNDING_ENDPOINT + '?' + query,
        headers={'User-Agent': 'K-Trader-Research/1.0'},
    )
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = json.load(response)
            if not isinstance(payload, list):
                raise RuntimeError(f'unexpected funding payload for {symbol}')
            return payload
        except Exception as exc:  # pragma: no cover - network retry
            last = exc
            if attempt == 3:
                raise
            time.sleep(0.5 * (2 ** attempt))
    raise last


def collect_funding(symbol: str, start: datetime, end: datetime) -> list[dict]:
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    cursor = start_ms
    by_time: dict[int, dict] = {}
    while cursor <= end_ms:
        page = funding_page(symbol, cursor, end_ms)
        if not page:
            break
        for row in page:
            t = int(row['fundingTime'])
            if start_ms <= t <= end_ms:
                by_time[t] = row
        last = max(int(row['fundingTime']) for row in page)
        if last < cursor:
            raise RuntimeError('funding pagination moved backward')
        nxt = last + 1
        if nxt <= cursor:
            raise RuntimeError('funding pagination stalled')
        cursor = nxt
        if len(page) < 1000:
            break
        time.sleep(0.05)
    return [by_time[t] for t in sorted(by_time)]


def funding_pct(side: int, entry: float, entry_time: datetime, exit_time: datetime, rows: list[dict]) -> float:
    s = int(entry_time.timestamp() * 1000)
    e = int(exit_time.timestamp() * 1000)
    total = 0.0
    for row in rows:
        t = int(row['fundingTime'])
        if s <= t <= e:
            signed = float(row['fundingRate']) * float(row['markPrice']) / entry
            total += signed if side == 1 else -signed
    return total


def choose_latest_valid_snapshot(as_of: datetime) -> tuple[pathlib.Path, dict]:
    candidates: list[tuple[datetime, pathlib.Path, dict]] = []
    for raw in glob.glob(str(BASE / 'v2_2_shadow_*/shadow_v1_1/summary.json')):
        p = pathlib.Path(raw)
        d = json.loads(p.read_text())
        if d.get('missing_symbols'):
            continue
        provenance = d.get('bundle_provenance') or {}
        if len(provenance) != int(d.get('panel_size') or 0):
            continue
        times = [utc(v['as_of']) for v in provenance.values() if v.get('as_of')]
        if not times:
            continue
        snap_as_of = min(times)
        if snap_as_of <= as_of:
            candidates.append((snap_as_of, p, d))
    if not candidates:
        raise RuntimeError('no valid prospective snapshot at/before requested as_of')
    candidates.sort(key=lambda x: (x[0], str(x[1])))
    _, summary_path, summary = candidates[-1]
    return summary_path.parent.parent / 'bundles', summary


def resolve_one(event: dict, bars: list[dict], funding_rows: list[dict], as_of: datetime) -> dict:
    side = 1 if event['side'] == 'LONG' else -1
    entry = float(event['entry_price'])
    stop = float(event['stop_price'])
    entry_time = utc(event['entry_time'])
    signal_time = utc(event['signal_bar_open_time'])
    risk = side * (entry - stop)
    if risk <= 0:
        raise RuntimeError('non-positive initial risk')
    risk_pct = risk / entry
    target = entry + side * TARGET_R * risk
    index_by_open = {b['open_time']: i for i, b in enumerate(bars)}
    if entry_time not in index_by_open:
        return {
            'status': 'SOURCE_ENTRY_BAR_UNAVAILABLE',
            'symbol': event['symbol'],
            'setup_family_id': event['setup_family_id'],
            'signal_bar_open_time': z(signal_time),
            'entry_time': z(entry_time),
        }
    entry_i = index_by_open[entry_time]
    available = [b for b in bars[entry_i:] if b['open_time'] < as_of and b['close_time'] < as_of]
    mfe = 0.0
    mae = 0.0
    threshold_times: dict[str, str | None] = {'0.5R': None, '1R': None, '2R': None, '3R': None}
    terminal = None
    raw_exit = None
    exit_time = None
    exit_i = None

    for offset, bar in enumerate(available):
        j = entry_i + offset
        # Frozen semantics: after 32 completed hold bars, exit at the next bar open before intrabar tests.
        if offset >= MAX_HOLD_BARS:
            terminal = 'TIME_EXIT'
            raw_exit = bar['open']
            exit_time = bar['open_time']
            exit_i = j
            break

        if side == 1:
            favorable = max(0.0, (bar['high'] - entry) / risk)
            adverse_exc = max(0.0, (entry - bar['low']) / risk)
            gap_stop = bar['open'] <= stop
            gap_target = bar['open'] >= target
            stop_hit = bar['low'] <= stop
            target_hit = bar['high'] >= target
        else:
            favorable = max(0.0, (entry - bar['low']) / risk)
            adverse_exc = max(0.0, (bar['high'] - entry) / risk)
            gap_stop = bar['open'] >= stop
            gap_target = bar['open'] <= target
            stop_hit = bar['high'] >= stop
            target_hit = bar['low'] <= target

        mfe = max(mfe, favorable)
        mae = max(mae, adverse_exc)
        for threshold in (0.5, 1.0, 2.0, 3.0):
            key = f'{threshold:g}R'
            if threshold_times[key] is None and favorable >= threshold:
                threshold_times[key] = z(bar['close_time'])

        if gap_stop:
            terminal, raw_exit, exit_time, exit_i = 'GAP_STOP', bar['open'], bar['open_time'], j
            break
        if gap_target:
            terminal, raw_exit, exit_time, exit_i = 'GAP_TARGET', bar['open'], bar['open_time'], j
            break
        # Same-bar ambiguity is STOP-first, matching the frozen harness.
        if stop_hit:
            terminal, raw_exit, exit_time, exit_i = 'STOP', stop, bar['close_time'], j
            break
        if target_hit:
            terminal, raw_exit, exit_time, exit_i = 'TARGET', target, bar['close_time'], j
            break

    out = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_outcome.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'symbol': event['symbol'],
        'side': event['side'],
        'setup_family_id': event['setup_family_id'],
        'signal_bar_open_time': z(signal_time),
        'entry_time': z(entry_time),
        'entry_price': entry,
        'stop_price': stop,
        'target_price_3R': target,
        'initial_risk_pct': risk_pct,
        'bars_observed': len(available),
        'mfe_R': mfe,
        'mae_R': mae,
        'time_to_R': threshold_times,
        'terminal_state': terminal,
        'resolved': terminal is not None,
        'as_of': z(as_of),
        'holdout_opened': False,
        'production_action': False,
        'clean_break_no_revisit': event.get('clean_break_no_revisit'),
        'level_v2_h1_open_space': event.get('level_v2_h1_open_space'),
        'level_v2_h1_next_level_R': event.get('level_v2_h1_next_level_R'),
    }

    if terminal is None:
        out['outcome_status'] = 'CENSORED_OPEN'
        return out

    assert raw_exit is not None and exit_time is not None and exit_i is not None
    executed_exit = adverse(raw_exit, side, False)
    gross = (executed_exit - entry) / entry if side == 1 else (entry - executed_exit) / entry
    fee = (FEE_BPS / 10000.0) * (1.0 + executed_exit / entry)
    fund = funding_pct(side, entry, entry_time, exit_time, funding_rows)
    net = gross - fee - fund
    raw_entry = derive_raw_entry(entry, side)
    raw_gross = (raw_exit - raw_entry) / raw_entry if side == 1 else (raw_entry - raw_exit) / raw_entry
    slippage_drag = raw_gross - gross
    out.update({
        'outcome_status': 'RESOLVED',
        'exit_time': z(exit_time),
        'raw_exit_price': raw_exit,
        'executed_exit_price': executed_exit,
        'hold_bars': exit_i - entry_i + 1,
        'gross_return_pct': gross,
        'fee_pct': fee,
        'funding_pct': fund,
        'slippage_return_drag_pct': slippage_drag,
        'net_return_pct': net,
        'realized_R': net / risk_pct,
        'win_net': net > 0,
    })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--as-of', required=True, type=utc)
    ap.add_argument('--base', default=str(BASE))
    ap.add_argument('--output', default=str(OUTPUT_ROOT))
    args = ap.parse_args()

    global BASE, LEDGER_ROOT, OUTPUT_ROOT
    BASE = pathlib.Path(args.base)
    LEDGER_ROOT = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
    OUTPUT_ROOT = pathlib.Path(args.output)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    ledger_events = load_jsonl(LEDGER_ROOT / 'deduplicated_events.jsonl')
    eligible = [e for e in ledger_events if e.get('status') == 'ELIGIBLE_SHADOW_SETUP']
    groups: dict[str, list[dict]] = defaultdict(list)
    for e in eligible:
        groups[e['setup_family_id']].append(e)
    for rows in groups.values():
        rows.sort(key=lambda e: (e.get('entry_time') or '', e.get('signal_bar_open_time') or '', e.get('symbol') or '', e.get('side') or ''))

    bundle_root, snapshot_summary = choose_latest_valid_snapshot(args.as_of)
    funding_cache: dict[str, list[dict]] = {}
    bars_cache: dict[str, list[dict]] = {}
    observations = []

    for family_id in sorted(groups):
        rows = groups[family_id]
        for idx, event in enumerate(rows):
            symbol = event['symbol']
            if symbol not in bars_cache:
                bars_cache[symbol] = load_bars(bundle_root / symbol / '15m.jsonl')
            if symbol not in funding_cache:
                first_entry = min(utc(e['entry_time']) for e in eligible if e['symbol'] == symbol)
                funding_cache[symbol] = collect_funding(symbol, first_entry, args.as_of)
            row = resolve_one(event, bars_cache[symbol], funding_cache[symbol], args.as_of)
            row['family_role'] = 'PRIMARY_REPRESENTATIVE' if idx == 0 else 'CORRELATED_DIAGNOSTIC_ONLY'
            row['counts_as_independent_family_evidence'] = idx == 0
            observations.append(row)

    family_rows = []
    for family_id in sorted(groups):
        members = [r for r in observations if r['setup_family_id'] == family_id]
        primary = next(r for r in members if r['family_role'] == 'PRIMARY_REPRESENTATIVE')
        family_rows.append({
            'setup_family_id': family_id,
            'primary_symbol': primary['symbol'],
            'primary_side': primary['side'],
            'primary_entry_time': primary['entry_time'],
            'observation_count': len(members),
            'resolved': primary['resolved'],
            'terminal_state': primary.get('terminal_state'),
            'realized_R': primary.get('realized_R'),
            'mfe_R': primary.get('mfe_R'),
            'mae_R': primary.get('mae_R'),
            'family_evidence_status': 'RESOLVED_PRIMARY' if primary['resolved'] else 'UNRESOLVED_PRIMARY',
        })

    obs_path = OUTPUT_ROOT / 'observations.jsonl'
    with obs_path.open('w') as f:
        for row in sorted(observations, key=lambda r: (r['entry_time'], r['symbol'], r['setup_family_id'])):
            f.write(json.dumps(row, sort_keys=True) + '\n')
    family_path = OUTPUT_ROOT / 'families.jsonl'
    with family_path.open('w') as f:
        for row in family_rows:
            f.write(json.dumps(row, sort_keys=True) + '\n')

    resolved = [r for r in family_rows if r['resolved']]
    realized = [float(r['realized_R']) for r in resolved if r.get('realized_R') is not None]
    wins = sum(x > 0 for x in realized)
    ledger_summary = json.loads((LEDGER_ROOT / 'ledger_summary.json').read_text())
    report = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_family_outcomes.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'as_of': z(args.as_of),
        'holdout_opened': False,
        'production_action': False,
        'family_semantics': 'earliest eligible entry is immutable primary representative',
        'target_R': TARGET_R,
        'max_hold_bars_m15': MAX_HOLD_BARS,
        'fee_bps_per_side': FEE_BPS,
        'slippage_bps_per_execution_side': SLIPPAGE_BPS,
        'latest_bundle_root': str(bundle_root),
        'latest_bundle_set_sha256': snapshot_summary.get('bundle_set_sha256'),
        'frozen_harness_sha256_values': ledger_summary.get('frozen_harness_sha256_values'),
        'protocol_sha256_values': ledger_summary.get('protocol_sha256_values'),
        'eligible_observation_count': len(observations),
        'unique_family_count': len(family_rows),
        'resolved_primary_family_count': len(resolved),
        'unresolved_primary_family_count': len(family_rows) - len(resolved),
        'resolved_win_count': wins,
        'resolved_loss_count': len(realized) - wins,
        'resolved_win_rate': wins / len(realized) if realized else None,
        'resolved_expectancy_R': statistics.fmean(realized) if realized else None,
        'observation_sha256': sha_file(obs_path),
        'family_sha256': sha_file(family_path),
        'evidence_status': (
            'OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES' if len(resolved) < 30 else
            'DIAGNOSTIC_30_49_RESOLVED_FAMILIES' if len(resolved) < 50 else
            'HYPOTHESIS_ONLY_50_99_RESOLVED_FAMILIES' if len(resolved) < 100 else
            'RECALIBRATION_PROPOSAL_ELIGIBLE_BY_SAMPLE_ONLY'
        ),
    }
    report['report_content_sha256'] = stable_hash(report)
    report_path = OUTPUT_ROOT / 'summary.json'
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', report_path, sha_file(report_path))


if __name__ == '__main__':
    main()
