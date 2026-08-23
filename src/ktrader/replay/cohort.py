from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Mapping, Sequence

from ktrader.history.universe import UniverseSnapshotArchive, UniverseSnapshotMember
from ktrader.market.timeframes import require_utc
from ktrader.models import NormalizedInstrument
from ktrader.replay.study import ReplayLiquidityPoint, ReplayStudyContext, load_replay_context, write_replay_context


STUDY_COHORT_SCHEMA_VERSION = "ktrader.study_cohort.v1"


@dataclass(frozen=True, slots=True)
class HistoricalStudyCohort:
    schema_version: str
    provider_id: str
    archive_sha256: str
    snapshot_digests: tuple[str, ...]
    start: datetime
    end: datetime
    symbols: tuple[str, ...]
    contexts: Mapping[str, ReplayStudyContext]
    max_context_age_seconds: float
    cohort_sha256: str


def build_study_cohort(
    archive: UniverseSnapshotArchive,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    symbols: Sequence[str] | None = None,
    max_context_age_seconds: float = 300.0,
) -> HistoricalStudyCohort:
    if max_context_age_seconds <= 0:
        raise ValueError("max_context_age_seconds must be positive")
    if start is not None:
        require_utc(start)
    if end is not None:
        require_utc(end)
    if start is not None and end is not None and end < start:
        raise ValueError("cohort end cannot be before start")

    snapshots = tuple(
        snapshot
        for snapshot in archive.snapshots
        if (start is None or snapshot.captured_at >= start)
        and (end is None or snapshot.captured_at <= end)
    )
    if not snapshots:
        raise ValueError("no universe snapshots fall inside cohort window")

    available = sorted({member.instrument.symbol for snapshot in snapshots for member in snapshot.members})
    if symbols is None:
        selected_symbols = tuple(available)
    else:
        normalized = tuple(dict.fromkeys(str(symbol).upper() for symbol in symbols))
        if not normalized:
            raise ValueError("symbols cannot be empty")
        missing = sorted(set(normalized) - set(available))
        if missing:
            raise ValueError("requested cohort symbols are absent from captured universe: " + ",".join(missing))
        selected_symbols = normalized

    contexts: dict[str, ReplayStudyContext] = {}
    for symbol in selected_symbols:
        instrument: NormalizedInstrument | None = None
        points: list[ReplayLiquidityPoint] = []
        for snapshot in snapshots:
            member = _member_for(snapshot.members, symbol)
            if member is None:
                continue
            if instrument is None:
                instrument = member.instrument
            elif not _same_analysis_instrument(instrument, member.instrument):
                raise ValueError(f"instrument analysis metadata changed inside cohort for {symbol}")
            points.append(
                ReplayLiquidityPoint(
                    timestamp=snapshot.captured_at,
                    liquidity_score=member.liquidity_score,
                    liquidity_rank=member.rank,
                    universe_size=snapshot.universe_size,
                )
            )
        if instrument is None or not points:
            raise ValueError(f"no replay context points available for {symbol}")
        contexts[symbol] = ReplayStudyContext(
            instrument=instrument,
            liquidity_points=tuple(points),
            max_context_age_seconds=max_context_age_seconds,
        )

    actual_start = snapshots[0].captured_at
    actual_end = snapshots[-1].captured_at
    snapshot_digests = tuple(snapshot.content_sha256 for snapshot in snapshots)
    digest = _cohort_digest(
        provider_id=archive.provider_id,
        archive_sha256=archive.archive_sha256,
        snapshot_digests=snapshot_digests,
        start=actual_start,
        end=actual_end,
        symbols=selected_symbols,
        contexts=contexts,
        max_context_age_seconds=max_context_age_seconds,
    )
    return HistoricalStudyCohort(
        schema_version=STUDY_COHORT_SCHEMA_VERSION,
        provider_id=archive.provider_id,
        archive_sha256=archive.archive_sha256,
        snapshot_digests=snapshot_digests,
        start=actual_start,
        end=actual_end,
        symbols=selected_symbols,
        contexts=contexts,
        max_context_age_seconds=max_context_age_seconds,
        cohort_sha256=digest,
    )


