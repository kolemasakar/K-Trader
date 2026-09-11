#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
from collections import defaultdict
from datetime import datetime

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
THRESHOLDS_R = (0.5, 1.0, 2.0, 3.0)


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
            })
    return bars


def load_jsonl(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def find_entry_index(bars, entry_dt):
    opens = [b['open_dt'] for b in bars]
    i = bisect.bisect_left(opens, entry_dt)
    if i < len(bars) and bars[i]['open_dt'] == entry_dt:
        return i
    return max(0, i - 1)


def find_exit_index(bars, exit_dt, reason):
    if reason in {'TIME_EXIT', 'GAP_STOP', 'GAP_TARGET'}:
        opens = [b['open_dt'] for b in bars]
        i = bisect.bisect_left(opens, exit_dt)
        if i < len(bars) and bars[i]['open_dt'] == exit_dt:
            return i
        return max(0, i - 1)
    closes = [b['close_dt'] for b in bars]
    i = bisect.bisect_left(closes, exit_dt)
    if i < len(bars) and bars[i]['close_dt'] == exit_dt:
        return i
    return max(0, i - 1)


def favorable_adverse(side, entry, high, low):
    if side == 1:
        favorable = high - entry
        adverse = entry - low
    else:
        favorable = entry - low
        adverse = high - entry
    return max(0.0, favorable), max(0.0, adverse)


def terminal_excursions(side, entry, price):
    directional = side * (price - entry)
    return max(0.0, directional), max(0.0, -directional)


def threshold_key(value):
    return str(value).replace('.', '_')


def slope_R(bars, start_i, exit_i, side, risk, window):
    if risk <= 0:
        return None
    end = exit_i - 1
    if end < start_i:
        return None
    begin = max(start_i, end - window + 1)
    if begin >= end:
        return 0.0
    return side * (bars[end]['close'] - bars[begin]['close']) / risk


def trade_path_metrics(trade, bars):
    entry = float(trade['entry_price'])
    stop = float(trade['stop_price'])
    target = float(trade['target_price'])
    exit_price = float(trade['exit_price'])
    risk = abs(entry - stop)
    side = 1 if trade['side'] == 'LONG' else -1
    if risk <= 0:
        raise ValueError('non-positive risk distance')

    entry_dt = ts(trade['entry_time'])
    exit_dt = ts(trade['exit_time'])
    entry_i = find_entry_index(bars, entry_dt)
    exit_i = find_exit_index(bars, exit_dt, trade['exit_reason'])
    if exit_i < entry_i:
        raise ValueError(f'exit before entry: {trade["symbol"]} {trade["entry_time"]}')

    mfe = 0.0
    mae = 0.0
    time_to = {x: None for x in THRESHOLDS_R}
    time_to_mfe = 0
    time_to_mae = 0

    # Only completed bars strictly before the exit-event bar contribute full H/L.
    # The exit-event bar itself is represented only by the known execution event,
    # avoiding intrabar look-ahead/order assumptions.
    for j in range(entry_i, exit_i):
        fav, adv = favorable_adverse(side, entry, bars[j]['high'], bars[j]['low'])
        fav_R = fav / risk
        adv_R = adv / risk
        if fav_R > mfe:
            mfe = fav_R
            time_to_mfe = j - entry_i
        if adv_R > mae:
            mae = adv_R
            time_to_mae = j - entry_i
        for threshold in THRESHOLDS_R:
            if time_to[threshold] is None and fav_R >= threshold:
                time_to[threshold] = j - entry_i

    # Known terminal event only; do not inspect the exit bar's unseen intrabar extremes.
    if trade['exit_reason'] in {'STOP', 'GAP_STOP'}:
        terminal_price = stop if trade['exit_reason'] == 'STOP' else exit_price
    elif trade['exit_reason'] in {'TARGET', 'GAP_TARGET'}:
        terminal_price = target if trade['exit_reason'] == 'TARGET' else exit_price
    else:
        terminal_price = exit_price

    fav, adv = terminal_excursions(side, entry, terminal_price)
    fav_R = fav / risk
    adv_R = adv / risk
    if fav_R > mfe:
        mfe = fav_R
        time_to_mfe = exit_i - entry_i
    if adv_R > mae:
        mae = adv_R
        time_to_mae = exit_i - entry_i
    for threshold in THRESHOLDS_R:
        if time_to[threshold] is None and fav_R >= threshold:
            time_to[threshold] = exit_i - entry_i

    fee_R = float(trade.get('fee_pct') or 0.0) / float(trade['risk_pct'])
    funding_R = float(trade.get('funding_pct') or 0.0) / float(trade['risk_pct'])

    out = {
        'schema_version': 'ktrader.mfe_mae.v2_2.v1',
        'symbol': trade['symbol'],
        'side': trade['side'],
        'entry_time': trade['entry_time'],
        'exit_time': trade['exit_time'],
        'episode_key': trade.get('episode_key'),
        'exit_reason': trade['exit_reason'],
        'hold_bars': trade['hold_bars'],
        'risk_pct': trade['risk_pct'],
        'realized_R': trade['net_R'],
        'MFE_R': mfe,
        'MAE_R': mae,
        'time_to_MFE_bars': time_to_mfe,
        'time_to_MAE_bars': time_to_mae,
        'fee_R': fee_R,
        'funding_R': funding_R,
        'explicit_cost_R': fee_R + funding_R,
        'terminal_slope_4_R': slope_R(bars, entry_i, exit_i, side, risk, 4),
        'terminal_slope_8_R': slope_R(bars, entry_i, exit_i, side, risk, 8),
    }
    for threshold in THRESHOLDS_R:
        out[f'time_to_{threshold_key(threshold)}R_bars'] = time_to[threshold]
        out[f'reached_{threshold_key(threshold)}R'] = time_to[threshold] is not None
    return out


def merge_level_context(rows, level_rows):
    index = {
        (r['symbol'], r['entry_time'], r.get('episode_key')): r
        for r in level_rows
    }
    merged = []
    for r in rows:
        key = (r['symbol'], r['entry_time'], r.get('episode_key'))
        out = dict(r)
        lc = index.get(key)
        if lc:
            for k, v in lc.items():
                if k not in {'schema_version', 'symbol', 'entry_time', 'episode_key', 'side'}:
                    out[k] = v
        merged.append(out)
    return merged


def group_summary(rows):
    if not rows:
        return {'n': 0}
    stops = [r for r in rows if r['exit_reason'] in {'STOP', 'GAP_STOP'}]
    targets = [r for r in rows if r['exit_reason'] in {'TARGET', 'GAP_TARGET'}]
    time_exits = [r for r in rows if r['exit_reason'] == 'TIME_EXIT']
    return {
        'n': len(rows),
        'mean_realized_R': mean([r['realized_R'] for r in rows]),
        'median_MFE_R': median([r['MFE_R'] for r in rows]),
        'median_MAE_R': median([r['MAE_R'] for r in rows]),
        'mean_MFE_R': mean([r['MFE_R'] for r in rows]),
        'mean_MAE_R': mean([r['MAE_R'] for r in rows]),
        'median_time_to_MFE_bars': median([r['time_to_MFE_bars'] for r in rows]),
        'median_explicit_cost_R': median([r['explicit_cost_R'] for r in rows]),
        'stop_n': len(stops),
        'stop_reached_0_5R_first': sum(r['reached_0_5R'] for r in stops),
        'stop_reached_1_0R_first': sum(r['reached_1_0R'] for r in stops),
        'stop_reached_2_0R_first': sum(r['reached_2_0R'] for r in stops),
        'target_n': len(targets),
        'target_median_MAE_R': median([r['MAE_R'] for r in targets]),
        'time_exit_n': len(time_exits),
        'time_exit_positive_n': sum(r['realized_R'] > 0 for r in time_exits),
        'time_exit_median_MFE_R': median([r['MFE_R'] for r in time_exits]),
        'time_exit_median_terminal_slope_4_R': median([r['terminal_slope_4_R'] for r in time_exits]),
    }


def grouped(rows, field):
    buckets = defaultdict(list)
    for r in rows:
        buckets[str(r.get(field))].append(r)
    return {k: group_summary(v) for k, v in sorted(buckets.items())}


def risk_bucket(value):
    if value < 0.015:
        return '1.25-1.5%'
    if value < 0.02:
        return '1.5-2.0%'
    if value < 0.03:
        return '2.0-3.0%'
    return '>=3.0%'


def enrich_buckets(rows):
    out = []
    for r in rows:
        x = dict(r)
        x['risk_bucket'] = risk_bucket(float(r['risk_pct']))
        h1sep = x.get('h1_ema_sep_atr')
        if h1sep is None:
            x['trend_strength_bucket'] = 'N/A'
        elif h1sep < 0.4:
            x['trend_strength_bucket'] = '0.2-0.4'
        elif h1sep < 0.8:
            x['trend_strength_bucket'] = '0.4-0.8'
        else:
            x['trend_strength_bucket'] = '>=0.8'
        out.append(x)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    out_dir = root / 'combined_rules/mfe_mae_v2_2'
    out_dir.mkdir(parents=True, exist_ok=True)

    histories = {}
    report = {
        'schema_version': 'ktrader.mfe_mae.v2_2.report.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'actual_path_only': True,
        'holdout_opened': False,
        'segments': {},
    }

    for segment in ('development', 'validation', 'non_holdout'):
        trades = load_jsonl(root / 'combined_rules/v2_2_trades' / f'{segment}.jsonl')
        rows = []
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in histories:
                histories[symbol] = load_bars(pathlib.Path(manifest['merged_histories'][symbol]['15m']['path']))
            row = trade_path_metrics(trade, histories[symbol])
            # Carry frozen causal features for grouping.
            for k, v in (trade.get('features') or {}).items():
                row[k] = v
            rows.append(row)

        level_path = root / 'combined_rules/level_context_v2' / f'{segment}.jsonl'
        if level_path.exists():
            rows = merge_level_context(rows, load_jsonl(level_path))
        rows = enrich_buckets(rows)

        with (out_dir / f'{segment}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + '\n')

        report['segments'][segment] = {
            'overall': group_summary(rows),
            'by_exit_reason': grouped(rows, 'exit_reason'),
            'by_side': grouped(rows, 'side'),
            'by_risk_bucket': grouped(rows, 'risk_bucket'),
            'by_trend_strength': grouped(rows, 'trend_strength_bucket'),
            'by_h1_open_space': grouped(rows, 'h1_open_space'),
            'by_h1_floating_zone': grouped(rows, 'h1_floating_zone_flag'),
        }

    report_path = out_dir / 'report.json'
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', report_path)


if __name__ == '__main__':
    main()
