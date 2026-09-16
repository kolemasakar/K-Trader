#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import pathlib
import statistics
from collections import defaultdict

BASE = pathlib.Path('/data/research/phase11g')
LEDGER = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
OUTROOT = BASE / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1'
HERE = pathlib.Path(__file__).resolve().parent

# Stable identity is authoritative. These price tolerances are intentionally
# narrow and only absorb already-observed sub-nanounit stop representation
# drift in accepted VTHOUSDT observations. Anything larger fails closed.
PRIOR_PRICE_ABS_TOL = 2e-9
PRIOR_PRICE_REL_TOL = 1e-12


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load module: {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_identity(row: dict) -> tuple:
    return (
        row['setup_family_id'],
        row['symbol'],
        row['side'],
        row['entry_time'],
    )


def price_close(a, b) -> bool:
    return math.isclose(
        float(a),
        float(b),
        rel_tol=PRIOR_PRICE_REL_TOL,
        abs_tol=PRIOR_PRICE_ABS_TOL,
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            'Resolve frozen-v2.2 prospective outcomes offline while preserving '
            'accepted terminal outcomes whose source entry bars have aged out of '
            'the latest 400-M15 capture window.'
        )
    )
    ap.add_argument('--as-of', required=True)
    ap.add_argument(
        '--prior-outcomes',
        required=True,
        help='Accepted prior outcome directory containing observations.jsonl',
    )
    ap.add_argument(
        '--funding-snapshot-root',
        required=True,
        help='Persisted funding_offline_v1 directory produced from official Binance USD-M data',
    )
    ap.add_argument('--output-root', default=str(OUTROOT))
    args = ap.parse_args()

    offline = load_module(
        'prospective_v2_2_offline_v1_base',
        HERE / 'prospective_v2_2_outcome_resolver_offline_v1.py',
    )
    economics = load_module(
        'prospective_v2_2_online_v1_economics',
        HERE / 'prospective_v2_2_outcome_resolver_v1.py',
    )

    as_of = offline.utc(args.as_of)
    prior_root = pathlib.Path(args.prior_outcomes)
    funding_root = pathlib.Path(args.funding_snapshot_root)
    output_root = pathlib.Path(args.output_root)
    funding_summary = funding_root / 'summary.json'

    if not (prior_root / 'observations.jsonl').exists():
        raise SystemExit(f'PRIOR_OUTCOMES_MISSING {prior_root}')
    if not funding_summary.exists():
        raise SystemExit(f'FUNDING_SUMMARY_MISSING {funding_summary}')

    events = [
        row
        for row in offline.load_jsonl(LEDGER / 'deduplicated_events.jsonl')
        if row.get('status') == 'ELIGIBLE_SHADOW_SETUP'
    ]
    if any(offline.utc(row['entry_time']) >= as_of for row in events):
        raise SystemExit('LEDGER_CONTAINS_FUTURE_OR_EQUAL_ENTRY_FOR_ASOF')

    groups = defaultdict(list)
    for row in events:
        groups[row['setup_family_id']].append(row)
    for rows in groups.values():
        rows.sort(
            key=lambda row: (
                row.get('entry_time') or '',
                row.get('signal_bar_open_time') or '',
                row.get('symbol') or '',
                row.get('side') or '',
            )
        )

    prior_rows = [
        row
        for row in offline.load_jsonl(prior_root / 'observations.jsonl')
        if row.get('resolved')
    ]
    prior_map = {}
    for row in prior_rows:
        key = stable_identity(row)
        if key in prior_map:
            raise SystemExit(f'DUPLICATE_PRIOR_STABLE_ID {key!r}')
        prior_map[key] = row

    bundle_root, snapshot = offline.latest_snapshot(as_of)
    bars_cache = {}
    funding_cache = {}
    observations = []

    prior_reuse = 0
    prior_revalidated = 0
    prior_source_window_expired = 0
    new_resolved = 0
    new_unresolved = 0
    max_entry_abs_delta = 0.0
    max_stop_abs_delta = 0.0

    for family_id in sorted(groups):
        for index, event in enumerate(groups[family_id]):
            symbol = event['symbol']
            role = 'PRIMARY_REPRESENTATIVE' if index == 0 else 'CORRELATED_DIAGNOSTIC_ONLY'
            if symbol not in bars_cache:
                bars_cache[symbol] = offline.load_bars(bundle_root / symbol / '15m.jsonl')

            prior = prior_map.get(stable_identity(event))
            if prior is not None:
                entry_delta = abs(float(event['entry_price']) - float(prior['entry_price']))
                stop_delta = abs(float(event['stop_price']) - float(prior['stop_price']))
                max_entry_abs_delta = max(max_entry_abs_delta, entry_delta)
                max_stop_abs_delta = max(max_stop_abs_delta, stop_delta)

                if not (
                    price_close(event['entry_price'], prior['entry_price'])
                    and price_close(event['stop_price'], prior['stop_price'])
                ):
                    raise SystemExit(
                        'PRIOR_IDENTITY_PRICE_MISMATCH '
                        + json.dumps(
                            {
                                'family': family_id,
                                'symbol': symbol,
                                'entry_time': event['entry_time'],
                                'entry_abs_delta': entry_delta,
                                'stop_abs_delta': stop_delta,
                            },
                            sort_keys=True,
                        )
                    )

                path = offline.terminal_path(event, bars_cache[symbol], as_of)
                if path.get('status') == 'SOURCE_ENTRY_BAR_UNAVAILABLE':
                    # A previously accepted terminal outcome is immutable. Once
                    # its source bar ages out of the rolling capture, preserve it
                    # rather than misclassifying it as unresolved.
                    prior_source_window_expired += 1
                else:
                    if not path.get('resolved'):
                        raise SystemExit(
                            'PRIOR_TERMINAL_BECAME_UNRESOLVED '
                            + json.dumps({'family': family_id, 'entry_time': event['entry_time']})
                        )
                    new_exit = offline.z(path['exit_time_dt'])
                    if (
                        prior.get('terminal_state') != path.get('terminal_state')
                        or prior.get('exit_time') != new_exit
                    ):
                        raise SystemExit(
                            'PRIOR_TERMINAL_PATH_MISMATCH '
                            + json.dumps(
                                {
                                    'family': family_id,
                                    'entry_time': event['entry_time'],
                                    'prior_terminal': prior.get('terminal_state'),
                                    'current_terminal': path.get('terminal_state'),
                                    'prior_exit': prior.get('exit_time'),
                                    'current_exit': new_exit,
                                },
                                sort_keys=True,
                            )
                        )
                    prior_revalidated += 1

                row = dict(prior)
                row['as_of'] = offline.z(as_of)
                row['resolution_source'] = 'PRIOR_ACCEPTED_IMMUTABLE_TERMINAL'
                row['prior_resolution_as_of'] = prior.get('as_of')
                row['identity_price_tolerance_abs'] = PRIOR_PRICE_ABS_TOL
                row['identity_price_tolerance_rel'] = PRIOR_PRICE_REL_TOL
                prior_reuse += 1
            else:
                path = offline.terminal_path(event, bars_cache[symbol], as_of)
                if path.get('status') == 'SOURCE_ENTRY_BAR_UNAVAILABLE':
                    raise SystemExit(
                        'NEW_OBSERVATION_SOURCE_ENTRY_BAR_UNAVAILABLE '
                        + json.dumps(
                            {
                                'family': family_id,
                                'symbol': symbol,
                                'entry_time': event['entry_time'],
                            },
                            sort_keys=True,
                        )
                    )

                row = {
                    'schema_version': 'ktrader.candidate_v2_2.prospective_outcome.v1',
                    'strategy_id': 'candidate_rule_set_v2_2',
                    'symbol': symbol,
                    'side': event['side'],
                    'setup_family_id': family_id,
                    'signal_bar_open_time': event['signal_bar_open_time'],
                    'entry_time': event['entry_time'],
                    'entry_price': float(event['entry_price']),
                    'stop_price': float(event['stop_price']),
                    'target_price_3R': path['target'],
                    'initial_risk_pct': path['risk'] / path['entry'],
                    'bars_observed': path['bars_observed'],
                    'mfe_R': path['mfe_R'],
                    'mae_R': path['mae_R'],
                    'time_to_R': path['time_to_R'],
                    'terminal_state': path['terminal_state'],
                    'resolved': path['resolved'],
                    'as_of': offline.z(as_of),
                    'holdout_opened': False,
                    'production_action': False,
                    'clean_break_no_revisit': event.get('clean_break_no_revisit'),
                    'level_v2_h1_open_space': event.get('level_v2_h1_open_space'),
                    'level_v2_h1_next_level_R': event.get('level_v2_h1_next_level_R'),
                    'resolution_source': 'CURRENT_CAUSAL_BUNDLE',
                }

                if not path['resolved']:
                    row['outcome_status'] = 'CENSORED_OPEN'
                    new_unresolved += 1
                else:
                    if symbol not in funding_cache:
                        funding_path = funding_root / f'{symbol}.json'
                        if not funding_path.exists():
                            raise SystemExit(f'FUNDING_SNAPSHOT_MISSING {symbol}')
                        funding_cache[symbol] = json.loads(funding_path.read_text())['records']

                    side = path['side_i']
                    entry = path['entry']
                    risk = path['risk']
                    exit_time = path['exit_time_dt']
                    raw_exit = path['raw_exit_price']
                    executed_exit = economics.adverse(raw_exit, side, False)
                    gross = (
                        (executed_exit - entry) / entry
                        if side == 1
                        else (entry - executed_exit) / entry
                    )
                    fee = economics.FEE_BPS / 10000 * (1 + executed_exit / entry)
                    funding = economics.funding_cost(
                        side,
                        entry,
                        offline.utc(event['entry_time']),
                        exit_time,
                        funding_cache[symbol],
                    )
                    net = gross - fee - funding
                    raw_entry = economics.raw_entry(entry, side)
                    raw_gross = (
                        (raw_exit - raw_entry) / raw_entry
                        if side == 1
                        else (raw_entry - raw_exit) / raw_entry
                    )
                    row.update(
                        {
                            'outcome_status': 'RESOLVED',
                            'exit_time': offline.z(exit_time),
                            'raw_exit_price': raw_exit,
                            'executed_exit_price': executed_exit,
                            'hold_bars': path['exit_i'] - path['entry_i'] + 1,
                            'gross_return_pct': gross,
                            'fee_pct': fee,
                            'funding_pct': funding,
                            'slippage_return_drag_pct': raw_gross - gross,
                            'net_return_pct': net,
                            'realized_R': net / (risk / entry),
                            'win_net': net > 0,
                            'funding_source': 'PERSISTED_OFFICIAL_BINANCE_SNAPSHOT',
                        }
                    )
                    new_resolved += 1

            row['family_role'] = role
            row['counts_as_independent_family_evidence'] = index == 0
            observations.append(row)

    current_keys = {stable_identity(event) for event in events}
    missing_prior = [key for key in prior_map if key not in current_keys]
    if missing_prior:
        raise SystemExit(f'PRIOR_ACCEPTED_OBSERVATION_MISSING_FROM_LEDGER {missing_prior[:3]!r}')

    families = []
    for family_id in sorted(groups):
        members = [row for row in observations if row['setup_family_id'] == family_id]
        primary = next(row for row in members if row['family_role'] == 'PRIMARY_REPRESENTATIVE')
        families.append(
            {
                'setup_family_id': family_id,
                'primary_symbol': primary['symbol'],
                'primary_side': primary['side'],
                'primary_entry_time': primary['entry_time'],
                'observation_count': len(members),
                'resolved': primary['resolved'],
                'terminal_state': primary.get('terminal_state'),
                'realized_R': primary.get('realized_R'),
                'mfe_R': primary.get('mfe_R'),
                'mae_R': primary.get('mae_R'),
                'family_evidence_status': (
                    'RESOLVED_PRIMARY' if primary['resolved'] else 'UNRESOLVED_PRIMARY'
                ),
            }
        )

    stamp = as_of.strftime('%Y%m%dT%H%M%SZ')
    out = output_root / stamp
    if out.exists():
        raise SystemExit(f'OUTPUT_EXISTS {out}')
    out.mkdir(parents=True)

    observations_path = out / 'observations.jsonl'
    families_path = out / 'families.jsonl'
    observations_path.write_text(
        ''.join(
            json.dumps(row, sort_keys=True) + '\n'
            for row in sorted(
                observations,
                key=lambda row: (
                    row.get('entry_time', ''),
                    row.get('symbol', ''),
                    row.get('setup_family_id', ''),
                ),
            )
        )
    )
    families_path.write_text(
        ''.join(json.dumps(row, sort_keys=True) + '\n' for row in families)
    )

    resolved = [row for row in families if row['resolved']]
    realized = [row['realized_R'] for row in resolved if row.get('realized_R') is not None]
    wins = sum(value > 0 for value in realized)
    ledger_summary = json.loads((LEDGER / 'ledger_summary.json').read_text())

    report = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_family_outcomes.offline_incremental.v1_1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'as_of': offline.z(as_of),
        'holdout_opened': False,
        'production_action': False,
        'network_used': False,
        'family_semantics': 'earliest eligible entry is immutable primary representative',
        'target_R': economics.TARGET_R,
        'max_hold_bars_m15': economics.MAX_HOLD,
        'fee_bps_per_side': economics.FEE_BPS,
        'slippage_bps_per_execution_side': economics.SLIP_BPS,
        'latest_bundle_root': str(bundle_root),
        'latest_bundle_set_sha256': snapshot.get('bundle_set_sha256'),
        'funding_snapshot_summary_sha256': sha(funding_summary),
        'prior_accepted_outcomes_path': str(prior_root),
        'prior_identity_abs_tol': PRIOR_PRICE_ABS_TOL,
        'prior_identity_rel_tol': PRIOR_PRICE_REL_TOL,
        'prior_terminal_reuse_count': prior_reuse,
        'prior_terminal_path_revalidated_count': prior_revalidated,
        'prior_terminal_source_window_expired_count': prior_source_window_expired,
        'max_prior_entry_abs_delta': max_entry_abs_delta,
        'max_prior_stop_abs_delta': max_stop_abs_delta,
        'new_resolved_observation_count': new_resolved,
        'new_unresolved_observation_count': new_unresolved,
        'eligible_observation_count': len(observations),
        'unique_family_count': len(families),
        'resolved_primary_family_count': len(resolved),
        'unresolved_primary_family_count': len(families) - len(resolved),
        'resolved_win_count': wins,
        'resolved_loss_count': len(realized) - wins,
        'resolved_win_rate': wins / len(realized) if realized else None,
        'resolved_expectancy_R': statistics.fmean(realized) if realized else None,
        'frozen_harness_sha256_values': ledger_summary.get('frozen_harness_sha256_values'),
        'protocol_sha256_values': ledger_summary.get('protocol_sha256_values'),
        'observation_sha256': sha(observations_path),
        'family_sha256': sha(families_path),
        'evidence_status': (
            'OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES'
            if len(resolved) < 30
            else (
                'DIAGNOSTIC_30_49_RESOLVED_FAMILIES'
                if len(resolved) < 50
                else (
                    'HYPOTHESIS_ONLY_50_99_RESOLVED_FAMILIES'
                    if len(resolved) < 100
                    else 'RECALIBRATION_PROPOSAL_ELIGIBLE_BY_SAMPLE_ONLY'
                )
            )
        ),
    }
    summary_path = out / 'summary.json'
    summary_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', summary_path, sha(summary_path))


if __name__ == '__main__':
    main()