def write_study_cohort(path: str | Path, cohort: HistoricalStudyCohort) -> Path:
    _validate_cohort(cohort)
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    contexts_dir = root / "contexts"
    contexts_dir.mkdir(parents=True, exist_ok=True)
    context_files: dict[str, str] = {}
    context_digests: dict[str, str] = {}
    for symbol in cohort.symbols:
        filename = f"{_safe_symbol(symbol)}.json"
        write_replay_context(contexts_dir / filename, cohort.contexts[symbol])
        context_files[symbol] = f"contexts/{filename}"
        context_digests[symbol] = _context_digest(cohort.contexts[symbol])

    manifest = {
        "schema_version": cohort.schema_version,
        "provider_id": cohort.provider_id,
        "archive_sha256": cohort.archive_sha256,
        "snapshot_digests": list(cohort.snapshot_digests),
        "start": _time(cohort.start),
        "end": _time(cohort.end),
        "symbols": list(cohort.symbols),
        "max_context_age_seconds": cohort.max_context_age_seconds,
        "context_files": context_files,
        "context_digests": context_digests,
        "cohort_sha256": cohort.cohort_sha256,
    }
    (root / "cohort.json").write_text(
        json.dumps(manifest, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return root


def load_study_cohort(path: str | Path) -> HistoricalStudyCohort:
    root = Path(path)
    payload = json.loads((root / "cohort.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != STUDY_COHORT_SCHEMA_VERSION:
        raise ValueError("unsupported study cohort schema version")
    raw_symbols = payload.get("symbols")
    raw_files = payload.get("context_files")
    raw_digests = payload.get("context_digests")
    raw_snapshots = payload.get("snapshot_digests")
    if not isinstance(raw_symbols, list) or not isinstance(raw_files, dict) or not isinstance(raw_digests, dict) or not isinstance(raw_snapshots, list):
        raise ValueError("invalid study cohort manifest")
    symbols = tuple(str(symbol) for symbol in raw_symbols)
    contexts: dict[str, ReplayStudyContext] = {}
    for symbol in symbols:
        filename = raw_files.get(symbol)
        if not isinstance(filename, str):
            raise ValueError("missing cohort context file")
        relative = Path(filename)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("unsafe cohort context path")
        context = load_replay_context(root / relative)
        if context.instrument.provider_id != str(payload["provider_id"]) or context.instrument.symbol != symbol:
            raise ValueError("cohort context identity mismatch")
        expected_context_digest = str(raw_digests.get(symbol))
        if _context_digest(context) != expected_context_digest:
            raise ValueError("cohort context digest mismatch")
        contexts[symbol] = context

    cohort = HistoricalStudyCohort(
        schema_version=STUDY_COHORT_SCHEMA_VERSION,
        provider_id=str(payload["provider_id"]),
        archive_sha256=str(payload["archive_sha256"]),
        snapshot_digests=tuple(str(value) for value in raw_snapshots),
        start=_parse_time(payload["start"]),
        end=_parse_time(payload["end"]),
        symbols=symbols,
        contexts=contexts,
        max_context_age_seconds=float(payload["max_context_age_seconds"]),
        cohort_sha256=str(payload["cohort_sha256"]),
    )
    _validate_cohort(cohort)
    return cohort


def _validate_cohort(cohort: HistoricalStudyCohort) -> None:
    if cohort.schema_version != STUDY_COHORT_SCHEMA_VERSION:
        raise ValueError("unsupported study cohort schema version")
    require_utc(cohort.start)
    require_utc(cohort.end)
    if cohort.end < cohort.start:
        raise ValueError("cohort end cannot be before start")
    if not cohort.symbols or len(set(cohort.symbols)) != len(cohort.symbols):
        raise ValueError("cohort symbols must be unique and non-empty")
    if set(cohort.contexts) != set(cohort.symbols):
        raise ValueError("cohort contexts must exactly match symbols")
    if not cohort.snapshot_digests:
        raise ValueError("cohort requires snapshot digests")
    for symbol in cohort.symbols:
        context = cohort.contexts[symbol]
        if context.instrument.provider_id != cohort.provider_id or context.instrument.symbol != symbol:
            raise ValueError("cohort context identity mismatch")
    expected = _cohort_digest(
        provider_id=cohort.provider_id,
        archive_sha256=cohort.archive_sha256,
        snapshot_digests=cohort.snapshot_digests,
        start=cohort.start,
        end=cohort.end,
        symbols=cohort.symbols,
        contexts=cohort.contexts,
        max_context_age_seconds=cohort.max_context_age_seconds,
    )
    if expected != cohort.cohort_sha256:
        raise ValueError("study cohort digest mismatch")


def _member_for(members: Sequence[UniverseSnapshotMember], symbol: str) -> UniverseSnapshotMember | None:
    return next((member for member in members if member.instrument.symbol == symbol), None)


def _same_analysis_instrument(left: NormalizedInstrument, right: NormalizedInstrument) -> bool:
    return (
        left.provider_id,
        left.symbol,
        left.provider_symbol or left.symbol,
        left.base_asset,
        left.quote_asset,
        left.market_type,
        left.contract_type,
        left.status,
        left.price_tick,
        left.quantity_step,
    ) == (
        right.provider_id,
        right.symbol,
        right.provider_symbol or right.symbol,
        right.base_asset,
        right.quote_asset,
        right.market_type,
        right.contract_type,
        right.status,
        right.price_tick,
        right.quantity_step,
    )


def _cohort_digest(
    *,
    provider_id: str,
    archive_sha256: str,
    snapshot_digests: Sequence[str],
    start: datetime,
    end: datetime,
    symbols: Sequence[str],
    contexts: Mapping[str, ReplayStudyContext],
    max_context_age_seconds: float,
) -> str:
    payload = {
        "schema_version": STUDY_COHORT_SCHEMA_VERSION,
        "provider_id": provider_id,
        "archive_sha256": archive_sha256,
        "snapshot_digests": list(snapshot_digests),
        "start": _time(start),
        "end": _time(end),
        "symbols": list(symbols),
        "max_context_age_seconds": max_context_age_seconds,
        "context_digests": {symbol: _context_digest(contexts[symbol]) for symbol in symbols},
    }
    return _digest(payload)


def _context_digest(context: ReplayStudyContext) -> str:
    instrument = context.instrument
    payload = {
        "provider_id": instrument.provider_id,
        "symbol": instrument.symbol,
        "provider_symbol": instrument.provider_symbol or instrument.symbol,
        "base_asset": instrument.base_asset,
        "quote_asset": instrument.quote_asset,
        "market_type": instrument.market_type,
        "contract_type": instrument.contract_type,
        "status": instrument.status,
        "price_tick": None if instrument.price_tick is None else format(instrument.price_tick, "f"),
        "quantity_step": None if instrument.quantity_step is None else format(instrument.quantity_step, "f"),
        "max_context_age_seconds": context.max_context_age_seconds,
        "liquidity_points": [
            [
                _time(point.timestamp),
                format(point.liquidity_score, "f"),
                point.liquidity_rank,
                point.universe_size,
            ]
            for point in context.liquidity_points
        ],
    }
    return _digest(payload)


def _safe_symbol(symbol: str) -> str:
    if not symbol or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for character in symbol):
        raise ValueError(f"unsafe cohort symbol {symbol!r}")
    return symbol


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()


def _time(value: datetime) -> str:
    require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    require_utc(parsed)
    return parsed.astimezone(timezone.utc)
