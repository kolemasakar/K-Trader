from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from ktrader.replay.prospective import (
    ProspectiveControlShard,
    ProspectiveCutoffRecord,
    ProspectiveDecisionAudit,
    ProspectiveSlotRecord,
)
from ktrader.replay.survivorship import analyze_prospective_survivorship


UTC = timezone.utc
START = datetime(2026, 1, 2, 0, 5, tzinfo=UTC)
END = START + timedelta(minutes=5)


def _decision(
    *,
    decision_id: str,
    generated_at: datetime,
    level_id: str,
    rr: str,
    atr_used_pct: str,
    reasons: tuple[str, ...],
    grade: str = "C",
    side: str = "NO_TRADE",
    signal_key: str | None = None,
) -> ProspectiveDecisionAudit:
    return ProspectiveDecisionAudit(
        decision_id=decision_id,
        canonical_symbol="SUIUSDT",
        signal_key=signal_key,
        side=side,
        grade=grade,
        setup_score=69 if grade == "C" else 90,
        raw_score=75 if grade == "C" else 92,
        setup_type="TRAP_LEVEL_CONFIRMATION",
        primary_level_id=level_id,
        primary_level_strength="STRONG",
        rr=Decimal(rr),
        atr_used_pct=Decimal(atr_used_pct),
        entry=None,
        stop=None,
        target=None,
        last_closed_bar=generated_at - timedelta(seconds=1),
        generated_at=generated_at,
        reason_codes=reasons,
    )


def _shard() -> ProspectiveControlShard:
    repeated_one = _decision(
        decision_id="d1",
        generated_at=START,
        level_id="level-1",
        rr="2",
        atr_used_pct="20",
        reasons=("RR_BELOW_3",),
    )
    repeated_two = _decision(
        decision_id="d2",
        generated_at=END,
        level_id="level-1",
        rr="2",
        atr_used_pct="20",
        reasons=("RR_BELOW_3",),
    )
    rr3_but_atr_fail = _decision(
        decision_id="d3",
        generated_at=START,
        level_id="level-2",
        rr="3.2",
        atr_used_pct="150",
        reasons=("ATR_USED_OVER_80",),
    )
    tradable = _decision(
        decision_id="d4",
        generated_at=END,
        level_id="level-3",
        rr="3.5",
        atr_used_pct="20",
        reasons=(),
        grade="A",
        side="LONG",
        signal_key="signal-1",
    )

    cutoffs = (
        ProspectiveCutoffRecord(
            cutoff=START,
            context_status="SELECTED",
            context_detail=None,
            snapshot_captured_at=START - timedelta(seconds=30),
            snapshot_sha256="snapshot-1",
            snapshot_age_seconds=30.0,
            slots=(
                ProspectiveSlotRecord(
                    symbol="SUIUSDT",
                    liquidity_rank=1,
                    universe_size=1,
                    status="ANALYZED",
                    detail=None,
                    decisions=(repeated_one, rr3_but_atr_fail),
                ),
            ),
        ),
        ProspectiveCutoffRecord(
            cutoff=END,
            context_status="SELECTED",
            context_detail=None,
            snapshot_captured_at=END - timedelta(seconds=30),
            snapshot_sha256="snapshot-2",
            snapshot_age_seconds=30.0,
            slots=(
                ProspectiveSlotRecord(
                    symbol="SUIUSDT",
                    liquidity_rank=1,
                    universe_size=1,
                    status="ANALYZED",
                    detail=None,
                    decisions=(repeated_two, tradable),
                ),
            ),
        ),
    )
    return ProspectiveControlShard(
        schema_version="ktrader.prospective_control_shard.v1",
        provider_id="binance_usdm",
        archive_sha256="archive-1",
        scanner_config_sha256="scanner-1",
        start=START,
        end=END,
        cutoff_interval_seconds=300,
        analysis_limit=20,
        max_context_age_seconds=300.0,
        shard_index=0,
        shard_count=1,
        expected_cutoff_count=2,
        bundle_sha256_by_symbol={"SUIUSDT": "bundle-1"},
        cutoffs=cutoffs,
        complete=True,
        shard_sha256="shard-1",
    )


def test_survivorship_separates_record_counts_from_unique_primary_levels():
    report = analyze_prospective_survivorship((_shard(),))

    assert report["record_funnel"] == {
        "htf_aligned": 4,
        "strong_confirmed_level": 4,
        "geometry_valid": 4,
        "atr_pass": 3,
        "ttl_pass": 3,
        "rr_pass": 1,
        "grade_pass": 1,
        "tradable": 1,
    }
    assert report["unique_primary_level_funnel"] == {
        "htf_aligned": 3,
        "strong_confirmed_level": 3,
        "geometry_valid": 3,
        "atr_pass": 2,
        "ttl_pass": 2,
        "rr_pass": 1,
        "grade_pass": 1,
        "tradable": 1,
    }
    repeated = report["late_stage_repeated_levels"]["geometry_valid"]
    assert repeated == (
        {
            "canonical_symbol": "SUIUSDT",
            "primary_level_id": "level-1",
            "record_count": 2,
        },
    )
    assert report["records_without_primary_level"] == {
        stage: 0 for stage in report["record_funnel"]
    }
    assert isinstance(report["analysis_sha256"], str)
    assert len(report["analysis_sha256"]) == 64


def test_survivorship_rejects_overlapping_cutoffs():
    shard = _shard()
    with pytest.raises(ValueError, match="overlapping cutoffs"):
        analyze_prospective_survivorship((shard, shard))
