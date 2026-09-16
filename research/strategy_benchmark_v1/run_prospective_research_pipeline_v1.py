#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

BASE_DEFAULT = pathlib.Path('/data/research/phase11g')

CAPTURE_RUNTIME_DEPENDENCIES = (
    'prospective_v2_2_shadow_capture.py',
    'prospective_v2_2_shadow_ledger.py',
    'level_context_v2_features.py',
    'level_context_v2_1_diagnostics.py',
    'level_context_v2_2_traversal.py',
)


def utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def stamp(value: dt.datetime) -> str:
    return value.strftime('%Y%m%dT%H%M%SZ')


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_stage(name: str, command: list[str], execute: bool, records: list[dict]) -> None:
    record = {'stage': name, 'command': command, 'status': 'PLANNED'}
    records.append(record)
    if not execute:
        return
    completed = subprocess.run(command, text=True, capture_output=True)
    record.update(
        {
            'returncode': completed.returncode,
            'stdout_tail': completed.stdout[-4000:],
            'stderr_tail': completed.stderr[-4000:],
        }
    )
    if completed.returncode != 0:
        record['status'] = 'FAILED'
        raise RuntimeError(f'STAGE_FAILED {name} rc={completed.returncode}')
    record['status'] = 'PASS'


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fail-closed frozen-v2.2 prospective research pipeline. Plan-only by default.'
    )
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--prior-outcomes', required=True)
    parser.add_argument('--script-dir', default=str(pathlib.Path(__file__).resolve().parent))
    parser.add_argument('--base', default=str(BASE_DEFAULT))
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--manifest-dir')
    args = parser.parse_args()

    as_of = utc(args.as_of)
    run_stamp = stamp(as_of)
    base = pathlib.Path(args.base)
    script_dir = pathlib.Path(args.script_dir)
    python = sys.executable

    run_root = base / f'v2_2_shadow_{run_stamp}'
    funding_root = run_root / 'funding_offline_v1'
    outcomes_parent = (
        base
        / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3'
    )
    outcomes_root = outcomes_parent / run_stamp
    diagnostics_root = (
        base
        / 'strategy_benchmark_v1/combined_rules/prospective_post30_diagnostics'
        / run_stamp
    )
    ledger = (
        base
        / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl'
    )
    manifest_dir = (
        pathlib.Path(args.manifest_dir)
        if args.manifest_dir
        else base / 'strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests'
    )

    scripts = {
        'capture': script_dir / 'run_prospective_v2_2_shadow_cycle.py',
        'funding': script_dir / 'export_prospective_funding_snapshot_v1.py',
        'resolver': script_dir / 'prospective_v2_2_outcome_resolver_offline_v1_3.py',
        'diagnostics': script_dir / 'prospective_v2_2_post30_diagnostics.py',
        'statistics': script_dir / 'prospective_post30_statistical_diagnostics.py',
    }
    runtime_dependencies = [script_dir / name for name in CAPTURE_RUNTIME_DEPENDENCIES]
    required_runtime_files = list(scripts.values()) + runtime_dependencies
    missing = [str(path) for path in required_runtime_files if not path.exists()]
    if missing:
        raise SystemExit('MISSING_PIPELINE_RUNTIME_FILES ' + json.dumps(missing))

    prior = pathlib.Path(args.prior_outcomes)
    if not (prior / 'observations.jsonl').exists():
        raise SystemExit(f'PRIOR_OUTCOMES_MISSING {prior}')
    if args.execute and run_root.exists():
        raise SystemExit(f'RUN_ROOT_EXISTS {run_root}')
    if args.execute and outcomes_root.exists():
        raise SystemExit(f'OUTCOMES_ROOT_EXISTS {outcomes_root}')

    commands = [
        ('capture', [python, str(scripts['capture']), '--as-of', args.as_of]),
        (
            'funding',
            [
                python,
                str(scripts['funding']),
                '--snapshot-root',
                str(run_root),
                '--as-of',
                args.as_of,
            ],
        ),
        (
            'resolver',
            [
                python,
                str(scripts['resolver']),
                '--as-of',
                args.as_of,
                '--prior-outcomes',
                str(prior),
                '--funding-snapshot-root',
                str(funding_root),
                '--output-root',
                str(outcomes_parent),
            ],
        ),
        (
            'post30',
            [
                python,
                str(scripts['diagnostics']),
                '--as-of',
                args.as_of,
                '--ledger',
                str(ledger),
                '--outcomes',
                str(outcomes_root),
                '--bundle-root',
                str(run_root / 'bundles'),
                '--output',
                str(diagnostics_root / 'descriptive'),
            ],
        ),
        (
            'statistics',
            [
                python,
                str(scripts['statistics']),
                '--report',
                str(diagnostics_root / 'descriptive/report.json'),
                '--output',
                str(diagnostics_root / 'statistical.json'),
            ],
        ),
    ]

    records: list[dict] = []
    status = 'PLAN_ONLY'
    error = None
    try:
        for name, command in commands:
            run_stage(name, command, args.execute, records)
        if args.execute:
            status = 'PASS'
    except Exception as exc:
        status = 'FAILED'
        error = str(exc)

    report = {
        'schema_version': 'ktrader.prospective_research_pipeline_manifest.v1',
        'as_of': args.as_of,
        'mode': 'EXECUTE' if args.execute else 'PLAN_ONLY',
        'status': status,
        'resolver_version': 'v1.3',
        'holdout_opened': False,
        'production_action': False,
        'run_root': str(run_root),
        'outcomes_root': str(outcomes_root),
        'prior_outcomes': str(prior),
        'runtime_preflight_file_count': len(required_runtime_files),
        'stages': records,
    }
    if error is not None:
        report['error'] = error

    manifest_dir.mkdir(parents=True, exist_ok=True)
    suffix = 'execute' if args.execute else 'plan'
    manifest_path = manifest_dir / f'pipeline_{run_stamp}_{suffix}.json'
    if manifest_path.exists():
        raise SystemExit(f'MANIFEST_EXISTS {manifest_path}')
    manifest_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')

    print(json.dumps(report, indent=2, sort_keys=True))
    print('MANIFEST', manifest_path, sha(manifest_path))
    if status == 'FAILED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
