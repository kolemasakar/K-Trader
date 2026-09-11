#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import statistics
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
BASE_PATH = HERE / 'level_context_v2_features.py'
sp = importlib.util.spec_from_file_location('level_context_v2', BASE_PATH)
lc = importlib.util.module_from_spec(sp)
sp.loader.exec_module(lc)

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
STRICT_BREAK_FRESH_BARS_H1 = 8


def load_jsonl(path: pathlib.Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def trade_metrics(rows):
    if not rows:
        return {'n': 0}
    rs = [float(r['net_R']) for r in rows]
    wins = sum(r > 0 for r in rs)
    gp = sum(r for r in rs if r > 0)
    gl = -sum(r for r in rs if r < 0)
    return {
        'n': len(rows),
        'win_rate': wins / len(rows),
        'expectancy_R': statistics.fmean(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def grouped(rows, key):
    groups = defaultdict(list)
    for r in rows:
        groups[str(r.get(key))].append(r)
    return {k: trade_metrics(v) for k, v in sorted(groups.items())}


def rejection_bucket(value):
    if value is None:
        return 'N/A'
    value = float(value)
    if value < 0.25:
        return '<0.25'
    if value < 0.50:
        return '0.25-0.50'
    return '>=0.50'


def age_bucket(value):
    if value is None:
        return 'N/A'
    value = int(value)
    if value <= 8:
        return '<=8'
    if value <= 24:
        return '9-24'
    return '>24'


def strict_level_break_features(bars, decision_dt, entry, stop, side):
    close_times = [b['close_dt'] for b in bars]
    decision_idx = lc.last_closed_index(close_times, decision_dt)
    atrs = lc.atr_wilder(bars, 14)
    if decision_idx < 20 or decision_idx >= len(bars):
        return {'strict_break_available': False}
    atr = atrs[decision_idx]
    risk = abs(entry - stop)
    if atr is None or atr <= 0 or risk <= 0:
        return {'strict_break_available': False}

    start = max(0, decision_idx - lc.H1_LOOKBACK)
    tolerance = lc.LEVEL_TOL_ATR * atr
    points = lc.confirmed_pivots(bars, decision_idx, lc.H1_LOOKBACK)
    clusters = lc.cluster_pivots(points, tolerance)
    events = []

    for cluster in clusters:
        relevant_kind = 'H' if side == 1 else 'L'
        relevant = [p for p in cluster['pivots'] if p['kind'] == relevant_kind]
        if len(relevant) < 2:
            continue

        first_scan = max(start + 1, min(p['confirmed_i'] for p in relevant) + 1)
        for i in range(first_scan, decision_idx + 1):
            pre = [p for p in relevant if p['confirmed_i'] < i]
            if len(pre) < 2:
                continue
            price = statistics.fmean(p['price'] for p in pre)
            prev_close = bars[i - 1]['close']
            close = bars[i]['close']
            if side == 1:
                crossed = prev_close <= price + tolerance and close > price + tolerance
            else:
                crossed = prev_close >= price - tolerance and close < price - tolerance
            if not crossed:
                continue

            retest_i = None
            invalidation_i = None
            closes_held = 0
            total_after = 0
            for j in range(i + 1, decision_idx + 1):
                b = bars[j]
                total_after += 1
                if side == 1:
                    held = b['close'] >= price
                    retest = b['low'] <= price + tolerance and b['close'] >= price
                    invalidated = b['close'] < price - tolerance
                else:
                    held = b['close'] <= price
                    retest = b['high'] >= price - tolerance and b['close'] <= price
                    invalidated = b['close'] > price + tolerance
                closes_held += int(held)
                if retest_i is None and retest:
                    retest_i = j
                if invalidation_i is None and invalidated:
                    invalidation_i = j

            events.append({
                'break_i': i,
                'level_price': price,
                'prebreak_pivot_count': len(pre),
                'break_displacement_atr': side * (close - price) / atr,
                'break_age_bars': decision_idx - i,
                'retest_present': retest_i is not None,
                'retest_age_bars': decision_idx - retest_i if retest_i is not None else None,
                'invalidated_after_break': invalidation_i is not None,
                'held_close_fraction': closes_held / total_after if total_after else 1.0,
                'level_distance_R_now': abs(entry - price) / risk,
            })
            break

    if not events:
        return {
            'strict_break_available': True,
            'strict_break_present': False,
            'strict_break_fresh': False,
            'strict_mirror_retest_present': False,
        }

    event = max(events, key=lambda x: x['break_i'])
    return {
        'strict_break_available': True,
        'strict_break_present': True,
        'strict_break_fresh': event['break_age_bars'] <= STRICT_BREAK_FRESH_BARS_H1,
        'strict_mirror_retest_present': event['retest_present'],
        **{f'strict_{k}': v for k, v in event.items()},
    }


def obstacle_evidence(row):
    if row.get('h1_open_space') is True:
        return 0
    score = 0
    if int(row.get('h1_next_level_touch_episodes') or 0) >= 2:
        score += 1
    if int(row.get('h1_next_level_false_break_count') or 0) > 0:
        score += 1
    if float(row.get('h1_next_level_rejection_tail_score') or 0.0) >= 0.50:
        score += 1
    age = row.get('h1_next_level_age_bars')
    if age is not None and int(age) <= 24:
        score += 1
    if row.get('h1_next_level_mirror') is True:
        score += 1
    return score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    out_dir = root / 'combined_rules/level_context_v2_1_diag'
    out_dir.mkdir(parents=True, exist_ok=True)

    histories = {}
    report = {
        'schema_version': 'ktrader.level_context_v2_1.diagnostics.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'strict_break_fresh_bars_h1': STRICT_BREAK_FRESH_BARS_H1,
        'segments': {},
    }

    for segment in ('development', 'validation', 'non_holdout'):
        trades = load_jsonl(root / 'combined_rules/v2_2_trades' / f'{segment}.jsonl')
        level_rows = load_jsonl(root / 'combined_rules/level_context_v2' / f'{segment}.jsonl')
        level_index = {(r['symbol'], r['entry_time'], r.get('episode_key')): r for r in level_rows}
        rows = []

        for trade in trades:
            symbol = trade['symbol']
            if symbol not in histories:
                histories[symbol] = lc.load_bars(pathlib.Path(manifest['merged_histories'][symbol]['1h']['path']))
            key = (symbol, trade['entry_time'], trade.get('episode_key'))
            row = dict(trade)
            row.update(level_index.get(key, {}))
            row.update(strict_level_break_features(
                histories[symbol],
                lc.ts(trade['entry_time']),
                float(trade['entry_price']),
                float(trade['stop_price']),
                1 if trade['side'] == 'LONG' else -1,
            ))
            row['h1_obstacle_evidence_count'] = obstacle_evidence(row)
            row['h1_next_level_rejection_bucket'] = rejection_bucket(row.get('h1_next_level_rejection_tail_score'))
            row['h1_next_level_age_bucket'] = age_bucket(row.get('h1_next_level_age_bars'))
            rows.append(row)

        with (out_dir / f'{segment}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + '\n')

        strict = [r for r in rows if r.get('strict_break_present')]
        mirrors = [r for r in rows if r.get('strict_mirror_retest_present')]
        obstacle = [r for r in rows if r.get('h1_open_space') is False]
        report['segments'][segment] = {
            'overall': trade_metrics(rows),
            'strict_break_n': len(strict),
            'strict_break_fresh_n': sum(bool(r.get('strict_break_fresh')) for r in rows),
            'strict_mirror_retest_n': len(mirrors),
            'h1_obstacle_n': len(obstacle),
            'by_strict_break_present': grouped(rows, 'strict_break_present'),
            'by_strict_break_fresh': grouped(rows, 'strict_break_fresh'),
            'by_strict_mirror_retest': grouped(rows, 'strict_mirror_retest_present'),
            'by_h1_open_space': grouped(rows, 'h1_open_space'),
            'by_h1_obstacle_evidence_count': grouped(rows, 'h1_obstacle_evidence_count'),
            'by_h1_next_level_type': grouped(obstacle, 'h1_next_level_type'),
            'by_h1_next_level_rejection_bucket': grouped(obstacle, 'h1_next_level_rejection_bucket'),
            'by_h1_next_level_age_bucket': grouped(obstacle, 'h1_next_level_age_bucket'),
            'strict_break_age_median': median([r.get('strict_break_age_bars') for r in strict]),
            'strict_break_displacement_atr_median': median([r.get('strict_break_displacement_atr') for r in strict]),
            'strict_break_held_fraction_mean': mean([r.get('strict_held_close_fraction') for r in strict]),
        }

    p = out_dir / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
