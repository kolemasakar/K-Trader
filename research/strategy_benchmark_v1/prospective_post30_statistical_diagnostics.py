#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
import statistics

PERMUTATIONS = 200_000
BOOTSTRAPS = 100_000


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    row1 = a + b
    col1 = a + c
    lo = max(0, row1 - (n - col1))
    hi = min(row1, col1)

    def probability(x: int) -> float:
        return math.comb(col1, x) * math.comb(n - col1, row1 - x) / math.comb(n, row1)

    observed = probability(a)
    return min(1.0, sum(probability(x) for x in range(lo, hi + 1) if probability(x) <= observed + 1e-15))


def contrast(name: str, group_a: list[dict], group_b: list[dict], seed: int) -> dict:
    xa = [float(row['realized_R']) for row in group_a]
    xb = [float(row['realized_R']) for row in group_b]
    observed = statistics.fmean(xa) - statistics.fmean(xb)
    wins_a = sum(value > 0 for value in xa)
    wins_b = sum(value > 0 for value in xb)

    pool = xa + xb
    na = len(xa)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(PERMUTATIONS):
        shuffled = pool[:]
        rng.shuffle(shuffled)
        diff = statistics.fmean(shuffled[:na]) - statistics.fmean(shuffled[na:])
        if abs(diff) >= abs(observed) - 1e-15:
            extreme += 1

    rng = random.Random(seed + 1000)
    boot = []
    for _ in range(BOOTSTRAPS):
        aa = [xa[rng.randrange(len(xa))] for __ in range(len(xa))]
        bb = [xb[rng.randrange(len(xb))] for __ in range(len(xb))]
        boot.append(statistics.fmean(aa) - statistics.fmean(bb))
    boot.sort()

    return {
        'name': name,
        'n_a': len(group_a),
        'n_b': len(group_b),
        'wins_a': wins_a,
        'wins_b': wins_b,
        'expectancy_a': statistics.fmean(xa),
        'expectancy_b': statistics.fmean(xb),
        'mean_diff_a_minus_b': observed,
        'bootstrap95_diff': [boot[int(0.025 * BOOTSTRAPS)], boot[int(0.975 * BOOTSTRAPS) - 1]],
        'permutation_p_two_sided': (extreme + 1) / (PERMUTATIONS + 1),
        'fisher_winrate_p_two_sided': fisher_two_sided(
            wins_a,
            len(xa) - wins_a,
            wins_b,
            len(xb) - wins_b,
        ),
    }


def benjamini_hochberg(values: list[float]) -> list[float]:
    m = len(values)
    order = sorted(range(m), key=lambda i: values[i])
    out = [1.0] * m
    previous = 1.0
    for position in range(m - 1, -1, -1):
        index = order[position]
        rank = position + 1
        q = min(previous, values[index] * m / rank)
        out[index] = q
        previous = q
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    report_path = pathlib.Path(args.report)
    output_path = pathlib.Path(args.output)
    if output_path.exists():
        raise SystemExit(f'OUTPUT_EXISTS {output_path}')

    report = json.loads(report_path.read_text())
    if not report.get('diagnostic_only') or report.get('holdout_opened') or report.get('production_action'):
        raise SystemExit('SOURCE_REPORT_GOVERNANCE_GUARD_FAILED')
    rows = [
        row
        for row in report['rows']
        if row.get('resolved') and row.get('realized_R') is not None
    ]

    definitions = [
        ('side SHORT vs LONG', 'side', 'SHORT', 'LONG', 11),
        ('rich obstacle <3R true vs false', 'rich_obstacle_inside_3R', True, False, 12),
        ('rich obstacle <1R true vs false', 'rich_obstacle_inside_1R', True, False, 13),
        ('clean break true vs false', 'clean_break_no_revisit', True, False, 14),
        ('floating zone true vs false', 'floating_zone_flag', True, False, 15),
        ('VSA opposing vs none', 'vsa_state', 'OPPOSING', 'NONE', 16),
    ]

    tests = []
    for name, key, value_a, value_b, seed in definitions:
        a = [row for row in rows if row.get(key) == value_a]
        b = [row for row in rows if row.get(key) == value_b]
        if a and b:
            tests.append(contrast(name, a, b, seed))

    for field, qfield in (
        ('permutation_p_two_sided', 'permutation_bh_q'),
        ('fisher_winrate_p_two_sided', 'fisher_bh_q'),
    ):
        adjusted = benjamini_hochberg([row[field] for row in tests])
        for row, q in zip(tests, adjusted):
            row[qfield] = q

    out = {
        'schema_version': 'ktrader.prospective_post30_statistical_diagnostics.v1',
        'diagnostic_only': True,
        'holdout_opened': False,
        'production_action': False,
        'network_used': False,
        'source_report': str(report_path),
        'source_report_sha256': sha(report_path),
        'resolved_family_n': len(rows),
        'permutation_iterations': PERMUTATIONS,
        'bootstrap_iterations': BOOTSTRAPS,
        'multiple_comparison': 'Benjamini-Hochberg across listed exploratory contrasts',
        'tests': tests,
        'interpretation_guard': 'Exploratory diagnostics only; do not convert subgroup differences into frozen-v2.2 filters or retuning decisions.',
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))
    print('REPORT', output_path, sha(output_path))


if __name__ == '__main__':
    main()
