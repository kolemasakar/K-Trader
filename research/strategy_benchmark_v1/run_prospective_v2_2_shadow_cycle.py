#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

from ktrader.history import collect_mtf_history_bundle, write_mtf_bundle
from ktrader.providers.registry import create_provider

DEFAULT_RESEARCH_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
DEFAULT_BASE = pathlib.Path('/data/research/phase11g')
DEFAULT_PROVIDER = 'binance_usdm'
DEFAULT_BOUNDARY = '2026-09-11T20:00:00Z'
HERE = pathlib.Path(__file__).resolve().parent
DEPTHS = {'1d': 20, '4h': 80, '1h': 300, '15m': 400, '5m': 20}
REQUIRED_BUNDLE_FILES = ('bundle.json', '15m.jsonl', '1h.jsonl')


def parse_utc(value: str) -> datetime:
    text = value.strip()
    dt = datetime.fromisoformat(text[:-1] + '+00:00' if text.endswith('Z') else text)
    if dt.tzinfo is None or dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError('--as-of must be timezone-aware UTC')
    return dt.astimezone(timezone.utc)


def z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


async def export_panel(*, provider_id: str, panel: list[str], as_of: datetime, bundle_root: pathlib.Path, max_pages: int) -> list[dict]:
    provider = create_provider(provider_id)
    try:
        instruments = await provider.list_instruments()
        by_symbol = {item.symbol: item for item in instruments}
        rows = []
        for symbol in panel:
            instrument = by_symbol.get(symbol)
            if instrument is None:
                raise RuntimeError(f'fixed-panel symbol unavailable on {provider_id}: {symbol}')
            bundle = await collect_mtf_history_bundle(
                provider,
                instrument,
                bars_by_interval=DEPTHS,
                as_of=as_of,
                max_pages_per_interval=max_pages,
            )
            symbol_root = bundle_root / symbol
            out_dir = write_mtf_bundle(symbol_root, bundle)
            missing = [name for name in REQUIRED_BUNDLE_FILES if not (symbol_root / name).exists()]
            if missing:
                raise RuntimeError(f'incomplete bundle for {symbol}: missing {missing}; writer_output={out_dir}')
            m = bundle.manifest
            rows.append({
                'symbol': symbol,
                'provider_id': m.provider_id,
                'as_of': z(m.as_of),
                'candle_counts': dict(m.candle_counts),
                'bundle_sha256': m.bundle_sha256,
                'output': str(symbol_root),
            })
            print('EXPORTED', symbol, m.bundle_sha256, flush=True)
        return rows
    finally:
        await provider.close()


def write_status(run_root: pathlib.Path, status: str, **extra) -> None:
    payload = {
        'schema_version': 'ktrader.candidate_v2_2.shadow_cycle_status.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'holdout_opened': False,
        'production_action': False,
        'status': status,
        **extra,
    }
    (run_root / 'cycle_status.json').write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')


