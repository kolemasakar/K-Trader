#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
from collections import defaultdict
from datetime import datetime

ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
BOOTSTRAP_SEED = 20260911
BOOTSTRAP_DRAWS = 5000


def ts(v): return datetime.fromisoformat(v.replace('Z', '+00:00'))

def load_jsonl(path):
    with path.open() as f: return [json.loads(x) for x in f if x.strip()]


def perf(rows):
    if not rows: return {'n': 0, 'win_rate': None, 'expectancy_R': None, 'profit_factor_R': None}
    rs = [float(r['net_R']) for r in rows]
    gp = sum(max(0.0, x) for x in rs); gl = -sum(min(0.0, x) for x in rs)
    return {
        'n': len(rows),
        'win_rate': sum(x > 0 for x in rs) / len(rs),
        'expectancy_R': statistics.fmean(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def quantile(xs, q):
    if not xs: return None
    xs = sorted(xs)
    pos = (len(xs) - 1) * q
    lo = int(pos); hi = min(lo + 1, len(xs) - 1); w = pos - lo
    return xs[lo] * (1 - w) + xs[hi] * w


def chrono_folds(rows, k=4):
    rows = sorted(rows, key=lambda r: (ts(r['entry_time']), r['symbol']))
    out = []
    n = len(rows)
    for i in range(k):
        a = round(i * n / k); z = round((i + 1) * n / k)
        part = rows[a:z]
        out.append({
            'fold': i + 1,
            'start_entry': part[0]['entry_time'] if part else None,
            'end_entry': part[-1]['entry_time'] if part else None,
            **perf(part),
        })
    return out


def block_bootstrap_by_day(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[ts(r['entry_time']).date().isoformat()].append(r)
    days = sorted(groups)
    rng = random.Random(BOOTSTRAP_SEED)
    exps, wrs, pfs = [], [], []
    for _ in range(BOOTSTRAP_DRAWS):
        sample = []
        for _j in range(len(days)):
            d = rng.choice(days)
            sample.extend(groups[d])
        m = perf(sample)
        if m['expectancy_R'] is not None: exps.append(m['expectancy_R'])
        if m['win_rate'] is not None: wrs.append(m['win_rate'])
        if m['profit_factor_R'] is not None and m['profit_factor_R'] < 999: pfs.append(m['profit_factor_R'])
    return {
        'block': 'UTC entry day',
        'day_count': len(days),
        'draws': BOOTSTRAP_DRAWS,
        'seed': BOOTSTRAP_SEED,
        'expectancy_R_p025': quantile(exps, 0.025),
        'expectancy_R_median': quantile(exps, 0.5),
        'expectancy_R_p975': quantile(exps, 0.975),
        'win_rate_p025': quantile(wrs, 0.025),
        'win_rate_median': quantile(wrs, 0.5),
        'win_rate_p975': quantile(wrs, 0.975),
        'profit_factor_R_p025': quantile(pfs, 0.025),
        'profit_factor_R_median': quantile(pfs, 0.5),
        'profit_factor_R_p975': quantile(pfs, 0.975),
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default=str(ROOT)); args = ap.parse_args()
    root = pathlib.Path(args.root)
    rows = load_jsonl(root / 'combined_rules/v2_2_trades/non_holdout.jsonl')
    overall = perf(rows)

    symbols = sorted({r['symbol'] for r in rows})
    leave_one_symbol_out = {}
    for s in symbols:
        kept = [r for r in rows if r['symbol'] != s]
        removed = [r for r in rows if r['symbol'] == s]
        leave_one_symbol_out[s] = {
            'removed_n': len(removed),
            'removed_perf': perf(removed),
            'remaining_perf': perf(kept),
            'expectancy_shift_R': perf(kept)['expectancy_R'] - overall['expectancy_R'] if kept else None,
        }

    dates = sorted({ts(r['entry_time']).date().isoformat() for r in rows})
    by_day = {d: perf([r for r in rows if ts(r['entry_time']).date().isoformat() == d]) for d in dates}
    by_side = {s: perf([r for r in rows if r['side'] == s]) for s in sorted({r['side'] for r in rows})}

    report = {
        'schema_version': 'ktrader.robustness.v2_2.diagnostic.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'independent_oos_claim': False,
        'warning': 'These are concentration/stability diagnostics on already-seen non-holdout data. They are not independent validation and must not be used to tune v2.2.',
        'overall': overall,
        'chronological_quartiles': chrono_folds(rows, 4),
        'by_utc_entry_day': by_day,
        'by_side': by_side,
        'leave_one_symbol_out': leave_one_symbol_out,
        'day_block_bootstrap': block_bootstrap_by_day(rows),
        'prospective_independent_validation_status': 'WAITING_FOR_FRESH_FROZEN_SHADOW_FAMILIES',
    }

    out = root / 'combined_rules/robustness_v2_2'
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__': main()
