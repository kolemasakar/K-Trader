#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import defaultdict
from datetime import datetime, timezone, timedelta

DATASET = pathlib.Path('/data/research/phase11g/profile_research_dataset_v0_20260911T204500Z_adaptive')


def utc(s: str) -> datetime:
    d = datetime.fromisoformat(s[:-1] + '+00:00' if s.endswith('Z') else s)
    return d.astimezone(timezone.utc)


def z(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_d1(path: pathlib.Path) -> tuple[dict, list[dict]]:
    with path.open() as f:
        manifest = json.loads(next(f))
        rows = [json.loads(line) for line in f if line.strip()]
    if manifest.get('record_type') != 'manifest':
        raise RuntimeError(f'missing manifest: {path}')
    return manifest, rows


def monday(dt: datetime) -> datetime:
    x = dt.astimezone(timezone.utc)
    return datetime(x.year, x.month, x.day, tzinfo=timezone.utc) - timedelta(days=x.weekday())


def build_symbol(symbol: str, src: pathlib.Path, dst: pathlib.Path, as_of: datetime) -> dict:
    manifest, rows = load_d1(src)
    groups: dict[datetime, list[dict]] = defaultdict(list)
    for row in rows:
        ot = utc(row['open_time'])
        ct = utc(row['close_time'])
        if not row.get('closed', False) or ct > as_of:
            continue
        groups[monday(ot)].append(row)

    weekly = []
    excluded_partial = 0
    for week_open in sorted(groups):
        week_rows = sorted(groups[week_open], key=lambda r: utc(r['open_time']))
        expected = [week_open + timedelta(days=i) for i in range(7)]
        opens = [utc(r['open_time']) for r in week_rows]
        week_close = week_open + timedelta(days=7) - timedelta(milliseconds=1)
        complete = len(week_rows) == 7 and opens == expected and week_close <= as_of
        if not complete:
            excluded_partial += 1
            continue
        weekly.append({
            'record_type': 'candle',
            'provider_id': manifest['provider_id'],
            'symbol': symbol,
            'interval': '1w',
            'open_time': z(week_open),
            'close_time': z(week_close),
            'open': week_rows[0]['open'],
            'high': str(max(float(r['high']) for r in week_rows)),
            'low': str(min(float(r['low']) for r in week_rows)),
            'close': week_rows[-1]['close'],
            'volume': str(sum(float(r.get('volume') or 0) for r in week_rows)),
            'quote_volume': str(sum(float(r.get('quote_volume') or 0) for r in week_rows)),
            'trade_count': sum(int(r.get('trade_count') or 0) for r in week_rows),
            'closed': True,
            'source_interval': '1d',
            'source_bar_count': 7,
        })

    dst.parent.mkdir(parents=True, exist_ok=True)
    payload_lines = [json.dumps(r, sort_keys=True) for r in weekly]
    payload = ('\n'.join(payload_lines) + ('\n' if payload_lines else '')).encode()
    derived_manifest = {
        'record_type': 'manifest',
        'schema_version': 'ktrader.position_w1_derived.v0',
        'research_only': True,
        'provider_id': manifest['provider_id'],
        'symbol': symbol,
        'interval': '1w',
        'as_of': z(as_of),
        'source_path': str(src),
        'source_d1_sha256': sha_file(src),
        'source_d1_bar_count': len(rows),
        'derived_w1_count': len(weekly),
        'actual_start': weekly[0]['open_time'] if weekly else None,
        'actual_end': weekly[-1]['close_time'] if weekly else None,
        'excluded_partial_week_count': excluded_partial,
        'payload_sha256': sha_bytes(payload),
    }
    with dst.open('w') as f:
        f.write(json.dumps(derived_manifest, sort_keys=True) + '\n')
        for line in payload_lines:
            f.write(line + '\n')
    return {**derived_manifest, 'output_path': str(dst), 'file_sha256': sha_file(dst)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default=str(DATASET))
    args = ap.parse_args()
    root = pathlib.Path(args.dataset)
    ds_summary = json.loads((root / 'dataset_summary.json').read_text())
    as_of = utc(ds_summary['as_of'])
    bundle_root = root / 'bundles'
    out_root = root / 'derived' / '1w'
    rows = []
    for symbol_dir in sorted(p for p in bundle_root.iterdir() if p.is_dir()):
        symbol = symbol_dir.name
        rows.append(build_symbol(symbol, symbol_dir / '1d.jsonl', out_root / f'{symbol}.jsonl', as_of))
    counts = [r['derived_w1_count'] for r in rows]
    report = {
        'schema_version': 'ktrader.position_w1_dataset.v0',
        'research_only': True,
        'dataset_root': str(root),
        'as_of': z(as_of),
        'symbol_count': len(rows),
        'all_symbols_nonempty': all(c > 0 for c in counts),
        'min_w1_bars': min(counts) if counts else 0,
        'max_w1_bars': max(counts) if counts else 0,
        'rows': rows,
    }
    report_path = root / 'position_w1_summary.json'
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ('schema_version','symbol_count','all_symbols_nonempty','min_w1_bars','max_w1_bars')}, indent=2))
    print('REPORT', report_path, sha_file(report_path))


if __name__ == '__main__':
    main()
