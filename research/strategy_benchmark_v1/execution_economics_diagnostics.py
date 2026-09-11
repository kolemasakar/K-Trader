#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import statistics
from collections import defaultdict

ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
HARNESS = ROOT / 'harness/candidate_v2_2_backtest.py'


def load_module(path):
    sp = importlib.util.spec_from_file_location('candidate_v2_2_frozen_execdiag', path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def key(t):
    return (t['symbol'], t['side'], t.get('episode_key'))


def risk_bucket(x):
    if x < 0.015:
        return '1.25-1.5%'
    if x < 0.02:
        return '1.5-2.0%'
    if x < 0.03:
        return '2.0-3.0%'
    return '>=3.0%'


def liquidity_bucket(x):
    if x is None:
        return 'N/A'
    if x < 0.75:
        return '<0.75x'
    if x < 1.25:
        return '0.75-1.25x'
    return '>=1.25x'


def summary(rows):
    if not rows:
        return {'n': 0}
    return {
        'n': len(rows),
        'mean_net_R': mean([r['base_net_R'] for r in rows]),
        'median_fee_R': median([r['fee_R'] for r in rows]),
        'median_funding_R_signed_cost': median([r['funding_R_signed_cost'] for r in rows]),
        'median_explicit_cost_R': median([r['explicit_cost_R'] for r in rows]),
        'mean_explicit_cost_R': mean([r['explicit_cost_R'] for r in rows]),
        'median_zero_to_base_execution_drag_R': median([r['zero_to_base_execution_drag_R'] for r in rows]),
        'mean_zero_to_base_execution_drag_R': mean([r['zero_to_base_execution_drag_R'] for r in rows]),
        'median_base_to_stress_execution_drag_R': median([r['base_to_stress_execution_drag_R'] for r in rows]),
        'mean_base_to_stress_execution_drag_R': mean([r['base_to_stress_execution_drag_R'] for r in rows]),
        'median_total_base_cost_plus_execution_drag_R': median([
            (r['explicit_cost_R'] + r['zero_to_base_execution_drag_R'])
            if r['zero_to_base_execution_drag_R'] is not None else None
            for r in rows
        ]),
    }


def grouped(rows, field):
    g = defaultdict(list)
    for r in rows:
        g[str(r.get(field))].append(r)
    return {k: summary(v) for k, v in sorted(g.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(ROOT))
    ap.add_argument('--harness', default=str(HARNESS))
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    frozen = load_module(pathlib.Path(args.harness))
    b = frozen.b

    manifest = json.loads((root / 'sources/sources_manifest.json').read_text())
    protocol = json.loads((root / 'protocol.json').read_text())
    syms = protocol['primary_panel']['symbols']
    m15s, h1s, funds = {}, {}, {}
    for s in syms:
        m15s[s] = b.load_bars(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
        h1s[s] = b.load_bars(pathlib.Path(manifest['merged_histories'][s]['1h']['path']))
        funds[s] = b.load_funding(pathlib.Path(manifest['funding'][s]['path']))

    _, zero = frozen.run_segment(m15s, h1s, funds, 'non_holdout', 0.0)
    _, base = frozen.run_segment(m15s, h1s, funds, 'non_holdout', b.SLIPPAGE_BPS['base'])
    _, stress = frozen.run_segment(m15s, h1s, funds, 'non_holdout', b.SLIPPAGE_BPS['stress'])

    iz = {key(t): t for t in zero}
    ib = {key(t): t for t in base}
    ist = {key(t): t for t in stress}

    rows = []
    for k, t in sorted(ib.items(), key=lambda kv: (kv[1]['entry_time'], kv[1]['symbol'])):
        risk = float(t['risk_pct'])
        fee_R = float(t.get('fee_pct') or 0.0) / risk
        funding_R = float(t.get('funding_pct') or 0.0) / risk
        z = iz.get(k)
        st = ist.get(k)
        relqv = (t.get('features') or {}).get('relative_quote_volume')
        rows.append({
            'symbol': t['symbol'],
            'side': t['side'],
            'episode_key': t.get('episode_key'),
            'entry_time': t['entry_time'],
            'exit_reason': t['exit_reason'],
            'risk_pct': risk,
            'risk_bucket': risk_bucket(risk),
            'relative_quote_volume': relqv,
            'liquidity_bucket': liquidity_bucket(relqv),
            'base_net_R': float(t['net_R']),
            'fee_R': fee_R,
            # funding_pct is subtracted by the engine; positive = cost, negative = credit.
            'funding_R_signed_cost': funding_R,
            'explicit_cost_R': fee_R + funding_R,
            'zero_net_R': float(z['net_R']) if z else None,
            'stress_net_R': float(st['net_R']) if st else None,
            # Full-path sensitivity, not a pure algebraic slippage attribution: slippage may alter target/exit timing.
            'zero_to_base_execution_drag_R': float(z['net_R']) - float(t['net_R']) if z else None,
            'base_to_stress_execution_drag_R': float(t['net_R']) - float(st['net_R']) if st else None,
            'zero_exit_reason': z['exit_reason'] if z else None,
            'stress_exit_reason': st['exit_reason'] if st else None,
        })

    report = {
        'schema_version': 'ktrader.execution_economics.v2_2.diagnostic.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'definitions': {
            'fee_R': 'fee_pct / executed risk_pct',
            'funding_R_signed_cost': 'funding_pct / executed risk_pct; positive is cost, negative is credit',
            'zero_to_base_execution_drag_R': 'matched full-path net_R at 0 bps minus frozen base-slippage net_R',
            'base_to_stress_execution_drag_R': 'frozen base-slippage net_R minus matched 5 bps stress net_R',
            'warning': 'execution drag is full-path sensitivity; slippage can alter entry, target and exit timing, so it is not treated as a purely algebraic cost',
        },
        'base_trade_count': len(base),
        'zero_trade_count': len(zero),
        'stress_trade_count': len(stress),
        'base_matched_zero_count': sum(key(t) in iz for t in base),
        'base_matched_stress_count': sum(key(t) in ist for t in base),
        'zero_only_count': len(set(iz) - set(ib)),
        'stress_only_count': len(set(ist) - set(ib)),
        'overall': summary(rows),
        'by_risk_bucket': grouped(rows, 'risk_bucket'),
        'by_liquidity_bucket': grouped(rows, 'liquidity_bucket'),
        'by_exit_reason': grouped(rows, 'exit_reason'),
        'by_side': grouped(rows, 'side'),
        'rows': rows,
    }

    out = root / 'combined_rules/execution_economics_v2_2'
    out.mkdir(parents=True, exist_ok=True)
    p = out / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in (
        'base_trade_count','zero_trade_count','stress_trade_count','base_matched_zero_count',
        'base_matched_stress_count','zero_only_count','stress_only_count','overall',
        'by_risk_bucket','by_liquidity_bucket','by_exit_reason'
    )}, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__':
    main()
