from __future__ import annotations

import json
import pathlib
import subprocess
import sys


def write_snapshot(root: pathlib.Path, stamp: str, event: dict) -> None:
    shadow = root / f'v2_2_shadow_{stamp}' / 'shadow_v1_1'
    shadow.mkdir(parents=True)
    summary = {
        'panel_size': 1,
        'missing_symbols': [],
        'bundle_provenance': {'VTHOUSDT': {'bundle_sha256': stamp}},
        'frozen_harness_sha256': 'harness',
        'protocol_sha256': 'protocol',
        'signal_bars_evaluated_count': 1,
        'event_count': 1,
        'eligible_setup_count': 1,
        'boundary': '2026-09-11T20:00:00Z',
        'bundle_set_sha256': stamp,
    }
    (shadow / 'summary.json').write_text(json.dumps(summary))
    (shadow / 'shadow_events.jsonl').write_text(json.dumps(event) + '\n')


def test_first_seen_payload_is_immutable(tmp_path: pathlib.Path) -> None:
    event = {
        'strategy_id': 'candidate_rule_set_v2_2',
        'symbol': 'VTHOUSDT',
        'side': 'LONG',
        'signal_bar_open_time': '2026-09-13T07:45:00Z',
        'setup_family_id': 'family-1',
        'status': 'ELIGIBLE_SHADOW_SETUP',
        'entry_price': 0.00089887974,
        'stop_price': 0.0008404414667906131,
        'clean_break_no_revisit': False,
    }
    later = dict(event)
    later['stop_price'] = 0.0008404501882895961

    write_snapshot(tmp_path, '20260916T100000Z', event)
    write_snapshot(tmp_path, '20260916T190000Z', later)

    script = pathlib.Path(__file__).resolve().parents[1] / 'prospective_v2_2_shadow_ledger_v1_2.py'
    output = tmp_path / 'ledger'
    subprocess.run(
        [sys.executable, str(script), '--base', str(tmp_path), '--output', str(output)],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [json.loads(line) for line in (output / 'deduplicated_events.jsonl').read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]['stop_price'] == event['stop_price']
    assert 'ledger_conflict_with_prior_payload' not in rows[0]

    report = json.loads((output / 'ledger_summary.json').read_text())
    assert report['schema_version'] == 'ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2'
    assert report['first_seen_payload_immutable'] is True
    assert report['raw_duplicate_event_occurrences'] == 1
    assert report['conflicting_duplicate_event_occurrences'] == 1
    assert report['conflicting_event_key_count'] == 1
    assert report['deduplicated_event_count'] == 1
    assert report['eligible_setup_count'] == 1
    assert report['unique_eligible_family_count'] == 1
