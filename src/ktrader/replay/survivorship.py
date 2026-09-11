from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from decimal import Decimal
import json
from pathlib import Path

from ktrader.replay.harness import canonical_digest
from ktrader.replay.prospective import ProspectiveControlShard, ProspectiveDecisionAudit


PROSPECTIVE_SURVIVORSHIP_SCHEMA_VERSION = "ktrader.prospective_survivorship.v1"

_STAGE_ORDER = (
    "htf_aligned",
    "strong_confirmed_level",
    "geometry_valid",
    "atr_pass",
    "ttl_pass",
    "rr_pass",
    "grade_pass",
    "tradable",
)

_GEOMETRY_REASONS = {
    "MISSING_PRICE_TICK",
    "NO_STRUCTURAL_TARGET",
    "MISSING_CONFIRMATION",
    "INVALID_GEOMETRY",
    "GEOMETRY_UNAVAILABLE",
}


def analyze_prospective_survivorship(
    shards: Sequence[ProspectiveControlShard],
) -> Mapping[str, object]:
    """Measure record-level and distinct-primary-level survivorship.

    The canonical prospective report intentionally counts decision records at
    every cutoff. This diagnostic keeps those record counts but adds a second
    view keyed by ``(canonical_symbol, primary_level_id)`` so repeated M5
    observations of one structural level are not mistaken for independent
    setup evidence.

    This function does not change trading semantics, report schemas, or gate
    thresholds. Its funnel mirrors the canonical prospective-control funnel.
    """

    ordered = _validate_sources(shards)
    cutoffs = tuple(record for shard in ordered for record in shard.cutoffs)
    decisions = tuple(
        decision
        for record in cutoffs
        for slot in record.slots
        if slot.status == "ANALYZED"
        for decision in slot.decisions
    )
    candidates = tuple(decision for decision in decisions if decision.setup_type != "NO_SETUP")
    stages = _funnel_stages(candidates)

    record_funnel = {stage: len(stages[stage]) for stage in _STAGE_ORDER}
    unique_level_funnel = {
        stage: len(_primary_level_keys(stages[stage]))
        for stage in _STAGE_ORDER
    }
    records_without_primary_level = {
        stage: sum(decision.primary_level_id is None for decision in stages[stage])
        for stage in _STAGE_ORDER
    }
    records_by_symbol = {
        stage: dict(sorted(Counter(decision.canonical_symbol for decision in stages[stage]).items()))
        for stage in _STAGE_ORDER
    }
    late_stage_repeated_levels = {
        stage: _repeated_level_rows(stages[stage])
        for stage in (
            "geometry_valid",
            "atr_pass",
            "ttl_pass",
            "rr_pass",
            "grade_pass",
            "tradable",
        )
    }

    windows = sorted(
        {
            (
                shard.start.isoformat(),
                shard.end.isoformat(),
                shard.archive_sha256,
            )
            for shard in ordered
        }
    )

    fields: dict[str, object] = {
        "schema_version": PROSPECTIVE_SURVIVORSHIP_SCHEMA_VERSION,
        "provider_id": ordered[0].provider_id,
        "scanner_config_sha256": ordered[0].scanner_config_sha256,
        "cutoff_interval_seconds": ordered[0].cutoff_interval_seconds,
        "analysis_limit": ordered[0].analysis_limit,
        "max_context_age_seconds": ordered[0].max_context_age_seconds,
        "source_shard_sha256": tuple(shard.shard_sha256 for shard in ordered),
        "source_windows": tuple(
            {
                "start": start,
                "end": end,
                "archive_sha256": archive_sha256,
            }
            for start, end, archive_sha256 in windows
        ),
        "logical_cutoffs": len(cutoffs),
        "decision_records": len(decisions),
        "candidate_records": len(candidates),
        "record_funnel": record_funnel,
        "unique_primary_level_funnel": unique_level_funnel,
        "records_without_primary_level": records_without_primary_level,
        "records_by_symbol": records_by_symbol,
        "late_stage_repeated_levels": late_stage_repeated_levels,
        "identity_definition": "(canonical_symbol, primary_level_id)",
        "interpretation": (
            "Distinct-primary-level counts are a dependency diagnostic, not a "
            "replacement for the canonical record funnel and not a trading gate."
        ),
    }
    return {
        **fields,
        "analysis_sha256": canonical_digest(fields),
    }


