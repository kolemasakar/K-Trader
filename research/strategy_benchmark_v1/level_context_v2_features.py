#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import math
import pathlib
import statistics
from datetime import datetime

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
PIVOT_RADIUS = 2
LEVEL_TOL_ATR = 0.25
H1_LOOKBACK = 160
H4_LOOKBACK = 80
CONSOLIDATION_BARS = 8
FLOATING_WINDOW = 8


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def load_bars(path: pathlib.Path):
    bars = []
    with path.open() as f:
        for line in f:
            d = json.loads(line)
            if d.get('record_type') != 'candle':
                continue
            bars.append({
                'open_time': d['open_time'],
                'close_time': d['close_time'],
                'open_dt': ts(d['open_time']),
                'close_dt': ts(d['close_time']),
                'open': float(d['open']),
                'high': float(d['high']),
                'low': float(d['low']),
                'close': float(d['close']),
                'quote_volume': float(d.get('quote_volume') or 0.0),
            })
    return bars


def atr_wilder(bars, n=14):
    tr = []
    prev = None
    for b in bars:
        value = b['high'] - b['low'] if prev is None else max(
            b['high'] - b['low'], abs(b['high'] - prev), abs(b['low'] - prev)
        )
        tr.append(value)
        prev = b['close']
    out = [None] * len(bars)
    if len(tr) < n:
        return out
    value = sum(tr[:n]) / n
    out[n - 1] = value
    for i in range(n, len(tr)):
        value = (value * (n - 1) + tr[i]) / n
        out[i] = value
    return out


def last_closed_index(close_times, decision_dt):
    return bisect.bisect_right(close_times, decision_dt) - 1


def confirmed_pivots(bars, decision_idx, lookback, radius=PIVOT_RADIUS):
    if decision_idx < radius * 2:
        return []
    start = max(radius, decision_idx - lookback)
    last_candidate = decision_idx - radius
    points = []
    for k in range(start, last_candidate + 1):
        hi = bars[k]['high']
        lo = bars[k]['low']
        if all(hi > bars[k - j]['high'] for j in range(1, radius + 1)) and all(
            hi >= bars[k + j]['high'] for j in range(1, radius + 1)
        ):
            points.append({'price': hi, 'kind': 'H', 'pivot_i': k, 'confirmed_i': k + radius})
        if all(lo < bars[k - j]['low'] for j in range(1, radius + 1)) and all(
            lo <= bars[k + j]['low'] for j in range(1, radius + 1)
        ):
            points.append({'price': lo, 'kind': 'L', 'pivot_i': k, 'confirmed_i': k + radius})
    return points


def cluster_pivots(points, tolerance):
    clusters = []
    for p in sorted(points, key=lambda x: x['price']):
        if not clusters or abs(p['price'] - clusters[-1]['price']) > tolerance:
            clusters.append({'price': p['price'], 'pivots': [p]})
        else:
            c = clusters[-1]
            c['pivots'].append(p)
            c['price'] = statistics.fmean(x['price'] for x in c['pivots'])
    return clusters


def collapse_touch_episodes(indices):
    episodes = []
    for i in indices:
        if not episodes or i - episodes[-1][-1] > 1:
            episodes.append([i])
        else:
            episodes[-1].append(i)
    return episodes


