#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from collections import defaultdict

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
LEVEL_TOL_ATR = 0.25


def load_jsonl(path: pathlib.Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def load_bars(path: pathlib.Path):
    out = []
    with path.open() as f:
        for line in f:
            d = json.loads(line)
            if d.get('record_type') != 'candle':
                continue
            out.append({
                'high': float(d['high']), 'low': float(d['low']), 'close': float(d['close'])
            })
    return out


def collapse(indices):
    episodes = []
    for i in indices:
        if not episodes or i - episodes[-1][-1] > 1:
            episodes.append([i])
        else:
            episodes[-1].append(i)
    return episodes


def metrics(rows):
    if not rows:
        return {'n': 0}
    rs = [float(r['net_R']) for r in rows]
    gp = sum(x for x in rs if x > 0)
    gl = -sum(x for x in rs if x < 0)
    return {
        'n': len(rows),
        'win_rate': sum(x > 0 for x in rs) / len(rows),
        'expectancy_R': statistics.fmean(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def grouped(rows, field):
    g = defaultdict(list)
    for r in rows:
        g[str(r.get(field))].append(r)
    return {k: metrics(v) for k, v in sorted(g.items())}


def bucket_count(n):
    if n <= 0:
        return '0'
    if n == 1:
        return '1'
    return '>=2'


def traversal_features(row, bars):
    if not row.get('strict_break_present'):
        return {'traversal_available': False}
    break_i = int(row['strict_break_i'])
    decision_i = int(row['h1_decision_index'])
    level = float(row['strict_level_price'])
    atr = float(row['h1_atr14'])
    entry = float(row['entry_price'])
    stop = float(row['stop_price'])
    risk = abs(entry - stop)
    side = 1 if row['side'] == 'LONG' else -1
    tol = LEVEL_TOL_ATR * atr
    if risk <= 0 or break_i >= decision_i or decision_i >= len(bars):
        return {'traversal_available': False}

    interactions = []
    states = []
    breakout_side = 0
    wrong_side = 0
    total = 0
    for i in range(break_i + 1, decision_i + 1):
        b = bars[i]
        total += 1
        if b['low'] <= level + tol and b['high'] >= level - tol:
            interactions.append(i)
        if b['close'] > level + tol:
            state = 1
        elif b['close'] < level - tol:
            state = -1
        else:
            state = 0
        states.append(state)
        breakout_side += int(state == side)
        wrong_side += int(state == -side)

    nonzero = [s for s in states if s != 0]
    crossings = sum(1 for a, b in zip(nonzero, nonzero[1:]) if a != b)
    episodes = collapse(interactions)
    first_revisit = episodes[0][0] if episodes else None
    last_revisit = episodes[-1][-1] if episodes else None

    return {
        'traversal_available': True,
        'revisit_episode_count': len(episodes),
        'revisit_episode_bucket': bucket_count(len(episodes)),
        'first_revisit_delay_bars': first_revisit - break_i if first_revisit is not None else None,
        'last_revisit_age_bars': decision_i - last_revisit if last_revisit is not None else None,
        'zone_crossing_count': crossings,
        'zone_crossing_bucket': bucket_count(crossings),
        'breakout_side_close_fraction': breakout_side / total if total else None,
        'wrong_side_close_count': wrong_side,
        'any_wrong_side_close': wrong_side > 0,
        'entry_distance_to_broken_level_R': abs(entry - level) / risk,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    src = root / 'combined_rules/level_context_v2_1_diag'
    out = root / 'combined_rules/level_context_v2_2_traversal'
    out.mkdir(parents=True, exist_ok=True)
    histories = {}
    report = {
        'schema_version': 'ktrader.level_context_v2_2.traversal.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'segments': {},
    }

    for seg in ('development', 'validation', 'non_holdout'):
        rows = load_jsonl(src / f'{seg}.jsonl')
        enriched = []
        for r in rows:
            symbol = r['symbol']
            if symbol not in histories:
                histories[symbol] = load_bars(pathlib.Path(manifest['merged_histories'][symbol]['1h']['path']))
            x = dict(r)
            x.update(traversal_features(x, histories[symbol]))
            enriched.append(x)
        with (out / f'{seg}.jsonl').open('w') as f:
            for r in enriched:
                f.write(json.dumps(r, sort_keys=True) + '\n')
        avail = [r for r in enriched if r.get('traversal_available')]
        report['segments'][seg] = {
            'overall': metrics(enriched),
            'available_n': len(avail),
            'by_revisit_episode_bucket': grouped(avail, 'revisit_episode_bucket'),
            'by_zone_crossing_bucket': grouped(avail, 'zone_crossing_bucket'),
            'by_any_wrong_side_close': grouped(avail, 'any_wrong_side_close'),
            'median_revisit_episode_count': statistics.median([r['revisit_episode_count'] for r in avail]) if avail else None,
            'median_zone_crossing_count': statistics.median([r['zone_crossing_count'] for r in avail]) if avail else None,
            'median_breakout_side_close_fraction': statistics.median([r['breakout_side_close_fraction'] for r in avail if r.get('breakout_side_close_fraction') is not None]) if avail else None,
        }

    p = out / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