def main() -> None:
    ap = argparse.ArgumentParser(description='Run one frozen v2.2 prospective shadow capture using canonical K-Trader provider history tooling')
    ap.add_argument('--as-of', required=True, type=parse_utc)
    ap.add_argument('--provider', default=DEFAULT_PROVIDER, choices=('binance_usdm', 'bybit_linear'))
    ap.add_argument('--research-root', default=str(DEFAULT_RESEARCH_ROOT))
    ap.add_argument('--base', default=str(DEFAULT_BASE))
    ap.add_argument('--boundary', default=DEFAULT_BOUNDARY)
    ap.add_argument('--max-pages', type=int, default=100)
    ap.add_argument('--attempt', default='1', help='immutable run-attempt token; use 2+ only after an infrastructure-invalid prior attempt at the same as-of')
    args = ap.parse_args()

    research_root = pathlib.Path(args.research_root)
    base = pathlib.Path(args.base)
    protocol_path = research_root / 'protocol.json'
    protocol = json.loads(protocol_path.read_text())
    panel = list(protocol['primary_panel']['symbols'])

    boundary = parse_utc(args.boundary)
    if args.as_of <= boundary:
        raise SystemExit('--as-of must be after frozen prospective boundary')

    run_token = args.as_of.strftime('%Y%m%dT%H%M%SZ')
    suffix = '' if str(args.attempt) == '1' else f'_r{args.attempt}'
    run_root = base / f'v2_2_shadow_{run_token}{suffix}'
    if run_root.exists():
        raise SystemExit(f'run root already exists; refusing overwrite: {run_root}')
    bundle_root = run_root / 'bundles'
    shadow_root = run_root / 'shadow_v1_1'
    bundle_root.mkdir(parents=True, exist_ok=False)
    write_status(run_root, 'EXPORTING', as_of=z(args.as_of), provider_id=args.provider, attempt=str(args.attempt))

    try:
        exports = asyncio.run(export_panel(
            provider_id=args.provider,
            panel=panel,
            as_of=args.as_of,
            bundle_root=bundle_root,
            max_pages=args.max_pages,
        ))
    except Exception as exc:
        write_status(run_root, 'INVALID_INFRASTRUCTURE', stage='EXPORT', error=repr(exc), as_of=z(args.as_of))
        raise

    export_summary = {
        'schema_version': 'ktrader.candidate_v2_2.shadow_export.v1_1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'holdout_opened': False,
        'production_action': False,
        'provider_id': args.provider,
        'as_of': z(args.as_of),
        'boundary': z(boundary),
        'panel_size': len(panel),
        'depths': DEPTHS,
        'protocol_path': str(protocol_path),
        'protocol_sha256': sha_file(protocol_path),
        'exports': exports,
    }
    export_path = run_root / 'bundle_export_summary.json'
    export_path.write_text(json.dumps(export_summary, indent=2, sort_keys=True) + '\n')

    capture = HERE / 'prospective_v2_2_shadow_capture.py'
    ledger = HERE / 'prospective_v2_2_shadow_ledger.py'
    for required in (capture, ledger):
        if not required.exists():
            write_status(run_root, 'INVALID_INFRASTRUCTURE', stage='COMPANION_CHECK', error=f'missing {required}')
            raise SystemExit(f'missing companion research script: {required}')

    subprocess.run([
        sys.executable, str(capture),
        '--bundle-root', str(bundle_root),
        '--output', str(shadow_root),
        '--research-root', str(research_root),
        '--boundary', z(boundary),
    ], check=True)

    shadow_summary = json.loads((shadow_root / 'summary.json').read_text())
    if shadow_summary.get('missing_symbols'):
        write_status(run_root, 'INVALID_INFRASTRUCTURE', stage='CAPTURE', missing_symbols=shadow_summary['missing_symbols'])
        raise SystemExit(f"capture missing fixed-panel symbols: {shadow_summary['missing_symbols']}")
    if len(shadow_summary.get('bundle_provenance') or {}) != len(panel):
        write_status(run_root, 'INVALID_INFRASTRUCTURE', stage='CAPTURE', error='bundle provenance count mismatch')
        raise SystemExit('bundle provenance count mismatch')

    write_status(run_root, 'VALID_SHADOW_CAPTURE', as_of=z(args.as_of), signal_bars_evaluated_count=shadow_summary.get('signal_bars_evaluated_count'), event_count=shadow_summary.get('event_count'))

    subprocess.run([
        sys.executable, str(ledger),
        '--base', str(base),
    ], check=True)

    final = {
        'schema_version': 'ktrader.candidate_v2_2.shadow_cycle.v1_1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'holdout_opened': False,
        'production_action': False,
        'cycle_status': 'VALID_SHADOW_CAPTURE',
        'run_root': str(run_root),
        'as_of': z(args.as_of),
        'provider_id': args.provider,
        'panel_size': len(panel),
        'bundle_export_summary_sha256': sha_file(export_path),
        'shadow_summary_sha256': sha_file(shadow_root / 'summary.json'),
        'event_file_sha256': sha_file(shadow_root / 'shadow_events.jsonl'),
        'signal_bars_evaluated_count': shadow_summary.get('signal_bars_evaluated_count'),
        'event_count': shadow_summary.get('event_count'),
        'eligible_setup_count': shadow_summary.get('eligible_setup_count'),
        'unique_eligible_family_count': shadow_summary.get('unique_eligible_family_count'),
        'frozen_harness_sha256': shadow_summary.get('frozen_harness_sha256'),
        'protocol_sha256': shadow_summary.get('protocol_sha256'),
    }
    final_path = run_root / 'cycle_summary.json'
    final_path.write_text(json.dumps(final, indent=2, sort_keys=True) + '\n')
    print(json.dumps(final, indent=2, sort_keys=True))
    print('CYCLE_SUMMARY', final_path)


if __name__ == '__main__':
    main()
