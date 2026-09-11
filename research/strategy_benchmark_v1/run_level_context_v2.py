#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
from datetime import timedelta

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
MODULE_PATH = pathlib.Path(__file__).with_name('level_context_v2_features.py')

spec = importlib.util.spec_from_file_location('level_context_v2_features', MODULE_PATH)
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)


def aggregate_h1_to_h4(h1):
    """Create only complete UTC-aligned 4h candles from closed H1 bars."""
    groups = {}
    for b in h1:
        dt = b['open_dt']
        bucket_hour = (dt.hour // 4) * 4
        bucket = dt.replace(hour=bucket_hour, minute=0, second=0, microsecond=0)
        groups.setdefault(bucket, []).append(b)

    out = []
    for bucket in sorted(groups):
        bars = sorted(groups[bucket], key=lambda x: x['open_dt'])
        expected = [bucket + timedelta(hours=i) for i in range(4)]
        if len(bars) != 4 or [b['open_dt'] for b in bars] != expected:
            continue
        out.append({
            'open_time': bars[0]['open_time'],
            'close_time': bars[-1]['close_time'],
            'open_dt': bars[0]['open_dt'],
            'close_dt': bars[-1]['close_dt'],
            'open': bars[0]['open'],
            'high': max(b['high'] for b in bars),
            'low': min(b['low'] for b in bars),
            'close': bars[-1]['close'],
            'quote_volume': sum(b.get('quote_volume', 0.0) for b in bars),
        })
    return out


def load_trades(path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = pathlib.Path(args.root)
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    out_dir = root / 'combined_rules/level_context_v2'
    out_dir.mkdir(parents=True, exist_ok=True)

    histories = {}
    summary = {
        'schema_version': 'ktrader.level_context_v2.summary.v1',
        'h4_source': 'causal_utc_aggregation_from_merged_h1_when_4h_missing',
        'segments': {},
    }

    for segment in ('development', 'validation', 'non_holdout'):
        trades = load_trades(root / 'combined_rules/v2_2_trades' / f'{segment}.jsonl')
        rows = []
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in histories:
                h1 = lc.load_bars(pathlib.Path(manifest['merged_histories'][symbol]['1h']['path']))
                if '4h' in manifest['merged_histories'][symbol]:
                    h4 = lc.load_bars(pathlib.Path(manifest['merged_histories'][symbol]['4h']['path']))
                else:
                    h4 = aggregate_h1_to_h4(h1)
                histories[symbol] = {'h1': h1, 'h4': h4}
            rows.append(lc.extract_trade_context(trade, histories[symbol]['h1'], histories[symbol]['h4']))

        with (out_dir / f'{segment}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + '\n')
        summary['segments'][segment] = lc.summarize(rows)

    report = out_dir / 'summary.json'
    report.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=2, sort_keys=True))
    print('REPORT', report)


if __name__ == '__main__':
    main()
