#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal

BASE = pathlib.Path('/data/research/phase11g')
CORR_THRESHOLD = 0.70
MIN_COMMON_RETURNS = 100
ENTRY_COHORT_MINUTES = 60
VSA_BASELINE_WINDOW = 20


def utc(value: str) -> datetime:
    d = datetime.fromisoformat(value[:-1] + '+00:00' if value.endswith('Z') else value)
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds() != 0:
        raise ValueError('UTC required')
    return d.astimezone(timezone.utc)


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: pathlib.Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def metrics(rows: list[dict]) -> dict:
    resolved = [r for r in rows if r.get('resolved') and r.get('realized_R') is not None]
    rs = [float(r['realized_R']) for r in resolved]
    if not rs:
        return {'n_total': len(rows), 'n_resolved': 0}
    gp = sum(max(0.0, x) for x in rs)
    gl = -sum(min(0.0, x) for x in rs)
    return {
        'n_total': len(rows),
        'n_resolved': len(rs),
        'wins': sum(x > 0 for x in rs),
        'losses': sum(x <= 0 for x in rs),
        'win_rate': sum(x > 0 for x in rs) / len(rs),
        'expectancy_R': statistics.fmean(rs),
        'median_R': statistics.median(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def grouped_metrics(rows: list[dict], key: str) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return {k: metrics(v) for k, v in sorted(groups.items())}


def load_bars(path: pathlib.Path) -> list[dict]:
    out = []
    with path.open() as f:
        first = True
        for line in f:
            d = json.loads(line)
            if first and d.get('record_type') == 'manifest':
                first = False
                continue
            first = False
            if d.get('record_type') != 'candle':
                continue
            out.append(
                {
                    'open_time': d['open_time'],
                    'close_time': d['close_time'],
                    'open_dt': utc(d['open_time']),
                    'open': Decimal(str(d['open'])),
                    'high': Decimal(str(d['high'])),
                    'low': Decimal(str(d['low'])),
                    'close': Decimal(str(d['close'])),
                    'volume': Decimal(str(d['volume'])),
                }
            )
    return out


def detect_vsa_at(bars: list[dict], index: int | None) -> list[dict]:
    i = index
    if i is None or i < VSA_BASELINE_WINDOW or i < 2 or i >= len(bars):
        return []
    bar = bars[i]
    prior = bars[i - VSA_BASELINE_WINDOW:i]
    avg_volume = sum((x['volume'] for x in prior), Decimal('0')) / Decimal(VSA_BASELINE_WINDOW)
    avg_spread = sum((x['high'] - x['low'] for x in prior), Decimal('0')) / Decimal(VSA_BASELINE_WINDOW)
    spread = bar['high'] - bar['low']
    if avg_volume <= 0 or avg_spread <= 0 or spread <= 0:
        return []
    rel_volume = bar['volume'] / avg_volume
    rel_spread = spread / avg_spread
    close_loc = (bar['close'] - bar['low']) / spread
    p1, p2 = bars[i - 1], bars[i - 2]
    lower_than_prior_two = bar['volume'] < p1['volume'] and bar['volume'] < p2['volume']
    out = []

    def add(event_type: str, direction: str) -> None:
        out.append(
            {
                'event_type': event_type,
                'direction': direction,
                'relative_volume': float(rel_volume),
                'relative_spread': float(rel_spread),
                'close_location': float(close_loc),
            }
        )

    if bar['close'] < bar['open'] and rel_spread <= Decimal('0.8') and rel_volume <= Decimal('0.8') and lower_than_prior_two and close_loc >= Decimal('0.5'):
        add('NS', 'LONG')
    if bar['close'] > bar['open'] and rel_spread <= Decimal('0.8') and rel_volume <= Decimal('0.8') and lower_than_prior_two and close_loc <= Decimal('0.5'):
        add('ND', 'SHORT')
    if bar['low'] < min(p1['low'], p2['low']) and close_loc >= Decimal('0.6') and rel_spread <= Decimal('1.0') and rel_volume <= Decimal('1.0'):
        add('T', 'LONG')
    if bar['high'] > max(p1['high'], p2['high']) and close_loc <= Decimal('0.35') and rel_spread >= Decimal('1.2') and rel_volume >= Decimal('1.2'):
        add('UT', 'SHORT')
    if bar['close'] >= bar['open'] and rel_spread >= Decimal('1.5') and rel_volume >= Decimal('1.8') and close_loc <= Decimal('0.75'):
        add('BC', 'SHORT')
    if bar['close'] <= bar['open'] and rel_spread >= Decimal('1.5') and rel_volume >= Decimal('1.8') and close_loc >= Decimal('0.25'):
        add('SC', 'LONG')
    if bar['close'] <= bar['open'] and rel_volume >= Decimal('1.5') and rel_spread <= Decimal('1.0') and close_loc >= Decimal('0.5'):
        add('SV', 'LONG')
    return out


def return_map(bars: list[dict]) -> dict[str, float]:
    out = {}
    for i in range(1, len(bars)):
        p0, p1 = float(bars[i - 1]['close']), float(bars[i]['close'])
        if p0 > 0 and p1 > 0:
            out[bars[i]['open_time']] = math.log(p1 / p0)
    return out


def pearson_maps(a: dict[str, float], b: dict[str, float]) -> tuple[float | None, int]:
    keys = sorted(set(a).intersection(b))
    if len(keys) < MIN_COMMON_RETURNS:
        return None, len(keys)
    xs = [a[k] for k in keys]
    ys = [b[k] for k in keys]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None, len(keys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy), len(keys)


class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[b] = a


def components(dsu: DSU, labels: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for i, label in enumerate(labels):
        groups[dsu.find(i)].append(label)
    return sorted((sorted(v) for v in groups.values()), key=lambda x: (-len(x), x))


def max_concurrent(rows: list[dict], as_of: datetime, side: str | None = None) -> int:
    events = []
    for row in rows:
        if side is not None and row['side'] != side:
            continue
        start = utc(row['entry_time'])
        end = utc(row['exit_time']) if row.get('resolved') and row.get('exit_time') else as_of
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    current = best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


def cost_summary(rows: list[dict]) -> dict:
    resolved = [r for r in rows if r.get('resolved') and r.get('initial_risk_pct')]
    if not resolved:
        return {'n': 0}

    def vals(field: str) -> list[float]:
        out = []
        for row in resolved:
            v = row.get(field)
            if v is not None:
                out.append(float(v) / float(row['initial_risk_pct']))
        return out

    fee = vals('fee_pct')
    funding = vals('funding_pct')
    slippage = vals('slippage_return_drag_pct')
    return {
        'n': len(resolved),
        'mean_fee_R': statistics.fmean(fee) if fee else None,
        'median_fee_R': statistics.median(fee) if fee else None,
        'mean_funding_signed_cost_R': statistics.fmean(funding) if funding else None,
        'median_funding_signed_cost_R': statistics.median(funding) if funding else None,
        'mean_slippage_drag_R': statistics.fmean(slippage) if slippage else None,
        'median_slippage_drag_R': statistics.median(slippage) if slippage else None,
        'mean_fee_plus_funding_R': statistics.fmean([a + b for a, b in zip(fee, funding)]) if len(fee) == len(funding) and fee else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--as-of', required=True)
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--outcomes', required=True)
    ap.add_argument('--bundle-root', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    as_of = utc(args.as_of)
    ledger_path = pathlib.Path(args.ledger)
    outcomes_root = pathlib.Path(args.outcomes)
    bundle_root = pathlib.Path(args.bundle_root)
    output = pathlib.Path(args.output)
    if output.exists():
        raise SystemExit(f'OUTPUT_EXISTS {output}')

    eligible = [r for r in load_jsonl(ledger_path) if r.get('status') == 'ELIGIBLE_SHADOW_SETUP']
    groups = defaultdict(list)
    for row in eligible:
        groups[row['setup_family_id']].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: (r.get('entry_time') or '', r.get('signal_bar_open_time') or '', r.get('symbol') or '', r.get('side') or ''))
    primary_events = {family_id: rows[0] for family_id, rows in groups.items()}

    outcome_observations = load_jsonl(outcomes_root / 'observations.jsonl')
    primary_outcomes = {
        r['setup_family_id']: r
        for r in outcome_observations
        if r.get('family_role') == 'PRIMARY_REPRESENTATIVE'
    }
    if set(primary_events) != set(primary_outcomes):
        raise SystemExit('LEDGER_OUTCOME_FAMILY_SET_MISMATCH')

    bars_cache = {}
    bar_index = {}
    ret_maps = {}
    rows = []
    for family_id in sorted(primary_events):
        event = primary_events[family_id]
        outcome = primary_outcomes[family_id]
        symbol = event['symbol']
        if symbol not in bars_cache:
            bars_cache[symbol] = load_bars(bundle_root / symbol / '15m.jsonl')
            bar_index[symbol] = {b['open_time']: i for i, b in enumerate(bars_cache[symbol])}
            ret_maps[symbol] = return_map(bars_cache[symbol])
        signal_i = bar_index[symbol].get(event.get('signal_bar_open_time'))
        vsa_events = detect_vsa_at(bars_cache[symbol], signal_i)
        aligned = [x['event_type'] for x in vsa_events if x['direction'] == event['side']]
        opposing = [x['event_type'] for x in vsa_events if x['direction'] != event['side']]
        if aligned and opposing:
            vsa_state = 'MIXED'
        elif aligned:
            vsa_state = 'ALIGNED'
        elif opposing:
            vsa_state = 'OPPOSING'
        elif signal_i is None:
            vsa_state = 'SOURCE_SIGNAL_BAR_UNAVAILABLE'
        else:
            vsa_state = 'NONE'

        frozen = event.get('frozen_v2_2_level_features') or {}
        rich_open = event.get('level_v2_h1_open_space')
        frozen_open = frozen.get('open_space')
        rich_next = event.get('level_v2_h1_next_level_R')
        row = {
            'setup_family_id': family_id,
            'symbol': event['symbol'],
            'side': event['side'],
            'signal_bar_open_time': event.get('signal_bar_open_time'),
            'entry_time': outcome['entry_time'],
            'exit_time': outcome.get('exit_time'),
            'resolved': outcome.get('resolved'),
            'terminal_state': outcome.get('terminal_state'),
            'realized_R': outcome.get('realized_R'),
            'initial_risk_pct': outcome.get('initial_risk_pct'),
            'fee_pct': outcome.get('fee_pct'),
            'funding_pct': outcome.get('funding_pct'),
            'slippage_return_drag_pct': outcome.get('slippage_return_drag_pct'),
            'clean_break_no_revisit': bool(event.get('clean_break_no_revisit')),
            'frozen_open_space': frozen_open,
            'rich_open_space': rich_open,
            'rich_next_level_R': rich_next,
            'frozen_vs_rich_open_space_disagreement': frozen_open is not None and rich_open is not None and frozen_open != rich_open,
            'rich_obstacle_inside_3R': rich_next is not None and float(rich_next) < 3.0,
            'rich_obstacle_inside_1R': rich_next is not None and float(rich_next) < 1.0,
            'floating_zone_flag': event.get('level_v2_h1_floating_zone_flag'),
            'consolidation_present': event.get('level_v2_h1_consolidation_present'),
            'vsa_state': vsa_state,
            'vsa_events': vsa_events,
        }
        rows.append(row)

    symbols = sorted({r['symbol'] for r in rows})
    corr_lookup = {}
    pairwise = []
    symbol_dsu = DSU(len(symbols))
    symbol_index = {s: i for i, s in enumerate(symbols)}
    for i, a in enumerate(symbols):
        for b in symbols[i + 1:]:
            rho, common = pearson_maps(ret_maps[a], ret_maps[b])
            pairwise.append({'a': a, 'b': b, 'rho': rho, 'common_returns': common})
            if rho is not None:
                corr_lookup[(a, b)] = corr_lookup[(b, a)] = rho
                if abs(rho) >= CORR_THRESHOLD:
                    symbol_dsu.union(symbol_index[a], symbol_index[b])

    family_dsu = DSU(len(rows))
    edge_count = 0
    for i, a in enumerate(rows):
        ea = utc(a['entry_time'])
        for j in range(i + 1, len(rows)):
            b = rows[j]
            if a['side'] != b['side']:
                continue
            mins = abs((ea - utc(b['entry_time'])).total_seconds()) / 60.0
            if mins > ENTRY_COHORT_MINUTES:
                continue
            rho = 1.0 if a['symbol'] == b['symbol'] else corr_lookup.get((a['symbol'], b['symbol']))
            if rho is not None and abs(rho) >= CORR_THRESHOLD:
                family_dsu.union(i, j)
                edge_count += 1

    cohort_idx = defaultdict(list)
    for i in range(len(rows)):
        cohort_idx[family_dsu.find(i)].append(i)
    cohorts = []
    for cohort_no, inds in enumerate(sorted(cohort_idx.values(), key=lambda z: min(utc(rows[i]['entry_time']) for i in z)), 1):
        cohort_rows = [rows[i] for i in inds]
        cohorts.append(
            {
                'diagnostic_cohort_id': f'P{cohort_no:03d}',
                'family_count': len(cohort_rows),
                'symbols': sorted({r['symbol'] for r in cohort_rows}),
                'side': cohort_rows[0]['side'],
                'first_entry': min(r['entry_time'] for r in cohort_rows),
                'last_entry': max(r['entry_time'] for r in cohort_rows),
                'performance': metrics(cohort_rows),
            }
        )

    counts = Counter(r['symbol'] for r in rows)
    n = len(rows)
    hhi = sum((c / n) ** 2 for c in counts.values()) if n else None

    report = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_post30_diagnostics.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'as_of': args.as_of,
        'diagnostic_only': True,
        'holdout_opened': False,
        'production_action': False,
        'network_used': False,
        'source_ledger': str(ledger_path),
        'source_ledger_sha256': sha(ledger_path),
        'source_outcomes': str(outcomes_root),
        'source_observations_sha256': sha(outcomes_root / 'observations.jsonl'),
        'bundle_root': str(bundle_root),
        'overall': metrics(rows),
        'by_side': grouped_metrics(rows, 'side'),
        'by_symbol': grouped_metrics(rows, 'symbol'),
        'by_terminal_state': grouped_metrics([r for r in rows if r.get('resolved')], 'terminal_state'),
        'level_context': {
            'by_clean_break_no_revisit': grouped_metrics(rows, 'clean_break_no_revisit'),
            'by_rich_obstacle_inside_3R': grouped_metrics(rows, 'rich_obstacle_inside_3R'),
            'by_rich_obstacle_inside_1R': grouped_metrics(rows, 'rich_obstacle_inside_1R'),
            'by_floating_zone_flag': grouped_metrics(rows, 'floating_zone_flag'),
            'by_consolidation_present': grouped_metrics(rows, 'consolidation_present'),
            'frozen_vs_rich_open_space_disagreement_count': sum(bool(r['frozen_vs_rich_open_space_disagreement']) for r in rows),
        },
        'vsa': {
            'by_alignment_state': grouped_metrics(rows, 'vsa_state'),
            'source_signal_bar_unavailable_count': sum(r['vsa_state'] == 'SOURCE_SIGNAL_BAR_UNAVAILABLE' for r in rows),
            'any_raw_vsa_count': sum(bool(r['vsa_events']) for r in rows),
        },
        'execution_costs_primary_resolved': cost_summary(rows),
        'portfolio': {
            'symbol_family_counts': dict(sorted(counts.items())),
            'symbol_hhi': hhi,
            'top_symbol_share': max(counts.values()) / n if n else None,
            'max_concurrent_all': max_concurrent(rows, as_of),
            'max_concurrent_long': max_concurrent(rows, as_of, 'LONG'),
            'max_concurrent_short': max_concurrent(rows, as_of, 'SHORT'),
            'correlation_definition': {
                'returns': 'current captured 15m log returns',
                'abs_rho_threshold': CORR_THRESHOLD,
                'minimum_common_returns': MIN_COMMON_RETURNS,
            },
            'symbol_correlation_clusters': components(symbol_dsu, symbols),
            'same_side_60m_correlated_cohort_count': len(cohorts),
            'multi_family_correlated_cohort_count': sum(c['family_count'] > 1 for c in cohorts),
            'largest_correlated_cohort_size': max((c['family_count'] for c in cohorts), default=0),
            'trade_graph_edge_count': edge_count,
            'cohorts': cohorts,
            'pairwise_correlations': pairwise,
        },
        'rows': rows,
        'governance': {
            'evidence_tier': 'DIAGNOSTIC_30_49_RESOLVED_FAMILIES',
            'retuning_authorized': False,
            'holdout_authorized': False,
            'production_mutation_authorized': False,
            'interpretation': 'Descriptive diagnostics only; subgroup differences are not promotion or filter decisions.',
        },
    }

    output.mkdir(parents=True)
    report_path = output / 'report.json'
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(
        json.dumps(
            {
                'overall': report['overall'],
                'by_side': report['by_side'],
                'by_terminal_state': report['by_terminal_state'],
                'level_context': report['level_context'],
                'vsa': report['vsa'],
                'execution_costs_primary_resolved': report['execution_costs_primary_resolved'],
                'portfolio': {k: report['portfolio'][k] for k in (
                    'symbol_family_counts', 'symbol_hhi', 'top_symbol_share',
                    'max_concurrent_all', 'max_concurrent_long', 'max_concurrent_short',
                    'symbol_correlation_clusters', 'same_side_60m_correlated_cohort_count',
                    'multi_family_correlated_cohort_count', 'largest_correlated_cohort_size',
                    'trade_graph_edge_count',
                )},
            },
            indent=2,
            sort_keys=True,
        )
    )
    print('REPORT', report_path, sha(report_path))


if __name__ == '__main__':
    main()
