from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path

from ktrader.engine.models import TradingDecision
from ktrader.history.bundle import MTFReplayBundle, slice_datasets_asof
from ktrader.history.universe import UniverseSnapshot, UniverseSnapshotArchive
from ktrader.market.universe import UniverseCandidate
from ktrader.outcomes.evaluator import decision_fingerprint
from ktrader.replay.harness import canonical_digest
from ktrader.replay.provenance import scanner_config_sha256
from ktrader.replay.study import stable_signal_key
from ktrader.runtime.analyzer import analyze_candle_snapshot
from ktrader.runtime.models import RuntimeScannerConfig, setup_interval_seconds


PROSPECTIVE_CONTROL_SHARD_SCHEMA_VERSION = "ktrader.prospective_control_shard.v1"
PROSPECTIVE_CONTROL_REPORT_SCHEMA_VERSION = "ktrader.prospective_control_report.v1"
UTC_DAY_5M_EMPTY_ERROR = "ValueError: 5m day sequence is empty"


@dataclass(frozen=True, slots=True)
class ProspectiveDecisionAudit:
    decision_id: str
    signal_key: str | None
    side: str
    grade: str
    setup_score: int
    raw_score: int
    setup_type: str
    primary_level_id: str | None
    primary_level_strength: str | None
    rr: Decimal | None
    atr_used_pct: Decimal | None
    entry: Decimal | None
    stop: Decimal | None
    target: Decimal | None
    last_closed_bar: datetime
    generated_at: datetime
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProspectiveSlotRecord:
    symbol: str
    liquidity_rank: int
    universe_size: int
    status: str
    detail: str | None
    decisions: tuple[ProspectiveDecisionAudit, ...]


@dataclass(frozen=True, slots=True)
class ProspectiveCutoffRecord:
    cutoff: datetime
    context_status: str
    context_detail: str | None
    snapshot_captured_at: datetime | None
    snapshot_sha256: str | None
    snapshot_age_seconds: float | None
    slots: tuple[ProspectiveSlotRecord, ...]


@dataclass(frozen=True, slots=True)
class ProspectiveControlShard:
    schema_version: str
    provider_id: str
    archive_sha256: str
    scanner_config_sha256: str
    start: datetime
    end: datetime
    cutoff_interval_seconds: int
    analysis_limit: int
    max_context_age_seconds: float
    shard_index: int
    shard_count: int
    expected_cutoff_count: int
    bundle_sha256_by_symbol: Mapping[str, str]
    cutoffs: tuple[ProspectiveCutoffRecord, ...]
    complete: bool
    shard_sha256: str


@dataclass(frozen=True, slots=True)
class ProspectiveControlReport:
    schema_version: str
    provider_id: str
    start: datetime
    end: datetime
    cutoff_interval_seconds: int
    analysis_limit: int
    max_context_age_seconds: float
    archive_sha256: str
    scanner_config_sha256: str
    bundle_sha256_by_symbol: Mapping[str, str]
    logical_cutoffs: int
    selected_context_cutoffs: int
    missing_context_cutoffs: tuple[datetime, ...]
    stale_context_cutoffs: tuple[datetime, ...]
    context_age_seconds: Mapping[str, float | None]
    symbol_slots: int
    history_pass_slots: int
    history_fail_slots: int
    analysis_error_slots: int
    decision_records: int
    best_side_counts: Mapping[str, int]
    candidate_records_by_symbol: Mapping[str, int]
    history_fail_by_symbol: Mapping[str, int]
    analysis_errors: Mapping[str, int]
    reason_counts: Mapping[str, int]
    setup_type_counts: Mapping[str, int]
    funnel: Mapping[str, int]
    funnel_pct_of_htf: Mapping[str, float]
    tradable_records: tuple[Mapping[str, object], ...]
    rr3_nontradable: tuple[Mapping[str, object], ...]
    near_miss: tuple[Mapping[str, object], ...]
    unique_tradable_signal_count: int
    report_sha256: str


AnalysisFunction = Callable[..., Sequence[TradingDecision]]
CheckpointFunction = Callable[[ProspectiveControlShard], None]


def logical_cutoffs(
    start: datetime,
    end: datetime,
    *,
    interval_seconds: int,
) -> tuple[datetime, ...]:
    _require_utc(start, "start")
    _require_utc(end, "end")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    if end < start:
        raise ValueError("end must not be before start")
    if not _aligned(start, interval_seconds) or not _aligned(end, interval_seconds):
        raise ValueError("prospective control bounds must align to the cutoff interval")
    values: list[datetime] = []
    current = start
    step = timedelta(seconds=interval_seconds)
    while current <= end:
        values.append(current)
        current += step
    return tuple(values)


