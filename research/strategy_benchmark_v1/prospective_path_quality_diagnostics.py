#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import statistics
from collections import Counter, defaultdict


def load_jsonl(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def mean(values):
    values = list(values)
    return statistics.fmean(values) if values else None


def median(values):
    values = list(values)
    return statistics.median(values) if values else None


def metrics(rows: list[dict]) -> dict:
    realized = [float(row['realized_R']) for row in rows]
    wins = sum(value > 0 for value in realized)
    return {
        'n': len(rows),
        'wins': wins,
        'win_rate': wins / len(rows) if rows else None,
        'expectancy_R': mean(realized),
        'median_R': median(realized),
        'mean_mfe_R': mean(float(row.get('mfe_R') or 0) for row in rows),
        'mean_mae_R': mean(float(row.get('mae_R') or 0) for row in rows),
        'median_hold_bars': median(int(row.get('hold_bars') or 0) for row in rows),
    }


def mfe_bucket(value: float) -> str:
    if value < 0.5:
        return '<0.5R'
    if value < 1.0:
        return '0.5-1R'
    if value < 2.0:
        return '1-2R'
    if value < 3.0:
        return '2-3R'
    return '>=3R'


def main() -> None:
    parser = argparse.ArgumentParser(description='Diagnostic-only path/MFE/MAE analysis for prospective primary families.')
    parser.add_argument('--outcomes', required=True, help='Outcome directory containing observations.jsonl and summary.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    outcomes = pathlib.Path(args.outcomes)
    summary = json.loads((outcomes / 'summary.json').read_text())
    rows = [
        row
        for row in load_jsonl(outcomes / 'observations.jsonl')
        if row.get('family_role') == 'PRIMARY_REPRESENTATIVE' and row.get('resolved')
    ]

    by_terminal = defaultdict(list)
    by_day = defaultdict(list)
    by_session = defaultdict(list)
    for row in rows:
        by_terminal[row.get('terminal_state')].append(row)
        by_day[row['entry_time'][:10]].append(row)
        hour = int(row['entry_time'][11:13])
        start = (hour // 6) * 6
        by_session[f'{start:02d}-{start + 5:02d}'].append(row)

    terminal = {}
    for name, group in sorted(by_terminal.items()):
        terminal[name] = {
            **metrics(group),
            'reached_0_5R': sum(bool((row.get('time_to_R') or {}).get('0.5R')) for row in group),
            'reached_1R': sum(bool((row.get('time_to_R') or {}).get('1R')) for row in group),
            'reached_2R': sum(bool((row.get('time_to_R') or {}).get('2R')) for row in group),
            'reached_3R': sum(bool((row.get('time_to_R') or {}).get('3R')) for row in group),
            'mfe_ge_1R_but_nonpositive': sum(
                float(row.get('mfe_R') or 0) >= 1.0 and float(row['realized_R']) <= 0 for row in group
            ),
            'mfe_ge_2R_but_nonpositive': sum(
                float(row.get('mfe_R') or 0) >= 2.0 and float(row['realized_R']) <= 0 for row in group
            ),
        }

    time_exit = by_terminal.get('TIME_EXIT', [])
    by_mfe = defaultdict(list)
    by_side = defaultdict(list)
    for row in time_exit:
        by_mfe[mfe_bucket(float(row.get('mfe_R') or 0))].append(row)
        by_side[row['side']].append(row)

    risk_cost_rows = []
    for row in rows:
        risk = float(row['initial_risk_pct'])
        cost_r = (
            float(row.get('fee_pct') or 0)
            + float(row.get('funding_pct') or 0)
            + float(row.get('slippage_return_drag_pct') or 0)
        ) / risk
        risk_cost_rows.append((row, cost_r, float(row['realized_R']) + cost_r))

    overall = metrics(rows)
    symbols = sorted({row['symbol'] for row in rows})
    loo = []
    for symbol in symbols:
        group = [row for row in rows if row['symbol'] != symbol]
        expectancy = mean(float(row['realized_R']) for row in group)
        loo.append(
            {
                'excluded_symbol': symbol,
                'n': len(group),
                'expectancy_R': expectancy,
                'delta_vs_all': expectancy - overall['expectancy_R'],
            }
        )

    report = {
        'schema_version': 'ktrader.prospective_path_quality.v1',
        'as_of': summary.get('as_of'),
        'diagnostic_only': True,
        'holdout_opened': False,
        'production_action': False,
        'overall': overall,
        'terminal_state': terminal,
        'time_exit_by_mfe_bucket': {key: metrics(value) for key, value in sorted(by_mfe.items())},
        'time_exit_by_side': {key: metrics(value) for key, value in sorted(by_side.items())},
        'execution_costs': {
            'mean_total_cost_R': mean(cost for _, cost, _ in risk_cost_rows),
            'median_total_cost_R': median(cost for _, cost, _ in risk_cost_rows),
            'mean_pre_cost_R': mean(pre for _, _, pre in risk_cost_rows),
            'post_cost_expectancy_R': overall['expectancy_R'],
            'families_pre_cost_positive_post_cost_nonpositive': sum(
                pre > 0 and float(row['realized_R']) <= 0 for row, _, pre in risk_cost_rows
            ),
        },
        'by_day': {key: metrics(value) for key, value in sorted(by_day.items())},
        'by_utc_session': {key: metrics(value) for key, value in sorted(by_session.items())},
        'leave_one_symbol_out': loo,
        'symbol_counts': dict(Counter(row['symbol'] for row in rows)),
    }

    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', output, hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