def write_prospective_survivorship_report(
    path: str | Path,
    report: Mapping[str, object],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
    return target


def _validate_sources(
    shards: Sequence[ProspectiveControlShard],
) -> tuple[ProspectiveControlShard, ...]:
    if not shards:
        raise ValueError("at least one prospective-control shard is required")

    ordered = tuple(
        sorted(
            shards,
            key=lambda shard: (
                shard.start,
                shard.end,
                shard.shard_index,
                shard.shard_sha256,
            ),
        )
    )
    first = ordered[0]
    for shard in ordered:
        if not shard.complete:
            raise ValueError("survivorship analysis requires complete shards")
        if (
            shard.provider_id != first.provider_id
            or shard.scanner_config_sha256 != first.scanner_config_sha256
            or shard.cutoff_interval_seconds != first.cutoff_interval_seconds
            or shard.analysis_limit != first.analysis_limit
            or shard.max_context_age_seconds != first.max_context_age_seconds
        ):
            raise ValueError("survivorship shard configuration mismatch")

    cutoffs = [record.cutoff for shard in ordered for record in shard.cutoffs]
    if len(cutoffs) != len(set(cutoffs)):
        raise ValueError("survivorship source shards contain overlapping cutoffs")
    return ordered


def _funnel_stages(
    candidates: Sequence[ProspectiveDecisionAudit],
) -> Mapping[str, tuple[ProspectiveDecisionAudit, ...]]:
    htf = tuple(
        decision
        for decision in candidates
        if "HTF_CONTEXT_MISMATCH" not in decision.reason_codes
    )
    strong = tuple(
        decision
        for decision in htf
        if "PRIMARY_LEVEL_NOT_STRONG" not in decision.reason_codes
        and "PRIMARY_LEVEL_NOT_CONFIRMED" not in decision.reason_codes
        and decision.primary_level_strength == "STRONG"
    )
    geometry = tuple(
        decision
        for decision in strong
        if decision.rr is not None
        and not _GEOMETRY_REASONS.intersection(decision.reason_codes)
    )
    atr_pass = tuple(
        decision
        for decision in geometry
        if decision.atr_used_pct is not None
        and decision.atr_used_pct <= Decimal("80")
        and "ATR_USED_OVER_80" not in decision.reason_codes
    )
    ttl_pass = tuple(
        decision
        for decision in atr_pass
        if "SETUP_EXPIRED" not in decision.reason_codes
    )
    rr_pass = tuple(
        decision
        for decision in ttl_pass
        if decision.rr is not None and decision.rr >= Decimal("3")
    )
    grade_pass = tuple(
        decision for decision in rr_pass if decision.grade in {"A", "A+"}
    )
    tradable = tuple(
        decision for decision in grade_pass if decision.side in {"LONG", "SHORT"}
    )
    return {
        "htf_aligned": htf,
        "strong_confirmed_level": strong,
        "geometry_valid": geometry,
        "atr_pass": atr_pass,
        "ttl_pass": ttl_pass,
        "rr_pass": rr_pass,
        "grade_pass": grade_pass,
        "tradable": tradable,
    }


def _primary_level_keys(
    decisions: Sequence[ProspectiveDecisionAudit],
) -> set[tuple[str, str]]:
    return {
        (decision.canonical_symbol, decision.primary_level_id)
        for decision in decisions
        if decision.primary_level_id is not None
    }


def _repeated_level_rows(
    decisions: Sequence[ProspectiveDecisionAudit],
) -> tuple[Mapping[str, object], ...]:
    counts = Counter(
        (decision.canonical_symbol, decision.primary_level_id)
        for decision in decisions
        if decision.primary_level_id is not None
    )
    rows = [
        {
            "canonical_symbol": symbol,
            "primary_level_id": level_id,
            "record_count": count,
        }
        for (symbol, level_id), count in counts.items()
        if count > 1
    ]
    rows.sort(
        key=lambda row: (
            -int(row["record_count"]),
            str(row["canonical_symbol"]),
            str(row["primary_level_id"]),
        )
    )
    return tuple(rows[:20])