def select_recorded_snapshot(
    archive: UniverseSnapshotArchive,
    cutoff: datetime,
    *,
    max_context_age_seconds: float,
) -> tuple[str, UniverseSnapshot | None, float | None]:
    _require_utc(cutoff, "cutoff")
    if max_context_age_seconds <= 0:
        raise ValueError("max_context_age_seconds must be positive")
    selected: UniverseSnapshot | None = None
    for snapshot in archive.snapshots:
        if snapshot.captured_at > cutoff:
            break
        selected = snapshot
    if selected is None:
        return "MISSING", None, None
    age = (cutoff - selected.captured_at).total_seconds()
    if age > max_context_age_seconds:
        return "STALE", selected, age
    return "SELECTED", selected, age


def current_utc_day_5m_available(
    candles_by_interval: Mapping[str, Sequence[object]],
    *,
    cutoff: datetime,
) -> bool:
    _require_utc(cutoff, "cutoff")
    day_start = cutoff.astimezone(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    for candle in candles_by_interval.get("5m", ()):
        open_time = getattr(candle, "open_time", None)
        if not isinstance(open_time, datetime):
            continue
        if open_time >= day_start and open_time.astimezone(timezone.utc).date() == day_start.date():
            return True
    return False


def run_prospective_control_shard(
    archive: UniverseSnapshotArchive,
    bundles: Mapping[str, MTFReplayBundle],
    *,
    scanner_config: RuntimeScannerConfig | None = None,
    start: datetime,
    end: datetime,
    analysis_limit: int = 20,
    max_context_age_seconds: float = 300.0,
    shard_index: int = 0,
    shard_count: int = 1,
    resume: ProspectiveControlShard | None = None,
    max_new_cutoffs: int | None = None,
    analysis_function: AnalysisFunction = analyze_candle_snapshot,
    checkpoint_function: CheckpointFunction | None = None,
    checkpoint_every: int = 1,
) -> ProspectiveControlShard:
    scanner = scanner_config or RuntimeScannerConfig()
    if analysis_limit <= 0:
        raise ValueError("analysis_limit must be positive")
    if max_context_age_seconds <= 0:
        raise ValueError("max_context_age_seconds must be positive")
    if shard_count <= 0 or shard_index < 0 or shard_index >= shard_count:
        raise ValueError("invalid shard index/count")
    if max_new_cutoffs is not None and max_new_cutoffs <= 0:
        raise ValueError("max_new_cutoffs must be positive when configured")
    if checkpoint_every <= 0:
        raise ValueError("checkpoint_every must be positive")

    interval_seconds = setup_interval_seconds(scanner.setup_interval)
    full_cutoffs = logical_cutoffs(start, end, interval_seconds=interval_seconds)
    assigned = tuple(
        cutoff
        for index, cutoff in enumerate(full_cutoffs)
        if index % shard_count == shard_index
    )
    required_symbols = _selected_symbols_for_window(
        archive,
        full_cutoffs,
        analysis_limit=analysis_limit,
        max_context_age_seconds=max_context_age_seconds,
    )
    bundle_digests = _validate_inputs(
        archive,
        bundles,
        end=end,
        required_symbols=required_symbols,
    )
    config_digest = scanner_config_sha256(scanner)

    existing: dict[datetime, ProspectiveCutoffRecord] = {}
    if resume is not None:
        _validate_resume(
            resume,
            archive=archive,
            bundle_digests=bundle_digests,
            scanner_config_sha256_value=config_digest,
            start=start,
            end=end,
            interval_seconds=interval_seconds,
            analysis_limit=analysis_limit,
            max_context_age_seconds=max_context_age_seconds,
            shard_index=shard_index,
            shard_count=shard_count,
            assigned=assigned,
        )
        existing = {record.cutoff: record for record in resume.cutoffs}

    processed_new = 0
    for cutoff in assigned:
        if cutoff in existing:
            continue
        existing[cutoff] = _run_cutoff(
            archive,
            bundles,
            scanner=scanner,
            cutoff=cutoff,
            analysis_limit=analysis_limit,
            max_context_age_seconds=max_context_age_seconds,
            analysis_function=analysis_function,
        )
        processed_new += 1
        current = _build_shard(
            archive=archive,
            bundle_digests=bundle_digests,
            scanner_config_sha256_value=config_digest,
            start=start,
            end=end,
            interval_seconds=interval_seconds,
            analysis_limit=analysis_limit,
            max_context_age_seconds=max_context_age_seconds,
            shard_index=shard_index,
            shard_count=shard_count,
            assigned=assigned,
            records=existing,
        )
        if checkpoint_function is not None and processed_new % checkpoint_every == 0:
            checkpoint_function(current)
        if max_new_cutoffs is not None and processed_new >= max_new_cutoffs:
            return current

    return _build_shard(
        archive=archive,
        bundle_digests=bundle_digests,
        scanner_config_sha256_value=config_digest,
        start=start,
        end=end,
        interval_seconds=interval_seconds,
        analysis_limit=analysis_limit,
        max_context_age_seconds=max_context_age_seconds,
        shard_index=shard_index,
        shard_count=shard_count,
        assigned=assigned,
        records=existing,
    )


def merge_prospective_control_shards(
    shards: Sequence[ProspectiveControlShard],
) -> ProspectiveControlReport:
    if not shards:
        raise ValueError("at least one prospective-control shard is required")
    ordered = tuple(sorted(shards, key=lambda item: item.shard_index))
    first = ordered[0]
    expected_indices = tuple(range(first.shard_count))
    actual_indices = tuple(item.shard_index for item in ordered)
    if actual_indices != expected_indices:
        raise ValueError("prospective-control shards must cover every shard index exactly once")
    for shard in ordered:
        _validate_shard_digest(shard)
        if not shard.complete:
            raise ValueError("cannot merge incomplete prospective-control shard")
        _require_same_provenance(first, shard)

    records = tuple(
        sorted(
            (record for shard in ordered for record in shard.cutoffs),
            key=lambda item: item.cutoff,
        )
    )
    expected = logical_cutoffs(
        first.start,
        first.end,
        interval_seconds=first.cutoff_interval_seconds,
    )
    if tuple(record.cutoff for record in records) != expected:
        raise ValueError("merged prospective-control cutoffs do not match the full logical window")
    return _aggregate_report(first, records)


def write_prospective_control_shard(
    path: str | Path,
    shard: ProspectiveControlShard,
) -> Path:
    _validate_shard_digest(shard)
    return _atomic_write_json(Path(path), _shard_payload(shard, include_digest=True))


def load_prospective_control_shard(path: str | Path) -> ProspectiveControlShard:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    shard = _deserialize_shard(payload)
    _validate_shard_digest(shard)
    return shard


def write_prospective_control_report(
    path: str | Path,
    report: ProspectiveControlReport,
) -> Path:
    _validate_report_digest(report)
    return _atomic_write_json(Path(path), _report_payload(report, include_digest=True))


def load_prospective_control_report(path: str | Path) -> ProspectiveControlReport:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    report = _deserialize_report(payload)
    _validate_report_digest(report)
    return report


def _run_cutoff(
    archive: UniverseSnapshotArchive,
    bundles: Mapping[str, MTFReplayBundle],
    *,
    scanner: RuntimeScannerConfig,
    cutoff: datetime,
    analysis_limit: int,
    max_context_age_seconds: float,
    analysis_function: AnalysisFunction,
) -> ProspectiveCutoffRecord:
    status, snapshot, age = select_recorded_snapshot(
        archive,
        cutoff,
        max_context_age_seconds=max_context_age_seconds,
    )
    if status != "SELECTED":
        detail = (
            "no recorded universe snapshot at/before cutoff"
            if status == "MISSING"
            else "newest recorded universe snapshot exceeds maximum context age"
        )
        return ProspectiveCutoffRecord(
            cutoff=cutoff,
            context_status=status,
            context_detail=detail,
            snapshot_captured_at=snapshot.captured_at if snapshot is not None else None,
            snapshot_sha256=snapshot.content_sha256 if snapshot is not None else None,
            snapshot_age_seconds=age,
            slots=(),
        )
    assert snapshot is not None

    slots: list[ProspectiveSlotRecord] = []
    for member in snapshot.members[:analysis_limit]:
        symbol = member.instrument.symbol
        bundle = bundles.get(symbol)
        if bundle is None:
            slots.append(
                ProspectiveSlotRecord(
                    symbol=symbol,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                    status="HISTORY_FAIL",
                    detail="BUNDLE_UNAVAILABLE",
                    decisions=(),
                )
            )
            continue
        try:
            replay_snapshot = slice_datasets_asof(
                bundle.datasets,
                as_of=cutoff,
                minimum_bars=scanner.history.interval_counts,
            )
        except ValueError as exc:
            message = str(exc)
            if not message.startswith("insufficient "):
                raise
            slots.append(
                ProspectiveSlotRecord(
                    symbol=symbol,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                    status="HISTORY_FAIL",
                    detail=f"ValueError: {message}",
                    decisions=(),
                )
            )
            continue

        candles_by_interval = {
            interval: dataset.candles
            for interval, dataset in replay_snapshot.datasets.items()
        }
        if not current_utc_day_5m_available(candles_by_interval, cutoff=cutoff):
            slots.append(
                ProspectiveSlotRecord(
                    symbol=symbol,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                    status="ANALYSIS_ERROR",
                    detail=UTC_DAY_5M_EMPTY_ERROR,
                    decisions=(),
                )
            )
            continue

        universe_candidate = UniverseCandidate(
            instrument=member.instrument,
            ticker=member.ticker,
            liquidity_score=member.liquidity_score,
        )
        try:
            decisions = tuple(
                analysis_function(
                    config=scanner,
                    instrument=member.instrument,
                    universe_candidate=universe_candidate,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                    candles_by_interval=candles_by_interval,
                    now=cutoff,
                )
            )
        except Exception as exc:  # fail-closed accounting; no decision is synthesized
            slots.append(
                ProspectiveSlotRecord(
                    symbol=symbol,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                    status="ANALYSIS_ERROR",
                    detail=f"{type(exc).__name__}: {exc}",
                    decisions=(),
                )
            )
            continue

        slots.append(
            ProspectiveSlotRecord(
                symbol=symbol,
                liquidity_rank=member.rank,
                universe_size=snapshot.universe_size,
                status="ANALYZED",
                detail=None,
                decisions=tuple(_audit_decision(decision) for decision in decisions),
            )
        )

    return ProspectiveCutoffRecord(
        cutoff=cutoff,
        context_status="SELECTED",
        context_detail=None,
        snapshot_captured_at=snapshot.captured_at,
        snapshot_sha256=snapshot.content_sha256,
        snapshot_age_seconds=age,
        slots=tuple(slots),
    )


def _audit_decision(decision: TradingDecision) -> ProspectiveDecisionAudit:
    signal_key = stable_signal_key(decision) if decision.side in {"LONG", "SHORT"} else None
    return ProspectiveDecisionAudit(
        decision_id=decision_fingerprint(decision),
        signal_key=signal_key,
        side=decision.side,
        grade=decision.grade,
        setup_score=decision.setup_score,
        raw_score=decision.raw_score,
        setup_type=decision.setup_type,
        primary_level_id=decision.primary_level_id,
        primary_level_strength=decision.primary_level_strength,
        rr=decision.rr,
        atr_used_pct=decision.atr_used_pct,
        entry=decision.entry,
        stop=decision.stop,
        target=decision.target,
        last_closed_bar=decision.last_closed_bar,
        generated_at=decision.generated_at,
        reason_codes=decision.reason_codes,
    )


def _build_shard(
    *,
    archive: UniverseSnapshotArchive,
    bundle_digests: Mapping[str, str],
    scanner_config_sha256_value: str,
    start: datetime,
    end: datetime,
    interval_seconds: int,
    analysis_limit: int,
    max_context_age_seconds: float,
    shard_index: int,
    shard_count: int,
    assigned: Sequence[datetime],
    records: Mapping[datetime, ProspectiveCutoffRecord],
) -> ProspectiveControlShard:
    ordered_records = tuple(records[value] for value in assigned if value in records)
    fields = {
        "schema_version": PROSPECTIVE_CONTROL_SHARD_SCHEMA_VERSION,
        "provider_id": archive.provider_id,
        "archive_sha256": archive.archive_sha256,
        "scanner_config_sha256": scanner_config_sha256_value,
        "start": start,
        "end": end,
        "cutoff_interval_seconds": interval_seconds,
        "analysis_limit": analysis_limit,
        "max_context_age_seconds": max_context_age_seconds,
        "shard_index": shard_index,
        "shard_count": shard_count,
        "expected_cutoff_count": len(assigned),
        "bundle_sha256_by_symbol": dict(sorted(bundle_digests.items())),
        "cutoffs": ordered_records,
        "complete": len(ordered_records) == len(assigned),
    }
    return ProspectiveControlShard(
        **fields,
        shard_sha256=canonical_digest(fields),
    )


def _selected_symbols_for_window(
    archive: UniverseSnapshotArchive,
    cutoffs: Sequence[datetime],
    *,
    analysis_limit: int,
    max_context_age_seconds: float,
) -> frozenset[str]:
    symbols: set[str] = set()
    for cutoff in cutoffs:
        status, snapshot, _age = select_recorded_snapshot(
            archive,
            cutoff,
            max_context_age_seconds=max_context_age_seconds,
        )
        if status != "SELECTED" or snapshot is None:
            continue
        symbols.update(member.instrument.symbol for member in snapshot.members[:analysis_limit])
    return frozenset(symbols)


def _validate_inputs(
    archive: UniverseSnapshotArchive,
    bundles: Mapping[str, MTFReplayBundle],
    *,
    end: datetime,
    required_symbols: frozenset[str],
) -> dict[str, str]:
    for key, bundle in bundles.items():
        manifest = bundle.manifest
        if key != manifest.canonical_symbol:
            raise ValueError("bundle mapping key/canonical symbol mismatch")
        if manifest.provider_id != archive.provider_id:
            raise ValueError("prospective control cannot mix archive/bundle providers")

    digests: dict[str, str] = {}
    for symbol in sorted(required_symbols):
        bundle = bundles.get(symbol)
        if bundle is None:
            continue
        manifest = bundle.manifest
        if manifest.as_of < end:
            raise ValueError(f"bundle {symbol} as_of does not cover prospective-control end")
        digests[symbol] = manifest.bundle_sha256
    return digests


def _validate_resume(
    resume: ProspectiveControlShard,
    *,
    archive: UniverseSnapshotArchive,
    bundle_digests: Mapping[str, str],
    scanner_config_sha256_value: str,
    start: datetime,
    end: datetime,
    interval_seconds: int,
    analysis_limit: int,
    max_context_age_seconds: float,
    shard_index: int,
    shard_count: int,
    assigned: Sequence[datetime],
) -> None:
    _validate_shard_digest(resume)
    expected = (
        resume.provider_id == archive.provider_id
        and resume.archive_sha256 == archive.archive_sha256
        and resume.scanner_config_sha256 == scanner_config_sha256_value
        and resume.start == start
        and resume.end == end
        and resume.cutoff_interval_seconds == interval_seconds
        and resume.analysis_limit == analysis_limit
        and resume.max_context_age_seconds == max_context_age_seconds
        and resume.shard_index == shard_index
        and resume.shard_count == shard_count
        and resume.expected_cutoff_count == len(assigned)
        and dict(resume.bundle_sha256_by_symbol) == dict(bundle_digests)
    )
    if not expected:
        raise ValueError("resume shard provenance/configuration mismatch")
    cutoffs = tuple(record.cutoff for record in resume.cutoffs)
    if len(cutoffs) != len(set(cutoffs)):
        raise ValueError("resume shard contains duplicate cutoffs")
    allowed = set(assigned)
    if any(value not in allowed for value in cutoffs):
        raise ValueError("resume shard contains cutoff outside deterministic shard assignment")


def _require_same_provenance(
    first: ProspectiveControlShard,
    other: ProspectiveControlShard,
) -> None:
    fields = (
        "schema_version",
        "provider_id",
        "archive_sha256",
        "scanner_config_sha256",
        "start",
        "end",
        "cutoff_interval_seconds",
        "analysis_limit",
        "max_context_age_seconds",
        "shard_count",
        "bundle_sha256_by_symbol",
    )
    if any(getattr(first, name) != getattr(other, name) for name in fields):
        raise ValueError("prospective-control shard provenance mismatch")


def _aggregate_report(
    source: ProspectiveControlShard,
    records: Sequence[ProspectiveCutoffRecord],
) -> ProspectiveControlReport:
    selected = tuple(record for record in records if record.context_status == "SELECTED")
    ages = [record.snapshot_age_seconds for record in selected if record.snapshot_age_seconds is not None]
    slots = tuple(slot for record in records for slot in record.slots)
    analyzed_slots = tuple(slot for slot in slots if slot.status == "ANALYZED")
    decisions = tuple(decision for slot in analyzed_slots for decision in slot.decisions)
    candidates = tuple(decision for decision in decisions if decision.setup_type != "NO_SETUP")

    best_side_counts: Counter[str] = Counter()
    for slot in analyzed_slots:
        best = _best_audit(slot.decisions)
        if best is not None:
            best_side_counts[best.side] += 1

    candidate_records_by_symbol: Counter[str] = Counter()
    for slot in analyzed_slots:
        count = sum(decision.setup_type != "NO_SETUP" for decision in slot.decisions)
        if count:
            candidate_records_by_symbol[slot.symbol] += count

    history_fail_by_symbol = Counter(slot.symbol for slot in slots if slot.status == "HISTORY_FAIL")
    analysis_errors = Counter(slot.detail or "UNKNOWN" for slot in slots if slot.status == "ANALYSIS_ERROR")
    reason_counts = Counter(reason for decision in candidates for reason in decision.reason_codes)
    setup_type_counts = Counter(decision.setup_type for decision in candidates)

    htf = tuple(decision for decision in candidates if "HTF_CONTEXT_MISMATCH" not in decision.reason_codes)
    strong = tuple(
        decision for decision in htf
        if "PRIMARY_LEVEL_NOT_STRONG" not in decision.reason_codes
        and "PRIMARY_LEVEL_NOT_CONFIRMED" not in decision.reason_codes
        and decision.primary_level_strength == "STRONG"
    )
    geometry_reasons = {
        "MISSING_PRICE_TICK",
        "NO_STRUCTURAL_TARGET",
        "MISSING_CONFIRMATION",
        "INVALID_GEOMETRY",
        "GEOMETRY_UNAVAILABLE",
    }
    geometry = tuple(
        decision for decision in strong
        if decision.rr is not None
        and not geometry_reasons.intersection(decision.reason_codes)
    )
    atr_pass = tuple(
        decision for decision in geometry
        if decision.atr_used_pct is not None
        and decision.atr_used_pct <= Decimal("80")
        and "ATR_USED_OVER_80" not in decision.reason_codes
    )
    ttl_pass = tuple(decision for decision in atr_pass if "SETUP_EXPIRED" not in decision.reason_codes)
    rr_pass = tuple(
        decision for decision in ttl_pass
        if decision.rr is not None and decision.rr >= Decimal("3")
    )
    grade_pass = tuple(decision for decision in rr_pass if decision.grade in {"A", "A+"})
    tradable = tuple(decision for decision in grade_pass if decision.side in {"LONG", "SHORT"})

    funnel = {
        "htf_aligned": len(htf),
        "strong_confirmed_level": len(strong),
        "geometry_valid": len(geometry),
        "atr_pass": len(atr_pass),
        "ttl_pass": len(ttl_pass),
        "rr_pass": len(rr_pass),
        "grade_pass": len(grade_pass),
        "tradable": len(tradable),
    }
    denominator = len(htf)
    funnel_pct = {
        key: round(value * 100.0 / denominator, 4) if denominator else 0.0
        for key, value in funnel.items()
        if key != "htf_aligned"
    }

    fields = {
        "schema_version": PROSPECTIVE_CONTROL_REPORT_SCHEMA_VERSION,
        "provider_id": source.provider_id,
        "start": source.start,
        "end": source.end,
        "cutoff_interval_seconds": source.cutoff_interval_seconds,
        "analysis_limit": source.analysis_limit,
        "max_context_age_seconds": source.max_context_age_seconds,
        "archive_sha256": source.archive_sha256,
        "scanner_config_sha256": source.scanner_config_sha256,
        "bundle_sha256_by_symbol": dict(sorted(source.bundle_sha256_by_symbol.items())),
        "logical_cutoffs": len(records),
        "selected_context_cutoffs": len(selected),
        "missing_context_cutoffs": tuple(record.cutoff for record in records if record.context_status == "MISSING"),
        "stale_context_cutoffs": tuple(record.cutoff for record in records if record.context_status == "STALE"),
        "context_age_seconds": {
            "min": min(ages) if ages else None,
            "max": max(ages) if ages else None,
        },
        "symbol_slots": len(slots),
        "history_pass_slots": len(analyzed_slots),
        "history_fail_slots": sum(slot.status == "HISTORY_FAIL" for slot in slots),
        "analysis_error_slots": sum(slot.status == "ANALYSIS_ERROR" for slot in slots),
        "decision_records": len(decisions),
        "best_side_counts": dict(sorted(best_side_counts.items())),
        "candidate_records_by_symbol": dict(sorted(candidate_records_by_symbol.items())),
        "history_fail_by_symbol": dict(sorted(history_fail_by_symbol.items())),
        "analysis_errors": dict(sorted(analysis_errors.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "setup_type_counts": dict(sorted(setup_type_counts.items())),
        "funnel": funnel,
        "funnel_pct_of_htf": funnel_pct,
        "tradable_records": tuple(_audit_summary(decision) for decision in tradable),
        "rr3_nontradable": tuple(
            _audit_summary(decision)
            for decision in rr_pass
            if decision.side not in {"LONG", "SHORT"}
        ),
        "near_miss": tuple(
            _audit_summary(decision)
            for decision in rr_pass
            if decision.grade not in {"A", "A+"}
        ),
        "unique_tradable_signal_count": len({decision.signal_key for decision in tradable if decision.signal_key}),
    }
    return ProspectiveControlReport(
        **fields,
        report_sha256=canonical_digest(fields),
    )


def _best_audit(decisions: Sequence[ProspectiveDecisionAudit]) -> ProspectiveDecisionAudit | None:
    if not decisions:
        return None
    return max(
        decisions,
        key=lambda item: (
            item.side != "NO_TRADE",
            item.setup_score,
            item.raw_score,
            item.rr or Decimal("0"),
        ),
    )


def _audit_summary(decision: ProspectiveDecisionAudit) -> Mapping[str, object]:
    return {
        "decision_id": decision.decision_id,
        "signal_key": decision.signal_key,
        "side": decision.side,
        "grade": decision.grade,
        "setup_score": decision.setup_score,
        "raw_score": decision.raw_score,
        "setup_type": decision.setup_type,
        "primary_level_id": decision.primary_level_id,
        "rr": decision.rr,
        "atr_used_pct": decision.atr_used_pct,
        "entry": decision.entry,
        "stop": decision.stop,
        "target": decision.target,
        "last_closed_bar": decision.last_closed_bar,
        "generated_at": decision.generated_at,
        "reason_codes": decision.reason_codes,
    }


def _shard_payload(shard: ProspectiveControlShard, *, include_digest: bool) -> dict[str, object]:
    payload = asdict(shard)
    if not include_digest:
        payload.pop("shard_sha256", None)
    return _jsonable(payload)


def _report_payload(report: ProspectiveControlReport, *, include_digest: bool) -> dict[str, object]:
    payload = asdict(report)
    if not include_digest:
        payload.pop("report_sha256", None)
    return _jsonable(payload)


def _validate_shard_digest(shard: ProspectiveControlShard) -> None:
    if shard.schema_version != PROSPECTIVE_CONTROL_SHARD_SCHEMA_VERSION:
        raise ValueError("unsupported prospective-control shard schema version")
    if canonical_digest(_shard_payload(shard, include_digest=False)) != shard.shard_sha256:
        raise ValueError("prospective-control shard digest mismatch")


def _validate_report_digest(report: ProspectiveControlReport) -> None:
    if report.schema_version != PROSPECTIVE_CONTROL_REPORT_SCHEMA_VERSION:
        raise ValueError("unsupported prospective-control report schema version")
    if canonical_digest(_report_payload(report, include_digest=False)) != report.report_sha256:
        raise ValueError("prospective-control report digest mismatch")


def _deserialize_shard(payload: Mapping[str, object]) -> ProspectiveControlShard:
    raw_cutoffs = payload.get("cutoffs")
    if not isinstance(raw_cutoffs, list):
        raise ValueError("prospective-control shard cutoffs must be a list")
    bundle_map = payload.get("bundle_sha256_by_symbol")
    if not isinstance(bundle_map, dict):
        raise ValueError("prospective-control shard bundle map is invalid")
    return ProspectiveControlShard(
        schema_version=str(payload.get("schema_version")),
        provider_id=str(payload.get("provider_id")),
        archive_sha256=str(payload.get("archive_sha256")),
        scanner_config_sha256=str(payload.get("scanner_config_sha256")),
        start=_parse_time(payload.get("start")),
        end=_parse_time(payload.get("end")),
        cutoff_interval_seconds=int(payload.get("cutoff_interval_seconds", 0)),
        analysis_limit=int(payload.get("analysis_limit", 0)),
        max_context_age_seconds=float(payload.get("max_context_age_seconds", 0)),
        shard_index=int(payload.get("shard_index", -1)),
        shard_count=int(payload.get("shard_count", 0)),
        expected_cutoff_count=int(payload.get("expected_cutoff_count", -1)),
        bundle_sha256_by_symbol={str(key): str(value) for key, value in bundle_map.items()},
        cutoffs=tuple(_deserialize_cutoff(item) for item in raw_cutoffs),
        complete=bool(payload.get("complete")),
        shard_sha256=str(payload.get("shard_sha256")),
    )


def _deserialize_cutoff(payload: Mapping[str, object]) -> ProspectiveCutoffRecord:
    raw_slots = payload.get("slots")
    if not isinstance(raw_slots, list):
        raise ValueError("prospective-control cutoff slots must be a list")
    snapshot_at = payload.get("snapshot_captured_at")
    return ProspectiveCutoffRecord(
        cutoff=_parse_time(payload.get("cutoff")),
        context_status=str(payload.get("context_status")),
        context_detail=str(payload["context_detail"]) if payload.get("context_detail") is not None else None,
        snapshot_captured_at=_parse_time(snapshot_at) if snapshot_at is not None else None,
        snapshot_sha256=str(payload["snapshot_sha256"]) if payload.get("snapshot_sha256") is not None else None,
        snapshot_age_seconds=float(payload["snapshot_age_seconds"]) if payload.get("snapshot_age_seconds") is not None else None,
        slots=tuple(_deserialize_slot(item) for item in raw_slots),
    )


def _deserialize_slot(payload: Mapping[str, object]) -> ProspectiveSlotRecord:
    raw_decisions = payload.get("decisions")
    if not isinstance(raw_decisions, list):
        raise ValueError("prospective-control slot decisions must be a list")
    return ProspectiveSlotRecord(
        symbol=str(payload.get("symbol")),
        liquidity_rank=int(payload.get("liquidity_rank", 0)),
        universe_size=int(payload.get("universe_size", 0)),
        status=str(payload.get("status")),
        detail=str(payload["detail"]) if payload.get("detail") is not None else None,
        decisions=tuple(_deserialize_audit(item) for item in raw_decisions),
    )


def _deserialize_audit(payload: Mapping[str, object]) -> ProspectiveDecisionAudit:
    raw_reasons = payload.get("reason_codes")
    if not isinstance(raw_reasons, list):
        raise ValueError("prospective-control audit reason_codes must be a list")
    return ProspectiveDecisionAudit(
        decision_id=str(payload.get("decision_id")),
        signal_key=str(payload["signal_key"]) if payload.get("signal_key") is not None else None,
        side=str(payload.get("side")),
        grade=str(payload.get("grade")),
        setup_score=int(payload.get("setup_score", 0)),
        raw_score=int(payload.get("raw_score", 0)),
        setup_type=str(payload.get("setup_type")),
        primary_level_id=str(payload["primary_level_id"]) if payload.get("primary_level_id") is not None else None,
        primary_level_strength=str(payload["primary_level_strength"]) if payload.get("primary_level_strength") is not None else None,
        rr=_optional_decimal(payload.get("rr")),
        atr_used_pct=_optional_decimal(payload.get("atr_used_pct")),
        entry=_optional_decimal(payload.get("entry")),
        stop=_optional_decimal(payload.get("stop")),
        target=_optional_decimal(payload.get("target")),
        last_closed_bar=_parse_time(payload.get("last_closed_bar")),
        generated_at=_parse_time(payload.get("generated_at")),
        reason_codes=tuple(str(item) for item in raw_reasons),
    )


def _deserialize_report(payload: Mapping[str, object]) -> ProspectiveControlReport:
    def mapping(name: str, caster):
        raw = payload.get(name)
        if not isinstance(raw, dict):
            raise ValueError(f"prospective-control report {name} is invalid")
        return {str(key): caster(value) for key, value in raw.items()}

    def times(name: str) -> tuple[datetime, ...]:
        raw = payload.get(name)
        if not isinstance(raw, list):
            raise ValueError(f"prospective-control report {name} must be a list")
        return tuple(_parse_time(value) for value in raw)

    def summaries(name: str) -> tuple[Mapping[str, object], ...]:
        raw = payload.get(name)
        if not isinstance(raw, list):
            raise ValueError(f"prospective-control report {name} must be a list")
        return tuple(_restore_jsonable_summary(value) for value in raw)

    ages = payload.get("context_age_seconds")
    if not isinstance(ages, dict):
        raise ValueError("prospective-control report context_age_seconds is invalid")
    return ProspectiveControlReport(
        schema_version=str(payload.get("schema_version")),
        provider_id=str(payload.get("provider_id")),
        start=_parse_time(payload.get("start")),
        end=_parse_time(payload.get("end")),
        cutoff_interval_seconds=int(payload.get("cutoff_interval_seconds", 0)),
        analysis_limit=int(payload.get("analysis_limit", 0)),
        max_context_age_seconds=float(payload.get("max_context_age_seconds", 0)),
        archive_sha256=str(payload.get("archive_sha256")),
        scanner_config_sha256=str(payload.get("scanner_config_sha256")),
        bundle_sha256_by_symbol=mapping("bundle_sha256_by_symbol", str),
        logical_cutoffs=int(payload.get("logical_cutoffs", 0)),
        selected_context_cutoffs=int(payload.get("selected_context_cutoffs", 0)),
        missing_context_cutoffs=times("missing_context_cutoffs"),
        stale_context_cutoffs=times("stale_context_cutoffs"),
        context_age_seconds={
            "min": float(ages["min"]) if ages.get("min") is not None else None,
            "max": float(ages["max"]) if ages.get("max") is not None else None,
        },
        symbol_slots=int(payload.get("symbol_slots", 0)),
        history_pass_slots=int(payload.get("history_pass_slots", 0)),
        history_fail_slots=int(payload.get("history_fail_slots", 0)),
        analysis_error_slots=int(payload.get("analysis_error_slots", 0)),
        decision_records=int(payload.get("decision_records", 0)),
        best_side_counts=mapping("best_side_counts", int),
        candidate_records_by_symbol=mapping("candidate_records_by_symbol", int),
        history_fail_by_symbol=mapping("history_fail_by_symbol", int),
        analysis_errors=mapping("analysis_errors", int),
        reason_counts=mapping("reason_counts", int),
        setup_type_counts=mapping("setup_type_counts", int),
        funnel=mapping("funnel", int),
        funnel_pct_of_htf=mapping("funnel_pct_of_htf", float),
        tradable_records=summaries("tradable_records"),
        rr3_nontradable=summaries("rr3_nontradable"),
        near_miss=summaries("near_miss"),
        unique_tradable_signal_count=int(payload.get("unique_tradable_signal_count", 0)),
        report_sha256=str(payload.get("report_sha256")),
    )


def _restore_jsonable_summary(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError("prospective-control report summary record is invalid")
    restored = dict(value)
    for name in ("rr", "atr_used_pct", "entry", "stop", "target"):
        restored[name] = _optional_decimal(restored.get(name))
    for name in ("last_closed_bar", "generated_at"):
        if restored.get(name) is not None:
            restored[name] = _parse_time(restored[name])
    if isinstance(restored.get("reason_codes"), list):
        restored["reason_codes"] = tuple(str(item) for item in restored["reason_codes"])
    return restored


def _jsonable(value: object) -> object:
    if isinstance(value, datetime):
        _require_utc(value, "datetime")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    _require_utc(parsed, "datetime")
    return parsed.astimezone(timezone.utc)


def _optional_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _require_utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be timezone-aware UTC")


def _aligned(value: datetime, interval_seconds: int) -> bool:
    return value.microsecond == 0 and int(value.timestamp()) % interval_seconds == 0
