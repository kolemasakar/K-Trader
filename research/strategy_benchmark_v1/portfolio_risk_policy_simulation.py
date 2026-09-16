#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import Counter, defaultdict
from datetime import datetime, timezone

DEFAULT_BASE = pathlib.Path('/data/research/phase11g')
DEFAULT_OUTROOT = DEFAULT_BASE / 'strategy_benchmark_v1/combined_rules/portfolio_risk_policy_simulation'

POLICIES = (
    {
        'policy_id': 'P025_3_CONSERVATIVE',
        'risk_per_family_pct': 0.25,
        'max_open_positions': 3,
        'max_portfolio_open_risk_pct': 0.75,
        'max_same_side_open_risk_pct': 0.75,
        'max_correlated_cluster_open_risk_pct': 0.50,
    },
    {
        'policy_id': 'P050_3_BALANCED',
        'risk_per_family_pct': 0.50,
        'max_open_positions': 3,
        'max_portfolio_open_risk_pct': 1.50,
        'max_same_side_open_risk_pct': 1.50,
        'max_correlated_cluster_open_risk_pct': 1.00,
    },
    {
        'policy_id': 'P050_4_BALANCED',
        'risk_per_family_pct': 0.50,
        'max_open_positions': 4,
        'max_portfolio_open_risk_pct': 2.00,
        'max_same_side_open_risk_pct': 2.00,
        'max_correlated_cluster_open_risk_pct': 1.00,
    },
    {
        'policy_id': 'P050_5_WIDE',
        'risk_per_family_pct': 0.50,
        'max_open_positions': 5,
        'max_portfolio_open_risk_pct': 2.50,
        'max_same_side_open_risk_pct': 2.50,
        'max_correlated_cluster_open_risk_pct': 1.50,
    },
)


def utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: pathlib.Path) -> list[dict]:
    with path.open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def symbol_clusters(diagnostic: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    clusters = diagnostic.get('portfolio', {}).get('symbol_correlation_clusters') or []
    for i, cluster in enumerate(clusters, 1):
        cluster_id = f'C{i:02d}'
        for symbol in cluster:
            if symbol in out:
                raise ValueError(f'duplicate cluster membership: {symbol}')
            out[symbol] = cluster_id
    return out


def primary_rows(observations: list[dict]) -> list[dict]:
    rows = [r for r in observations if r.get('family_role') == 'PRIMARY_REPRESENTATIVE']
    rows.sort(key=lambda r: (utc(r['entry_time']), r['symbol'], r['setup_family_id']))
    seen = set()
    for row in rows:
        family = row['setup_family_id']
        if family in seen:
            raise ValueError(f'duplicate primary family: {family}')
        seen.add(family)
    return rows


def simulate(rows: list[dict], clusters: dict[str, str], policy: dict, as_of: datetime) -> dict:
    risk = float(policy['risk_per_family_pct'])
    active: list[dict] = []
    accepted: list[dict] = []
    blocked: list[dict] = []
    peak_positions = 0
    peak_portfolio_risk = 0.0
    peak_same_side_risk = 0.0
    peak_cluster_risk = 0.0

    for row in rows:
        entry = utc(row['entry_time'])
        active = [a for a in active if a['release_time'] > entry]
        side = row['side']
        cluster_id = clusters.get(row['symbol'], f'SOLO:{row["symbol"]}')

        side_n = sum(a['side'] == side for a in active) + 1
        cluster_n = sum(a['cluster_id'] == cluster_id for a in active) + 1
        total_n = len(active) + 1

        reasons = []
        if total_n > int(policy['max_open_positions']):
            reasons.append('MAX_OPEN_POSITIONS')
        if total_n * risk > float(policy['max_portfolio_open_risk_pct']) + 1e-12:
            reasons.append('MAX_PORTFOLIO_OPEN_RISK')
        if side_n * risk > float(policy['max_same_side_open_risk_pct']) + 1e-12:
            reasons.append('MAX_SAME_SIDE_OPEN_RISK')
        if cluster_n * risk > float(policy['max_correlated_cluster_open_risk_pct']) + 1e-12:
            reasons.append('MAX_CORRELATED_CLUSTER_OPEN_RISK')

        if reasons:
            blocked.append({
                'setup_family_id': row['setup_family_id'],
                'symbol': row['symbol'],
                'side': side,
                'entry_time': row['entry_time'],
                'reasons': reasons,
            })
            continue

        release_time = utc(row['exit_time']) if row.get('resolved') and row.get('exit_time') else as_of
        item = {
            'setup_family_id': row['setup_family_id'],
            'symbol': row['symbol'],
            'side': side,
            'entry_time': row['entry_time'],
            'release_time': release_time,
            'cluster_id': cluster_id,
            'resolved': bool(row.get('resolved')),
            'realized_R': row.get('realized_R'),
        }
        active.append(item)
        accepted.append(item)

        side_counts = Counter(a['side'] for a in active)
        cluster_counts = Counter(a['cluster_id'] for a in active)
        peak_positions = max(peak_positions, len(active))
        peak_portfolio_risk = max(peak_portfolio_risk, len(active) * risk)
        peak_same_side_risk = max(peak_same_side_risk, max(side_counts.values(), default=0) * risk)
        peak_cluster_risk = max(peak_cluster_risk, max(cluster_counts.values(), default=0) * risk)

    resolved = [x for x in accepted if x['resolved'] and x.get('realized_R') is not None]
    rs = [float(x['realized_R']) for x in resolved]
    reason_counts = Counter(reason for row in blocked for reason in row['reasons'])
    return {
        'policy': policy,
        'family_count_considered': len(rows),
        'accepted_family_count': len(accepted),
        'blocked_family_count': len(blocked),
        'resolved_accepted_count': len(resolved),
        'resolved_accepted_expectancy_R': sum(rs) / len(rs) if rs else None,
        'resolved_accepted_wins': sum(x > 0 for x in rs),
        'peak_open_positions': peak_positions,
        'peak_portfolio_open_risk_pct': peak_portfolio_risk,
        'peak_same_side_open_risk_pct': peak_same_side_risk,
        'peak_correlated_cluster_open_risk_pct': peak_cluster_risk,
        'block_reason_counts': dict(sorted(reason_counts.items())),
        'blocked_families': blocked,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description='Diagnostic-only portfolio risk policy simulation.')
    ap.add_argument('--as-of', required=True)
    ap.add_argument('--outcomes', required=True)
    ap.add_argument('--diagnostic-report', required=True)
    ap.add_argument('--output-root', default=str(DEFAULT_OUTROOT))
    args = ap.parse_args()

    as_of = utc(args.as_of)
    outcomes = pathlib.Path(args.outcomes)
    diagnostic_path = pathlib.Path(args.diagnostic_report)
    summary = json.loads((outcomes / 'summary.json').read_text())
    diagnostic = json.loads(diagnostic_path.read_text())
    if summary.get('holdout_opened') is not False or summary.get('production_action') is not False:
        raise SystemExit('OUTCOME_GOVERNANCE_INVARIANT_FAILED')
    if diagnostic.get('holdout_opened') is not False or diagnostic.get('production_action') is not False:
        raise SystemExit('DIAGNOSTIC_GOVERNANCE_INVARIANT_FAILED')

    rows = primary_rows(load_jsonl(outcomes / 'observations.jsonl'))
    clusters = symbol_clusters(diagnostic)
    simulations = [simulate(rows, clusters, policy, as_of) for policy in POLICIES]

    report = {
        'schema_version': 'ktrader.portfolio_risk_policy_simulation.v1',
        'as_of': args.as_of,
        'diagnostic_only': True,
        'production_enforcement': False,
        'holdout_opened': False,
        'production_action': False,
        'selection_prohibited': True,
        'interpretation_guard': (
            'These scenarios quantify concentration effects on the already-observed sample. '
            'Do not choose a production policy by maximizing backtested expectancy here.'
        ),
        'simulations': simulations,
        'status': 'PASS',
    }

    stamp = as_of.strftime('%Y%m%dT%H%M%SZ')
    out = pathlib.Path(args.output_root) / stamp
    out.mkdir(parents=True, exist_ok=False)
    path = out / 'report.json'
    path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    print('REPORT', path, sha(path))


if __name__ == '__main__':
    main()