def enrich_cluster(cluster, bars, start, decision_idx, tolerance, atr):
    price = cluster['price']
    touched = []
    false_break_up = []
    false_break_down = []
    max_penetration_atr = 0.0
    rejection_scores = []

    for i in range(start, decision_idx + 1):
        b = bars[i]
        interacts = b['low'] - tolerance <= price <= b['high'] + tolerance
        if not interacts:
            continue
        touched.append(i)

        if b['high'] > price + tolerance and b['close'] < price:
            false_break_up.append(i)
            max_penetration_atr = max(max_penetration_atr, (b['high'] - price) / atr)
        if b['low'] < price - tolerance and b['close'] > price:
            false_break_down.append(i)
            max_penetration_atr = max(max_penetration_atr, (price - b['low']) / atr)

        rng = max(1e-15, b['high'] - b['low'])
        upper_wick = b['high'] - max(b['open'], b['close'])
        lower_wick = min(b['open'], b['close']) - b['low']
        near_high = abs(b['high'] - price) <= tolerance * 1.5
        near_low = abs(b['low'] - price) <= tolerance * 1.5
        score = 0.0
        if near_high:
            score = max(score, upper_wick / rng)
        if near_low:
            score = max(score, lower_wick / rng)
        rejection_scores.append(score)

    episodes = collapse_touch_episodes(touched)
    high_pivots = sum(1 for p in cluster['pivots'] if p['kind'] == 'H')
    low_pivots = sum(1 for p in cluster['pivots'] if p['kind'] == 'L')
    mirror = high_pivots > 0 and low_pivots > 0

    if mirror:
        level_type = 'MIRROR'
    elif high_pivots and len(episodes) >= 3:
        level_type = 'REPEATED_RESISTANCE'
    elif low_pivots and len(episodes) >= 3:
        level_type = 'REPEATED_SUPPORT'
    elif high_pivots:
        level_type = 'RESISTANCE'
    elif low_pivots:
        level_type = 'SUPPORT'
    else:
        level_type = 'UNCLASSIFIED'

    first_touch = episodes[0][0] if episodes else None
    last_touch = episodes[-1][-1] if episodes else None
    return {
        **cluster,
        'level_type': level_type,
        'pivot_count': len(cluster['pivots']),
        'high_pivot_count': high_pivots,
        'low_pivot_count': low_pivots,
        'mirror_role_change': mirror,
        'touch_episode_count': len(episodes),
        'first_touch_i': first_touch,
        'last_touch_i': last_touch,
        'false_break_up_count': len(false_break_up),
        'false_break_down_count': len(false_break_down),
        'false_break_count': len(false_break_up) + len(false_break_down),
        'max_penetration_atr': max_penetration_atr,
        'rejection_tail_score': max(rejection_scores) if rejection_scores else 0.0,
    }


def most_recent_trend_break(points, bars, decision_idx, side, tolerance):
    best = None
    for p in points:
        if side == 1 and p['kind'] != 'H':
            continue
        if side == -1 and p['kind'] != 'L':
            continue
        start = p['confirmed_i'] + 1
        for i in range(start, decision_idx + 1):
            broken = bars[i]['close'] > p['price'] + tolerance if side == 1 else bars[i]['close'] < p['price'] - tolerance
            if broken:
                if best is None or i > best['break_i']:
                    best = {'level_price': p['price'], 'pivot_i': p['pivot_i'], 'break_i': i}
                break
    return best


def consolidation_features(bars, atr, decision_idx, entry):
    if atr is None or atr <= 0 or decision_idx < CONSOLIDATION_BARS - 1:
        return None
    search_start = max(CONSOLIDATION_BARS - 1, decision_idx - 24)
    best = None
    for end in range(search_start, decision_idx + 1):
        start = end - CONSOLIDATION_BARS + 1
        window = bars[start:end + 1]
        hi = max(b['high'] for b in window)
        lo = min(b['low'] for b in window)
        width_atr = (hi - lo) / atr
        avg_bar_atr = statistics.fmean((b['high'] - b['low']) / atr for b in window)
        overlaps = []
        for a, b in zip(window, window[1:]):
            overlap = max(0.0, min(a['high'], b['high']) - max(a['low'], b['low']))
            union = max(a['high'], b['high']) - min(a['low'], b['low'])
            overlaps.append(overlap / union if union > 0 else 0.0)
        overlap_mean = statistics.fmean(overlaps) if overlaps else 0.0
        is_consolidation = width_atr <= 2.5 and avg_bar_atr <= 0.9 and overlap_mean >= 0.25
        if is_consolidation:
            best = {
                'start_i': start,
                'end_i': end,
                'high': hi,
                'low': lo,
                'width_atr': width_atr,
                'avg_bar_atr': avg_bar_atr,
                'overlap_mean': overlap_mean,
                'entry_position': 'ABOVE' if entry > hi else ('BELOW' if entry < lo else 'INSIDE'),
            }
    return best


