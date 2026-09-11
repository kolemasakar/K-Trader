#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import pathlib
from collections import Counter, defaultdict

BASE = pathlib.Path('/data/research/phase11g')


def stable_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_jsonl(path):
    with path.open() as f: return [json.loads(x) for x in f if x.strip()]


def event_key(r):
    return (r.get('strategy_id'), r.get('symbol'), r.get('side'), r.get('signal_bar_open_time'), r.get('setup_family_id'))


def validate_snapshot(summary: dict) -> tuple[bool, list[str]]:
    reasons = []
    panel_size = int(summary.get('panel_size') or 0)
    missing = summary.get('missing_symbols') or []
    provenance = summary.get('bundle_provenance') or {}
    if panel_size <= 0:
        reasons.append('NON_POSITIVE_PANEL_SIZE')
    if missing:
        reasons.append('MISSING_SYMBOLS')
    if panel_size > 0 and len(provenance) != panel_size:
        reasons.append('BUNDLE_PROVENANCE_COUNT_MISMATCH')
    if not summary.get('frozen_harness_sha256'):
        reasons.append('MISSING_FROZEN_HARNESS_SHA')
    if not summary.get('protocol_sha256'):
        reasons.append('MISSING_PROTOCOL_SHA')
    return not reasons, reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=str(BASE))
    ap.add_argument('--output', default=None)
    args = ap.parse_args()
    base = pathlib.Path(args.base)
    output = pathlib.Path(args.output) if args.output else base / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger'
    output.mkdir(parents=True, exist_ok=True)

    summary_paths = sorted(pathlib.Path(p) for p in glob.glob(str(base / 'v2_2_shadow_*/shadow_v1_1/summary.json')))
    snapshots = []
    rejected_snapshots = []
    events_by_key = {}
    duplicates = 0

    for sp in summary_paths:
        summary = json.loads(sp.read_text())
        valid, reasons = validate_snapshot(summary)
        base_record = {
            'summary_path': str(sp),
            'summary_sha256': hashlib.sha256(sp.read_bytes()).hexdigest(),
            'bundle_set_sha256': summary.get('bundle_set_sha256'),
            'boundary': summary.get('boundary'),
            'panel_size': summary.get('panel_size'),
            'missing_symbols': summary.get('missing_symbols'),
            'bundle_provenance_count': len(summary.get('bundle_provenance') or {}),
            'signal_bars_evaluated_count': summary.get('signal_bars_evaluated_count'),
            'event_count': summary.get('event_count'),
            'eligible_setup_count': summary.get('eligible_setup_count'),
            'frozen_harness_sha256': summary.get('frozen_harness_sha256'),
            'protocol_sha256': summary.get('protocol_sha256'),
        }
        if not valid:
            rejected_snapshots.append({**base_record, 'rejection_reasons': reasons})
            continue

        snapshots.append(base_record)
        ep = sp.parent / 'shadow_events.jsonl'
        events = load_jsonl(ep) if ep.exists() else []
        for r in events:
            k = event_key(r)
            if k in events_by_key:
                duplicates += 1
                old = events_by_key[k]
                if stable_hash(old) != stable_hash(r):
                    r = dict(r)
                    r['ledger_conflict_with_prior_payload'] = True
                events_by_key[k] = r
            else:
                events_by_key[k] = r

    events = sorted(events_by_key.values(), key=lambda r: (r.get('signal_bar_open_time') or '', r.get('symbol') or '', r.get('side') or ''))
    with (output / 'deduplicated_events.jsonl').open('w') as f:
        for r in events: f.write(json.dumps(r, sort_keys=True) + '\n')

    eligible = [r for r in events if r.get('status') == 'ELIGIBLE_SHADOW_SETUP']
    family_groups = defaultdict(list)
    for r in eligible:
        family_groups[r.get('setup_family_id')].append(r)

    status_counts = Counter(r.get('status') for r in events)
    report = {
        'schema_version': 'ktrader.candidate_v2_2.prospective_shadow.ledger.v1_1',
        'strategy_id': 'candidate_rule_set_v2_2',
        'holdout_opened': False,
        'production_action': False,
        'discovered_snapshot_count': len(summary_paths),
        'valid_snapshot_count': len(snapshots),
        'rejected_snapshot_count': len(rejected_snapshots),
        'snapshot_summaries': snapshots,
        'rejected_snapshots': rejected_snapshots,
        'raw_duplicate_event_occurrences': duplicates,
        'deduplicated_event_count': len(events),
        'status_counts': dict(sorted(status_counts.items(), key=lambda kv: str(kv[0]))),
        'eligible_setup_count': len(eligible),
        'unique_eligible_family_count': len(family_groups),
        'eligible_family_sizes': dict(sorted((k, len(v)) for k, v in family_groups.items() if k is not None)),
        'clean_break_no_revisit_eligible_count': sum(bool(r.get('clean_break_no_revisit')) for r in eligible),
        'frozen_harness_sha256_values': sorted({x.get('frozen_harness_sha256') for x in snapshots if x.get('frozen_harness_sha256')}),
        'protocol_sha256_values': sorted({x.get('protocol_sha256') for x in snapshots if x.get('protocol_sha256')}),
        'ledger_event_set_sha256': stable_hash(events),
        'independent_evidence_status': (
            'NO_VALID_SNAPSHOTS' if not snapshots else
            'NO_ELIGIBLE_FAMILIES_YET' if not eligible else
            ('OBSERVATION_ONLY_LT_30_FAMILIES' if len(family_groups) < 30 else
             'DIAGNOSTIC_30_49_FAMILIES' if len(family_groups) < 50 else
             'HYPOTHESIS_ONLY_50_99_FAMILIES' if len(family_groups) < 100 else
             'RECALIBRATION_PROPOSAL_ELIGIBLE_BY_SAMPLE_ONLY')
        ),
    }
    p = output / 'ledger_summary.json'
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', p)


if __name__ == '__main__': main()
