#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from collections import defaultdict

BASE = pathlib.Path('/data/research/phase11g')


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: pathlib.Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(x) for x in f if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=str(BASE))
    args = ap.parse_args()
    base = pathlib.Path(args.base)
    ledger = base / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger/deduplicated_events.jsonl'
    out_dir = base / 'strategy_benchmark_v1/combined_rules/prospective_level_context_v2'
    out_dir.mkdir(parents=True, exist_ok=True)
    eligible = [r for r in load_jsonl(ledger) if r.get('status') == 'ELIGIBLE_SHADOW_SETUP']
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in eligible:
        groups[r['setup_family_id']].append(r)
    families = []
    for family_id, rows in sorted(groups.items()):
        rows.sort(key=lambda r: (r.get('entry_time') or '', r.get('signal_bar_open_time') or '', r.get('symbol') or '', r.get('side') or ''))
        p = rows[0]
        frozen = p.get('frozen_v2_2_level_features') or {}
        frozen_open = frozen.get('open_space')
        rich_open = p.get('level_v2_h1_open_space')
        rich_next = p.get('level_v2_h1_next_level_R')
        families.append({
            'setup_family_id': family_id,
            'primary_symbol': p.get('symbol'),
            'primary_side': p.get('side'),
            'primary_entry_time': p.get('entry_time'),
            'observation_count': len(rows),
            'clean_break_no_revisit': p.get('clean_break_no_revisit'),
            'frozen_v2_2_open_space': frozen_open,
            'frozen_v2_2_next_level_R': frozen.get('next_confirmed_level_R'),
            'level_context_v2_open_space': rich_open,
            'level_context_v2_next_level_R': rich_next,
            'frozen_vs_level_v2_disagreement': frozen_open is not None and rich_open is not None and frozen_open != rich_open,
            'rich_obstacle_inside_3R': rich_next is not None and float(rich_next) < 3.0,
            'rich_obstacle_inside_1R': rich_next is not None and float(rich_next) < 1.0,
            'floating_zone_flag': p.get('level_v2_h1_floating_zone_flag'),
            'consolidation_present': p.get('level_v2_h1_consolidation_present'),
            'anchor_type': p.get('level_v2_h1_anchor_level_type'),
        })
    report = {
        'schema_version': 'ktrader.prospective_level_context_v2.observation.v1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'diagnostic_only': True,
        'holdout_opened': False,
        'production_action': False,
        'eligible_observation_count': len(eligible),
        'unique_family_count': len(families),
        'primary_clean_break_no_revisit_count': sum(bool(r['clean_break_no_revisit']) for r in families),
        'frozen_vs_level_v2_disagreement_count': sum(bool(r['frozen_vs_level_v2_disagreement']) for r in families),
        'rich_obstacle_inside_3R_count': sum(bool(r['rich_obstacle_inside_3R']) for r in families),
        'rich_obstacle_inside_1R_count': sum(bool(r['rich_obstacle_inside_1R']) for r in families),
        'families': families,
        'interpretation': 'Observation only. No Level Context v2 field changes frozen v2.2 eligibility.',
    }
    p = out_dir / 'report.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p, sha(p))


if __name__ == '__main__':
    main()
