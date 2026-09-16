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
    record.update({
        'returncode': completed.returncode,
        'stdout_tail': completed.stdout[-4000:],
        'stderr_tail': completed.stderr[-4000:],
    })
    if completed.returncode != 0:
        record['status'] = 'FAILED'
        raise RuntimeError(f'STAGE_FAILED {name} rc={completed.returncode}')
    record['status'] = 'PASS'


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fail-closed frozen-v2.2 prospective pipeline with evidence/risk/state manifests. Plan-only by default.'
    )
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--prior-outcomes', required=True)
    parser.add_argument('--script-dir', default=str(pathlib.Path(__file__).resolve().parent))
    parser.add_argument('--base', default=str(BASE_DEFAULT))
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--manifest-dir')
    parser.add_argument('--prereg-boundary', default='2026-09-16T13:00:00Z')
    args = parser.parse_args()

    as_of = utc(args.as_of)
    run_stamp = stamp(as_of)
    base = pathlib.Path(args.base)
    script_dir = pathlib.Path(args.script_dir)
    python = sys.executable

    run_root = base / f'v2_2_shadow_{run_stamp}'
    funding_root = run_root / 'funding_offline_v1'
    outcomes_parent = base / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3'
    outcomes_root = outcomes_parent / run_stamp
    diagnostics_root = base / 'strategy_benchmark_v1/combined_rules/prospective_post30_diagnostics' / run_stamp
    evidence_root = base / 'strategy_benchmark_v1/combined_rules/prospective_evidence_tracker' / run_stamp
    risk_root = base / 'strategy_benchmark_v1/combined_rules/prospective_portfolio_risk' / run_stamp
    state_path = base / 'strategy_benchmark_v1/combined_rules/current_state_manifests' / f'{run_stamp}.json'
    ledger_root = base / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
    ledger = ledger_root / 'deduplicated_events.jsonl'
    ledger_summary = ledger_root / 'ledger_summary.json'
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
        'evidence': script_dir / 'prospective_evidence_tracker.py',
        'risk': script_dir / 'prospective_portfolio_risk_layer.py',
        'state': script_dir / 'generate_current_research_state.py',
    }
    runtime_dependencies = [script_dir / name for name in CAPTURE_RUNTIME_DEPENDENCIES]
    required_runtime_files = list(scripts.values()) + runtime_dependencies
    missing = [str(path) for path in required_runtime_files if not path.exists()]
    if missing:
        raise SystemExit('MISSING_PIPELINE_RUNTIME_FILES ' + json.dumps(missing))

    prior = pathlib.Path(args.prior_outcomes)
    if not (prior / 'observations.jsonl').exists():
        raise SystemExit(f'PRIOR_OUTCOMES_MISSING {prior}')
    if args.execute:
        collisions = [path for path in (run_root, outcomes_root, evidence_root, risk_root, state_path) if path.exists()]
        if collisions:
            raise SystemExit('PIPELINE_OUTPUT_EXISTS ' + json.dumps([str(path) for path in collisions]))

    commands = [
        ('capture', [python, str(scripts['capture']), '--as-of', args.as_of]),
        ('funding', [
            python, str(scripts['funding']), '--snapshot-root', str(run_root), '--as-of', args.as_of,
        ]),
        ('resolver', [
            python, str(scripts['resolver']), '--as-of', args.as_of,
            '--prior-outcomes', str(prior), '--funding-snapshot-root', str(funding_root),
            '--output-root', str(outcomes_parent),
        ]),
        ('post30', [
            python, str(scripts['diagnostics']), '--as-of', args.as_of,
            '--ledger', str(ledger), '--outcomes', str(outcomes_root),
            '--bundle-root', str(run_root / 'bundles'), '--output', str(diagnostics_root / 'descriptive'),
        ]),
        ('statistics', [
            python, str(scripts['statistics']), '--report', str(diagnostics_root / 'descriptive/report.json'),
            '--output', str(diagnostics_root / 'statistical.json'),
        ]),
        ('evidence', [
            python, str(scripts['evidence']), '--as-of', args.as_of, '--outcomes', str(outcomes_root),
            '--ledger', str(ledger), '--prereg-boundary', args.prereg_boundary,
            '--output-root', str(evidence_root.parent),
        ]),
        ('portfolio_risk', [
            python, str(scripts['risk']), '--as-of', args.as_of, '--outcomes', str(outcomes_root),
            '--diagnostic-report', str(diagnostics_root / 'descriptive/report.json'),
            '--output-root', str(risk_root.parent),
        ]),
        ('state_manifest', [
            python, str(scripts['state']), '--as-of', args.as_of,
            '--cycle-summary', str(run_root / 'cycle_summary.json'),
            '--ledger-summary', str(ledger_summary),
            '--outcomes-summary', str(outcomes_root / 'summary.json'),
            '--evidence-report', str(evidence_root / 'report.json'),
            '--risk-report', str(risk_root / 'report.json'),
            '--output', str(state_path),
        ]),
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
        'schema_version': 'ktrader.prospective_research_pipeline_manifest.v2',
        'as_of': args.as_of,
        'mode': 'EXECUTE' if args.execute else 'PLAN_ONLY',
        'status': status,
        'resolver_version': 'v1.3',
        'prereg_boundary': args.prereg_boundary,
        'holdout_opened': False,
        'production_action': False,
        'run_root': str(run_root),
        'outcomes_root': str(outcomes_root),
        'evidence_root': str(evidence_root),
        'risk_root': str(risk_root),
        'state_path': str(state_path),
        'prior_outcomes': str(prior),
        'runtime_preflight_file_count': len(required_runtime_files),
        'stages': records,
    }
    if error is not None:
        report['error'] = error

    manifest_dir.mkdir(parents=True, exist_ok=True)
    suffix = 'execute' if args.execute else 'plan'
    manifest_path = manifest_dir / f'pipeline_v2_{run_stamp}_{suffix}.json'
    if manifest_path.exists():
        raise SystemExit(f'MANIFEST_EXISTS {manifest_path}')
    manifest_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')

    print(json.dumps(report, indent=2, sort_keys=True))
    print('MANIFEST', manifest_path, sha(manifest_path))
    if status == 'FAILED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