def floating_zone_features(bars, atr, decision_idx, entry):
    if atr is None or atr <= 0:
        return None
    start = max(0, decision_idx - FLOATING_WINDOW + 1)
    window = bars[start:decision_idx + 1]
    if len(window) < 3:
        return None

    near = sum(1 for b in window if abs(b['close'] - entry) <= 0.35 * atr) / len(window)
    overlaps = []
    for a, b in zip(window, window[1:]):
        overlap = max(0.0, min(a['high'], b['high']) - max(a['low'], b['low']))
        union = max(a['high'], b['high']) - min(a['low'], b['low'])
        overlaps.append(overlap / union if union > 0 else 0.0)
    overlap_mean = statistics.fmean(overlaps) if overlaps else 0.0
    path = sum(abs(window[i]['close'] - window[i - 1]['close']) for i in range(1, len(window)))
    efficiency = abs(window[-1]['close'] - window[0]['close']) / path if path > 0 else 0.0
    width_atr = (max(b['high'] for b in window) - min(b['low'] for b in window)) / atr

    width_component = max(0.0, min(1.0, (3.0 - width_atr) / 3.0))
    score = 0.35 * near + 0.35 * overlap_mean + 0.20 * (1.0 - efficiency) + 0.10 * width_component
    score = max(0.0, min(1.0, score))
    return {
        'floating_zone_score': score,
        'floating_zone_flag': score >= 0.55,
        'recent_close_near_fraction': near,
        'recent_overlap_mean': overlap_mean,
        'recent_directional_efficiency': efficiency,
        'recent_width_atr': width_atr,
    }


def timeframe_context(bars, decision_dt, entry, stop, side, lookback, prefix):
    close_times = [b['close_dt'] for b in bars]
    decision_idx = last_closed_index(close_times, decision_dt)
    atrs = atr_wilder(bars, 14)
    if decision_idx < 20 or decision_idx >= len(bars):
        return {f'{prefix}_available': False}
    atr = atrs[decision_idx]
    risk = abs(entry - stop)
    if atr is None or atr <= 0 or risk <= 0:
        return {f'{prefix}_available': False}

    start = max(0, decision_idx - lookback)
    points = confirmed_pivots(bars, decision_idx, lookback)
    tolerance = LEVEL_TOL_ATR * atr
    clusters = [enrich_cluster(c, bars, start, decision_idx, tolerance, atr) for c in cluster_pivots(points, tolerance)]
    confirmed = [c for c in clusters if c['pivot_count'] >= 2 or c['touch_episode_count'] >= 3]

    ahead = [c for c in confirmed if side * (c['price'] - entry) > 0]
    behind = [c for c in confirmed if side * (c['price'] - entry) < 0]
    next_level = min(ahead, key=lambda c: side * (c['price'] - entry)) if ahead else None
    anchor = min(behind, key=lambda c: abs(c['price'] - entry)) if behind else None

    trend_break = most_recent_trend_break(points, bars, decision_idx, side, tolerance)
    consolidation = consolidation_features(bars, atr, decision_idx, entry)
    floating = floating_zone_features(bars, atr, decision_idx, entry)

    out = {
        f'{prefix}_available': True,
        f'{prefix}_decision_index': decision_idx,
        f'{prefix}_atr14': atr,
        f'{prefix}_confirmed_level_count': len(confirmed),
        f'{prefix}_open_space': next_level is None,
        f'{prefix}_next_level_R': side * (next_level['price'] - entry) / risk if next_level else None,
        f'{prefix}_next_level_type': next_level['level_type'] if next_level else None,
        f'{prefix}_next_level_touch_episodes': next_level['touch_episode_count'] if next_level else 0,
        f'{prefix}_next_level_false_break_count': next_level['false_break_count'] if next_level else 0,
        f'{prefix}_next_level_rejection_tail_score': next_level['rejection_tail_score'] if next_level else None,
        f'{prefix}_next_level_age_bars': decision_idx - next_level['last_touch_i'] if next_level and next_level['last_touch_i'] is not None else None,
        f'{prefix}_next_level_mirror': next_level['mirror_role_change'] if next_level else False,
        f'{prefix}_anchor_level_R': abs(anchor['price'] - entry) / risk if anchor else None,
        f'{prefix}_anchor_level_type': anchor['level_type'] if anchor else None,
        f'{prefix}_anchor_touch_episodes': anchor['touch_episode_count'] if anchor else 0,
        f'{prefix}_anchor_false_break_count': anchor['false_break_count'] if anchor else 0,
        f'{prefix}_anchor_rejection_tail_score': anchor['rejection_tail_score'] if anchor else None,
        f'{prefix}_anchor_age_bars': decision_idx - anchor['last_touch_i'] if anchor and anchor['last_touch_i'] is not None else None,
        f'{prefix}_anchor_mirror': anchor['mirror_role_change'] if anchor else False,
        f'{prefix}_trend_break_present': trend_break is not None,
        f'{prefix}_trend_break_age_bars': decision_idx - trend_break['break_i'] if trend_break else None,
        f'{prefix}_trend_break_level_R': abs(entry - trend_break['level_price']) / risk if trend_break else None,
        f'{prefix}_consolidation_present': consolidation is not None,
        f'{prefix}_consolidation_width_atr': consolidation['width_atr'] if consolidation else None,
        f'{prefix}_consolidation_entry_position': consolidation['entry_position'] if consolidation else None,
    }
    if floating:
        out.update({f'{prefix}_{k}': v for k, v in floating.items()})
    return out


