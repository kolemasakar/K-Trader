#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from collections import defaultdict

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
TIME_EXIT_SLOPE_BAND_R = 0.25
THRESHOLDS = ('0_5', '1_0', '2_0', '3_0')


def load_jsonl(path: pathlib.Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def metrics(rows):
    if not rows:
        return {'n': 0}
    return {
        'n': len(rows),
        'mean_realized_R': mean([r.get('realized_R') for r in rows]),
        'median_MFE_R': median([r.get('MFE_R') for r in rows]),
        'median_MAE_R': median([r.get('MAE_R') for r in rows]),
        'median_giveback_R': median([r.get('giveback_R') for r in rows]),
        'median_capture_ratio': median([r.get('capture_ratio') for r in rows]),
        'median_terminal_slope_4_R': median([r.get('terminal_slope_4_R') for r in rows]),
    }


def grouped(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[str(row.get(field))].append(row)
    return {k: metrics(v) for k, v in sorted(groups.items())}


def stop_category(row):
    mfe = float(row['MFE_R'])
    if mfe < 0.5:
        return 'IMMEDIATE_FAILURE_LT_0_5R'
    if mfe < 1.0:
        return 'PARTIAL_FAVORABLE_0_5_TO_1R'
    return 'FAVORABLE_THEN_REVERSAL_GE_1R'


def time_exit_state(row):
    slope = row.get('terminal_slope_4_R')
    if slope is None:
        return 'N/A'
    slope = float(slope)
    if slope >= TIME_EXIT_SLOPE_BAND_R:
        return 'EXPANDING'
    if slope <= -TIME_EXIT_SLOPE_BAND_R:
        return 'RETRACING'
    return 'STALLING'


def enrich(row):
    out = dict(row)
    gross_terminal_R = float(out['realized_R']) + float(out.get('explicit_cost_R') or 0.0)
    out['gross_terminal_R'] = gross_terminal_R
    out['giveback_R'] = float(out['MFE_R']) - gross_terminal_R
    out['capture_ratio'] = gross_terminal_R / float(out['MFE_R']) if float(out['MFE_R']) > 0 else None
    if out['exit_reason'] in {'STOP', 'GAP_STOP'}:
        out['stop_path_category'] = stop_category(out)
    else:
        out['stop_path_category'] = None
    if out['exit_reason'] == 'TIME_EXIT':
        out['time_exit_state'] = time_exit_state(out)
    else:
        out['time_exit_state'] = None
    return out


def threshold_summary(rows):
    result = {}
    for key in THRESHOLDS:
        reached_field = f'reached_{key}R'
        time_field = f'time_to_{key}R_bars'
        reached = [r for r in rows if r.get(reached_field)]
        result[f'reached_{key}R_n'] = len(reached)
        result[f'reached_{key}R_fraction'] = len(reached) / len(rows) if rows else None
        result[f'time_to_{key}R_median_bars'] = median([r.get(time_field) for r in reached])
    return result


def path_summary(rows):
    stops = [r for r in rows if r['exit_reason'] in {'STOP', 'GAP_STOP'}]
    targets = [r for r in rows if r['exit_reason'] in {'TARGET', 'GAP_TARGET'}]
    time_exits = [r for r in rows if r['exit_reason'] == 'TIME_EXIT']
    result = {
        'overall': metrics(rows),
        'thresholds': threshold_summary(rows),
        'stop_n': len(stops),
        'stop_categories': grouped(stops, 'stop_path_category'),
        'target_n': len(targets),
        'target_thresholds': threshold_summary(targets),
        'target_median_MAE_R': median([r.get('MAE_R') for r in targets]),
        'time_exit_n': len(time_exits),
        'time_exit_states': grouped(time_exits, 'time_exit_state'),
        'time_exit_thresholds': threshold_summary(time_exits),
        'time_exit_positive_n': sum(float(r['realized_R']) > 0 for r in time_exits),
        'time_exit_median_giveback_R': median([r.get('giveback_R') for r in time_exits]),
        'time_exit_median_capture_ratio': median([r.get('capture_ratio') for r in time_exits]),
    }
    return result


def merge_diag(rows, diag_rows):
    idx = {(r['symbol'], r['entry_time'], r.get('episode_key')): r for r in diag_rows}
    out = []
    for row in rows:
        x = dict(row)
        d = idx.get((row['symbol'], row['entry_time'], row.get('episode_key')))
        if d:
            for k, v in d.items():
                if k not in {'symbol', 'entry_time', 'episode_key', 'side', 'schema_version'}:
                    x[k] = v
        out.append(x)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = pathlib.Path(args.root)
    src_dir = root / 'combined_rules/mfe_mae_v2_2'
    diag_dir = root / 'combined_rules/level_context_v2_1_diag'
    out_dir = root / 'combined_rules/mfe_mae_v2_2_stage2'
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        'schema_version': 'ktrader.mfe_mae.v2_2.stage2.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'actual_path_only': True,
        'holdout_opened': False,
        'time_exit_slope_band_R': TIME_EXIT_SLOPE_BAND_R,
        'segments': {},
    }

    for segment in ('development', 'validation', 'non_holdout'):
        rows = load_jsonl(src_dir / f'{segment}.jsonl')
        diag_path = diag_dir / f'{segment}.jsonl'
        if diag_path.exists():
            rows = merge_diag(rows, load_jsonl(diag_path))
        rows = [enrich(r) for r in rows]

        with (out_dir / f'{segment}.jsonl').open('w') as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + '\n')

        stops = [r for r in rows if r['exit_reason'] in {'STOP', 'GAP_STOP'}]
        time_exits = [r for r in rows if r['exit_reason'] == 'TIME_EXIT']
        report['segments'][segment] = {
            **path_summary(rows),
            'stop_categories_by_h1_open_space': {
                key: grouped([r for r in stops if str(r.get('h1_open_space')) == key], 'stop_path_category')
                for key in sorted({str(r.get('h1_open_space')) for r in stops})
            },
            'stop_categories_by_obstacle_evidence': {
                key: grouped([r for r in stops if str(r.get('h1_obstacle_evidence_count')) == key], 'stop_path_category')
                for key in sorted({str(r.get('h1_obstacle_evidence_count')) for r in stops})
            },
            'by_strict_break_present': grouped(rows, 'strict_break_present'),
            'by_strict_mirror_retest': grouped(rows, 'strict_mirror_retest_present'),
            'time_exit_by_h1_open_space': grouped(time_exits, 'h1_open_space'),
        }

    p = out_dir / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
