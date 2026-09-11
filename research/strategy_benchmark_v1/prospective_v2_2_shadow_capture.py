#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import pathlib
from datetime import datetime

DEFAULT_RESEARCH_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
DEFAULT_HARNESS = DEFAULT_RESEARCH_ROOT / 'harness/candidate_v2_2_backtest.py'
DEFAULT_BOUNDARY = '2026-09-11T20:00:00Z'
HERE = pathlib.Path(__file__).resolve().parent


def load_module(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def ts(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def stable_hash(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bundle-root', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--research-root', default=str(DEFAULT_RESEARCH_ROOT))
    ap.add_argument('--harness', default=str(DEFAULT_HARNESS))
    ap.add_argument('--boundary', default=DEFAULT_BOUNDARY)
    args = ap.parse_args()

    root = pathlib.Path(args.research_root)
    bundle_root = pathlib.Path(args.bundle_root)
    output = pathlib.Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    boundary = ts(args.boundary)
    harness_path = pathlib.Path(args.harness)

    frozen = load_module('candidate_v2_2_frozen', harness_path)
    v21 = frozen.v
    b = frozen.b
    lc = load_module('level_context_v2', HERE / 'level_context_v2_features.py')
    lc21 = load_module('level_context_v2_1', HERE / 'level_context_v2_1_diagnostics.py')
    traversal = load_module('level_context_v2_2_traversal', HERE / 'level_context_v2_2_traversal.py')

    protocol_path = root / 'protocol.json'
    protocol = json.loads(protocol_path.read_text())
    panel = protocol['primary_panel']['symbols']
    rows = []
    missing = []
    bundle_provenance = {}
    signal_bars_evaluated_by_symbol = {}
    evaluated_signal_open_times = []

    for symbol in panel:
        sdir = bundle_root / symbol
        m15p = sdir / '15m.jsonl'
        h1p = sdir / '1h.jsonl'
        bundlep = sdir / 'bundle.json'
        if not (m15p.exists() and h1p.exists() and bundlep.exists()):
            missing.append(symbol)
            signal_bars_evaluated_by_symbol[symbol] = 0
            continue

        bundle_meta = json.loads(bundlep.read_text())
        bundle_provenance[symbol] = {
            'as_of': bundle_meta.get('as_of'),
            'bundle_sha256': bundle_meta.get('bundle_sha256'),
            'provider_id': bundle_meta.get('provider_id'),
            'candle_counts': bundle_meta.get('candle_counts'),
        }
        m15 = b.load_bars(m15p)
        h1 = b.load_bars(h1p)
        mx = b.indicators(m15)
        hx = b.indicators(h1)
        h1cts = [x['close_dt'] for x in h1]
        symbol_evaluated = 0

        # len(m15)-1 is intentional: a signal bar is evaluated only when the
        # next closed M15 bar exists, so the frozen next-open entry price is
        # available causally inside this captured bundle.
        for i in range(max(53, b.PULLBACK_WINDOW), len(m15) - 1):
            bar = m15[i]
            if bar['open_dt'] < boundary:
                continue
            symbol_evaluated += 1
            evaluated_signal_open_times.append(bar['open_time'])
            signal = v21.signal_at(i, m15, mx, h1, hx, h1cts)
            if signal is None:
                continue

            side = signal['side']
            next_bar = m15[i + 1]
            entry = b.adverse(next_bar['open'], side, True, b.SLIPPAGE_BPS['base'])
            stop = signal['stop_raw']
            dist = side * (entry - stop)
            risk_pct = dist / entry if entry > 0 else 0.0
            features = dict(signal['features'])
            pull_i = int(features['pullback_episode_index'])
            pullback_time = m15[pull_i]['open_time'] if 0 <= pull_i < len(m15) else None

            family_payload = {
                'strategy_id': 'candidate_rule_set_v2_2',
                'symbol': symbol,
                'side': 'LONG' if side == 1 else 'SHORT',
                'pullback_episode_open_time': pullback_time,
            }

            row = {
                'schema_version': 'ktrader.candidate_v2_2.prospective_shadow.v1',
                'strategy_id': 'candidate_rule_set_v2_2',
                'holdout_opened': False,
                'production_action': False,
                'symbol': symbol,
                'side': family_payload['side'],
                'signal_bar_open_time': bar['open_time'],
                'signal_bar_close_time': bar['close_time'],
                'entry_time': next_bar['open_time'],
                'entry_price': entry,
                'stop_price': stop,
                'risk_pct': risk_pct,
                'episode_key_legacy': signal['episode_key'],
                'pullback_episode_open_time': pullback_time,
                'setup_family_id': stable_hash(family_payload),
                'frozen_features': features,
                'bundle_as_of': bundle_meta.get('as_of'),
                'bundle_sha256': bundle_meta.get('bundle_sha256'),
                'provider_id': bundle_meta.get('provider_id'),
                'status': None,
            }

            if dist <= 0 or risk_pct < v21.MIN_RISK_PCT:
                row['status'] = 'REJECT_MIN_RISK_DISTANCE'
                rows.append(row)
                continue

            decision_idx = int(features['h1_index'])
            frozen_level = frozen.level_features(h1, hx, decision_idx, entry, stop, side)
            row['frozen_v2_2_level_features'] = frozen_level
            if frozen_level is None:
                row['status'] = 'REJECT_LEVEL_CONTEXT_UNAVAILABLE'
                rows.append(row)
                continue
            if not frozen_level['structural_space_gate_pass']:
                row['status'] = 'REJECT_STRUCTURAL_SPACE'
            else:
                row['status'] = 'ELIGIBLE_SHADOW_SETUP'

            signal_dt = bar['close_dt']
            h1_context = lc.timeframe_context(h1, signal_dt, entry, stop, side, lc.H1_LOOKBACK, 'h1')
            row.update({f'level_v2_{k}': val for k, val in h1_context.items()})
            strict = lc21.strict_level_break_features(h1, signal_dt, entry, stop, side)
            row.update(strict)

            traversal_input = {
                **row,
                'h1_decision_index': h1_context.get('h1_decision_index'),
                'h1_atr14': h1_context.get('h1_atr14'),
            }
            if strict.get('strict_break_present') and h1_context.get('h1_available'):
                trav = traversal.traversal_features(traversal_input, h1)
            else:
                trav = {'traversal_available': False}
            row.update(trav)
            row['clean_break_no_revisit'] = bool(
                row.get('status') == 'ELIGIBLE_SHADOW_SETUP'
                and trav.get('traversal_available')
                and trav.get('revisit_episode_count') == 0
            )
            rows.append(row)

        signal_bars_evaluated_by_symbol[symbol] = symbol_evaluated

    rows.sort(key=lambda r: (r['signal_bar_open_time'], r['symbol'], r['side']))
    with (output / 'shadow_events.jsonl').open('w') as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + '\n')

    counts = collections.Counter(r['status'] for r in rows)
    eligible = [r for r in rows if r['status'] == 'ELIGIBLE_SHADOW_SETUP']
    summary = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_shadow.summary.v1_1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'boundary': args.boundary,
        'holdout_opened': False,
        'production_action': False,
        'panel_size': len(panel),
        'missing_symbols': missing,
        'bundle_root': str(bundle_root),
        'bundle_provenance': dict(sorted(bundle_provenance.items())),
        'bundle_set_sha256': stable_hash(bundle_provenance),
        'frozen_harness_path': str(harness_path),
        'frozen_harness_sha256': sha_file(harness_path),
        'protocol_sha256': sha_file(protocol_path),
        'signal_bars_evaluated_count': sum(signal_bars_evaluated_by_symbol.values()),
        'signal_bars_evaluated_by_symbol': dict(sorted(signal_bars_evaluated_by_symbol.items())),
        'earliest_signal_bar_open_time': min(evaluated_signal_open_times) if evaluated_signal_open_times else None,
        'latest_signal_bar_open_time': max(evaluated_signal_open_times) if evaluated_signal_open_times else None,
        'event_count': len(rows),
        'status_counts': dict(sorted(counts.items())),
        'eligible_setup_count': len(eligible),
        'unique_eligible_family_count': len({r['setup_family_id'] for r in eligible}),
        'clean_break_no_revisit_eligible_count': sum(r.get('clean_break_no_revisit', False) for r in eligible),
    }
    p = output / 'summary.json'
    p.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=2, sort_keys=True))
    print('SUMMARY', p)


if __name__ == '__main__':
    main()