def extract_trade_context(trade, h1, h4):
    entry = float(trade['entry_price'])
    stop = float(trade['stop_price'])
    side = 1 if trade['side'] == 'LONG' else -1
    decision_dt = ts(trade['entry_time'])
    out = {
        'schema_version': 'ktrader.level_context_v2.v1',
        'symbol': trade['symbol'],
        'entry_time': trade['entry_time'],
        'episode_key': trade.get('episode_key'),
        'side': trade['side'],
    }
    out.update(timeframe_context(h1, decision_dt, entry, stop, side, H1_LOOKBACK, 'h1'))
    out.update(timeframe_context(h4, decision_dt, entry, stop, side, H4_LOOKBACK, 'h4'))
    return out


def load_trades(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def summarize(rows):
    n = len(rows)
    if not n:
        return {'n': 0}
    return {
        'n': n,
        'h1_available': sum(bool(r.get('h1_available')) for r in rows),
        'h4_available': sum(bool(r.get('h4_available')) for r in rows),
        'h1_open_space': sum(bool(r.get('h1_open_space')) for r in rows),
        'h4_open_space': sum(bool(r.get('h4_open_space')) for r in rows),
        'h1_floating': sum(bool(r.get('h1_floating_zone_flag')) for r in rows),
        'h4_floating': sum(bool(r.get('h4_floating_zone_flag')) for r in rows),
        'h1_trend_break': sum(bool(r.get('h1_trend_break_present')) for r in rows),
        'h4_trend_break': sum(bool(r.get('h4_trend_break_present')) for r in rows),
        'h1_mirror_next': sum(bool(r.get('h1_next_level_mirror')) for r in rows),
        'h4_mirror_next': sum(bool(r.get('h4_next_level_mirror')) for r in rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    out_dir = root / 'combined_rules/level_context_v2'
    out_dir.mkdir(parents=True, exist_ok=True)

    histories = {}
    summary = {'schema_version': 'ktrader.level_context_v2.summary.v1', 'segments': {}}
    for segment in ('development', 'validation', 'non_holdout'):
        trades = load_trades(root / 'combined_rules/v2_2_trades' / f'{segment}.jsonl')
        rows = []
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in histories:
                histories[symbol] = {
                    'h1': load_bars(pathlib.Path(manifest['merged_histories'][symbol]['1h']['path'])),
                    'h4': load_bars(pathlib.Path(manifest['merged_histories'][symbol]['4h']['path'])),
                }
            row = extract_trade_context(trade, histories[symbol]['h1'], histories[symbol]['h4'])
            rows.append(row)
        with (out_dir / f'{segment}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + '\n')
        summary['segments'][segment] = summarize(rows)

    report = out_dir / 'summary.json'
    report.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=2, sort_keys=True))
    print('REPORT', report)


if __name__ == '__main__':
    main()
