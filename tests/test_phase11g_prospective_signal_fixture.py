from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ktrader.replay import (
    PROSPECTIVE_CONTROL_SHARD_SCHEMA_VERSION,
    ProspectiveControlShard,
    ProspectiveCutoffRecord,
    ProspectiveDecisionAudit,
    ProspectiveSlotRecord,
    canonical_digest,
    merge_prospective_control_shards,
)


UTC = timezone.utc


def test_synthetic_tradable_signal_fixture_reaches_report_without_probability_or_outcome():
    cutoff = datetime(2026, 9, 11, 12, 0, tzinfo=UTC)
    decision = ProspectiveDecisionAudit(
        decision_id="decision-1",
        canonical_symbol="SUIUSDT",
        signal_key="signal-1",
        side="LONG",
        grade="A",
        setup_score=85,
        raw_score=85,
        setup_type="TRAP_LEVEL_CONFIRMATION",
        primary_level_id="level-1",
        primary_level_strength="STRONG",
        rr=Decimal("3.5"),
        atr_used_pct=Decimal("40"),
        entry=Decimal("100"),
        stop=Decimal("99"),
        target=Decimal("103.5"),
        last_closed_bar=cutoff - timedelta(milliseconds=1),
        generated_at=cutoff,
        reason_codes=(),
    )
    slot = ProspectiveSlotRecord(
        symbol="SUIUSDT",
        liquidity_rank=1,
        universe_size=20,
        status="ANALYZED",
        detail=None,
        decisions=(decision,),
    )
    cutoff_record = ProspectiveCutoffRecord(
        cutoff=cutoff,
        context_status="SELECTED",
        context_detail=None,
        snapshot_captured_at=cutoff - timedelta(seconds=30),
        snapshot_sha256="a" * 64,
        snapshot_age_seconds=30.0,
        slots=(slot,),
    )
    fields = {
        "schema_version": PROSPECTIVE_CONTROL_SHARD_SCHEMA_VERSION,
        "provider_id": "binance_usdm",
        "archive_sha256": "b" * 64,
        "scanner_config_sha256": "c" * 64,
        "start": cutoff,
        "end": cutoff,
        "cutoff_interval_seconds": 300,
        "analysis_limit": 20,
        "max_context_age_seconds": 300.0,
        "shard_index": 0,
        "shard_count": 1,
        "expected_cutoff_count": 1,
        "bundle_sha256_by_symbol": {"SUIUSDT": "d" * 64},
        "cutoffs": (cutoff_record,),
        "complete": True,
    }
    shard = ProspectiveControlShard(
        **fields,
        shard_sha256=canonical_digest(fields),
    )

    report = merge_prospective_control_shards((shard,))

    assert report.funnel == {
        "htf_aligned": 1,
        "strong_confirmed_level": 1,
        "geometry_valid": 1,
        "atr_pass": 1,
        "ttl_pass": 1,
        "rr_pass": 1,
        "grade_pass": 1,
        "tradable": 1,
    }
    assert report.unique_tradable_signal_count == 1
    assert len(report.tradable_records) == 1
    record = report.tradable_records[0]
    assert record["canonical_symbol"] == "SUIUSDT"
    assert record["signal_key"] == "signal-1"
    assert "estimated_probability" not in record
    assert "outcome" not in record
