#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
CORR_THRESHOLD = 0.70
MIN_COMMON_RETURNS = 100
ENTRY_COHORT_MINUTES = 60


def ts(v: str) -> datetime:
    return datetime.fromisoformat(v.replace('Z', '+00:00'))


def load_jsonl(path: pathlib.Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def load_candles(path: pathlib.Path):
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
            out.append((d['open_time'], float(d['close'])))
    return out


def split(n: int):
    return int(math.floor(n * 0.60)), int(math.floor(n * 0.80))


def return_map(candles, end_idx):
    out = {}
    z = min(end_idx, len(candles))
    for i in range(1, z):
        p0, p1 = candles[i - 1][1], candles[i][1]
        if p0 > 0 and p1 > 0:
            out[candles[i][0]] = math.log(p1 / p0)
    return out


def pearson_maps(a, b):
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
    def __init__(self, n):
        self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[b] = a


def components(dsu, labels):
    groups = defaultdict(list)
    for i, label in enumerate(labels):
        groups[dsu.find(i)].append(label)
    return sorted(groups.values(), key=lambda x: (-len(x), x))


def max_concurrent(trades, predicate=lambda t: True):
    events = []
    for t in trades:
        if not predicate(t):
            continue
        events.append((ts(t['entry_time']), 1))
        events.append((ts(t['exit_time']), -1))
    # exit first at identical timestamp
    events.sort(key=lambda x: (x[0], x[1]))
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best


def metrics(rows):
    if not rows:
        return {'n': 0}
    rs = [float(x['net_R']) for x in rows]
    gp = sum(max(0.0, x) for x in rs)
    gl = -sum(min(0.0, x) for x in rs)
    return {
        'n': len(rows),
        'win_rate': sum(x > 0 for x in rs) / len(rs),
        'expectancy_R': statistics.fmean(rs),
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(ROOT))
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    trades = load_jsonl(root / 'combined_rules/v2_2_trades/non_holdout.jsonl')
    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    symbols = sorted({t['symbol'] for t in trades})

    ret_maps = {}
    for s in symbols:
        candles = load_candles(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
        _, v = split(len(candles))
        ret_maps[s] = return_map(candles, v)

    pairwise = []
    corr_lookup = {}
    sym_dsu = DSU(len(symbols))
    idx = {s: i for i, s in enumerate(symbols)}
    for i, a in enumerate(symbols):
        for b in symbols[i + 1:]:
            rho, common = pearson_maps(ret_maps[a], ret_maps[b])
            pairwise.append({'a': a, 'b': b, 'rho': rho, 'common_returns': common})
            if rho is not None:
                corr_lookup[(a, b)] = corr_lookup[(b, a)] = rho
                if abs(rho) >= CORR_THRESHOLD:
                    sym_dsu.union(idx[a], idx[b])

    symbol_corr_clusters = components(sym_dsu, symbols)

    trade_dsu = DSU(len(trades))
    edge_count = 0
    for i, a in enumerate(trades):
        ea = ts(a['entry_time'])
        for j in range(i + 1, len(trades)):
            b = trades[j]
            if a['side'] != b['side']:
                continue
            mins = abs((ea - ts(b['entry_time'])).total_seconds()) / 60.0
            if mins > ENTRY_COHORT_MINUTES:
                continue
            rho = 1.0 if a['symbol'] == b['symbol'] else corr_lookup.get((a['symbol'], b['symbol']))
            if rho is not None and abs(rho) >= CORR_THRESHOLD:
                trade_dsu.union(i, j)
                edge_count += 1

    trade_groups_idx = defaultdict(list)
    for i in range(len(trades)):
        trade_groups_idx[trade_dsu.find(i)].append(i)
    families = []
    for fid, inds in enumerate(sorted(trade_groups_idx.values(), key=lambda z: (min(ts(trades[i]['entry_time']) for i in z), min(z)))):
        rows = [trades[i] for i in inds]
        families.append({
            'diagnostic_family_id': f'F{fid + 1:03d}',
            'trade_count': len(rows),
            'symbols': sorted({r['symbol'] for r in rows}),
            'side': rows[0]['side'] if len({r['side'] for r in rows}) == 1 else 'MIXED',
            'first_entry': min(r['entry_time'] for r in rows),
            'last_entry': max(r['entry_time'] for r in rows),
            **metrics(rows),
        })

    counts = Counter(t['symbol'] for t in trades)
    n = len(trades)
    hhi = sum((c / n) ** 2 for c in counts.values()) if n else None
    side_counts = Counter(t['side'] for t in trades)

    cluster_max_concurrent = []
    for ci, cluster in enumerate(symbol_corr_clusters, 1):
        ss = set(cluster)
        cluster_max_concurrent.append({
            'cluster_id': f'C{ci:02d}',
            'symbols': cluster,
            'trade_count': sum(1 for t in trades if t['symbol'] in ss),
            'max_concurrent': max_concurrent(trades, lambda t, ss=ss: t['symbol'] in ss),
        })

    summary = {
        'schema_version': 'ktrader.portfolio_correlation.v2_2.diagnostic.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'correlation_definition': {
            'returns': '15m log returns, non-holdout source window',
            'abs_rho_cluster_threshold': CORR_THRESHOLD,
            'minimum_common_returns': MIN_COMMON_RETURNS,
        },
        'diagnostic_family_definition': {
            'same_side': True,
            'entry_within_minutes': ENTRY_COHORT_MINUTES,
            'same_symbol_or_abs_return_corr_gte': CORR_THRESHOLD,
            'warning': 'diagnostic grouping only; not canonical setup-family semantics',
        },
        'raw_trade_count': n,
        'diagnostic_family_count': len(families),
        'family_size_max': max((x['trade_count'] for x in families), default=0),
        'families_multi_trade': sum(x['trade_count'] > 1 for x in families),
        'trade_graph_edge_count': edge_count,
        'max_concurrent_all': max_concurrent(trades),
        'max_concurrent_long': max_concurrent(trades, lambda t: t['side'] == 'LONG'),
        'max_concurrent_short': max_concurrent(trades, lambda t: t['side'] == 'SHORT'),
        'side_counts': dict(sorted(side_counts.items())),
        'symbol_trade_counts': dict(sorted(counts.items())),
        'symbol_trade_hhi': hhi,
        'top_symbol_share': max(counts.values()) / n if n else None,
        'symbol_correlation_clusters': symbol_corr_clusters,
        'cluster_exposure': cluster_max_concurrent,
        'families': families,
        'pairwise_correlations': sorted(pairwise, key=lambda x: (x['a'], x['b'])),
        'overall': metrics(trades),
    }

    out = root / 'combined_rules/portfolio_correlation_v2_2'
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'report.json'
    p.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: summary[k] for k in (
        'raw_trade_count','diagnostic_family_count','family_size_max','families_multi_trade',
        'max_concurrent_all','max_concurrent_long','max_concurrent_short','symbol_trade_hhi',
        'top_symbol_share','symbol_correlation_clusters','cluster_exposure','overall'
    )}, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
