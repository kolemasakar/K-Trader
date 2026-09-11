#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
from collections import defaultdict
from datetime import datetime

ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')


def ts(v):
    return datetime.fromisoformat(v.replace('Z', '+00:00'))


def load_jsonl(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def load_candles(path):
    out = []
    with path.open() as f:
        for line in f:
            d = json.loads(line)
            if d.get('record_type') != 'candle':
                continue
            out.append({
                'open_time': d['open_time'], 'close_time': d['close_time'],
                'open_dt': ts(d['open_time']), 'close_dt': ts(d['close_time']),
                'open': float(d['open']), 'high': float(d['high']), 'low': float(d['low']), 'close': float(d['close']),
                'quote_volume': float(d.get('quote_volume') or 0.0),
                'taker_buy_quote_volume': float(d.get('taker_buy_quote_volume') or 0.0),
            })
    return out


def atr_wilder(bars, n=14):
    tr, prev = [], None
    for b in bars:
        x = b['high'] - b['low'] if prev is None else max(b['high'] - b['low'], abs(b['high'] - prev), abs(b['low'] - prev))
        tr.append(x); prev = b['close']
    out = [None] * len(bars)
    if len(tr) < n:
        return out
    a = sum(tr[:n]) / n; out[n-1] = a
    for i in range(n, len(tr)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def median_prior(values, i, n=20):
    if i < n:
        return None
    x = values[i-n:i]
    return statistics.median(x) if x else None


def signal_index(bars, entry_time):
    opens = [b['open_dt'] for b in bars]
    i = bisect.bisect_left(opens, ts(entry_time))
    return i - 1 if i > 0 else None


def bucket_rel_volume(x):
    if x is None: return 'N/A'
    if x < 0.75: return '<0.75x'
    if x < 1.25: return '0.75-1.25x'
    if x < 1.80: return '1.25-1.80x'
    return '>=1.80x'


def bucket_range_atr(x):
    if x is None: return 'N/A'
    if x < 0.8: return '<0.8'
    if x < 1.2: return '0.8-1.2'
    if x < 1.8: return '1.2-1.8'
    return '>=1.8'


def causal_features(bars, atrs, i):
    if i is None or i < 20 or i >= len(bars):
        return None
    b = bars[i]; atr = atrs[i]
    if atr is None or atr <= 0:
        return None
    rng = max(1e-15, b['high'] - b['low'])
    qv_med = median_prior([x['quote_volume'] for x in bars], i, 20)
    relvol = b['quote_volume'] / qv_med if qv_med and qv_med > 0 else None
    close_loc = (b['close'] - b['low']) / rng
    body_frac = abs(b['close'] - b['open']) / rng
    upper_wick = (b['high'] - max(b['open'], b['close'])) / rng
    lower_wick = (min(b['open'], b['close']) - b['low']) / rng
    prev_close = bars[i-1]['close']
    up = b['close'] > prev_close
    down = b['close'] < prev_close
    range_atr = rng / atr
    buy_share = b['taker_buy_quote_volume'] / b['quote_volume'] if b['quote_volume'] > 0 else None

    # Diagnostic candidate labels only. These are explicit research heuristics,
    # not canonical VSA definitions and never trading gates.
    labels = []
    if up and relvol is not None and relvol < 0.75 and range_atr < 0.8 and close_loc < 0.75:
        labels.append('ND_CANDIDATE')
    if down and relvol is not None and relvol < 0.75 and range_atr < 0.8 and close_loc > 0.25:
        labels.append('NS_CANDIDATE')
    if relvol is not None and relvol < 0.80 and range_atr <= 1.0 and lower_wick >= 0.35 and close_loc >= 0.60:
        labels.append('TEST_CANDIDATE')
    if relvol is not None and relvol >= 1.20 and range_atr >= 0.8 and upper_wick >= 0.35 and close_loc <= 0.35:
        labels.append('UT_CANDIDATE')
    if up and relvol is not None and relvol >= 1.80 and range_atr >= 1.20 and close_loc <= 0.65:
        labels.append('BC_CANDIDATE')
    if down and relvol is not None and relvol >= 1.80 and range_atr >= 1.20 and close_loc >= 0.35:
        labels.append('SC_CANDIDATE')
    if relvol is not None and relvol >= 1.50 and lower_wick >= 0.30 and close_loc >= 0.50:
        labels.append('SV_BULL_CANDIDATE')
    if relvol is not None and relvol >= 1.50 and upper_wick >= 0.30 and close_loc <= 0.50:
        labels.append('SV_BEAR_CANDIDATE')

    return {
        'signal_bar_open_time': b['open_time'],
        'relative_quote_volume_median20': relvol,
        'range_atr14': range_atr,
        'close_location': close_loc,
        'body_fraction': body_frac,
        'upper_wick_fraction': upper_wick,
        'lower_wick_fraction': lower_wick,
        'taker_buy_quote_share': buy_share,
        'bar_direction_vs_prev_close': 'UP' if up else ('DOWN' if down else 'FLAT'),
        'relative_volume_bucket': bucket_rel_volume(relvol),
        'range_atr_bucket': bucket_range_atr(range_atr),
        'vsa_candidate_labels': labels,
    }


def perf(rows):
    if not rows: return {'n': 0}
    rs = [float(r['net_R']) for r in rows]
    gp = sum(max(0.0, x) for x in rs); gl = -sum(min(0.0, x) for x in rs)
    return {
        'n': len(rows),
        'win_rate': sum(x > 0 for x in rs) / len(rs),
        'expectancy_R': statistics.fmean(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def grouped(rows, field):
    g = defaultdict(list)
    for r in rows: g[str(r.get(field))].append(r)
    return {k: perf(v) for k, v in sorted(g.items())}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(ROOT)); args = ap.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    report = {
        'schema_version': 'ktrader.vsa_volume_features.v2_2.diagnostic.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'labels_are_canonical_vsa': False,
        'warning': 'candidate labels are preregisterable feature hypotheses only; no VSA label is a hard gate',
        'segments': {},
    }

    cache = {}
    for segment in ('development','validation','non_holdout'):
        trades = load_jsonl(root / 'combined_rules/v2_2_trades' / f'{segment}.jsonl')
        rows = []
        for t in trades:
            s = t['symbol']
            if s not in cache:
                bars = load_candles(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
                cache[s] = (bars, atr_wilder(bars, 14))
            bars, atrs = cache[s]
            feat = causal_features(bars, atrs, signal_index(bars, t['entry_time']))
            row = dict(t)
            if feat: row.update(feat)
            rows.append(row)

        label_groups = defaultdict(list)
        for r in rows:
            labels = r.get('vsa_candidate_labels') or []
            if not labels:
                label_groups['NO_LABEL'].append(r)
            for label in labels:
                label_groups[label].append(r)

        report['segments'][segment] = {
            'overall': perf(rows),
            'by_relative_volume_bucket': grouped(rows, 'relative_volume_bucket'),
            'by_range_atr_bucket': grouped(rows, 'range_atr_bucket'),
            'by_bar_direction': grouped(rows, 'bar_direction_vs_prev_close'),
            'by_vsa_candidate_label': {k: perf(v) for k, v in sorted(label_groups.items())},
            'feature_availability_n': sum('relative_quote_volume_median20' in r for r in rows),
        }

        out = root / 'combined_rules/vsa_volume_features_v2_2'
        out.mkdir(parents=True, exist_ok=True)
        with (out / f'{segment}.jsonl').open('w') as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + '\n')

    p = root / 'combined_rules/vsa_volume_features_v2_2/report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
