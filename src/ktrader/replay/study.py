from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from collections import Counter
from collections.abc import Callable, Mapping, Sequence

from ktrader.engine.models import TradingDecision
from ktrader.engine.service import choose_best_decision
from ktrader.history.bundle import MTFReplayBundle, slice_datasets_asof
from ktrader.market.timeframes import interval_seconds, require_utc
from ktrader.market.universe import UniverseCandidate
from ktrader.models import NormalizedInstrument, NormalizedTicker
from ktrader.outcomes.evaluator import SignalOutcome, decision_fingerprint, evaluate_signal_outcome
from ktrader.outcomes.storage import OutcomeRepository
from ktrader.runtime.analyzer import analyze_candle_snapshot
from ktrader.runtime.models import RuntimeScannerConfig


REPLAY_CONTEXT_SCHEMA_VERSION = "ktrader.replay_context.v1"
REPLAY_STUDY_SCHEMA_VERSION = "ktrader.replay_study.v1"


@dataclass(frozen=True, slots=True)
class ReplayLiquidityPoint:
    timestamp: datetime
    liquidity_score: Decimal
    liquidity_rank: int
    universe_size: int

    def __post_init__(self) -> None:
        require_utc(self.timestamp)
        if self.liquidity_score < 0:
            raise ValueError("liquidity_score cannot be negative")
        if self.liquidity_rank <= 0 or self.universe_size <= 0 or self.liquidity_rank > self.universe_size:
            raise ValueError("invalid liquidity rank/universe size")


@dataclass(frozen=True, slots=True)
class ReplayStudyContext:
    instrument: NormalizedInstrument
    liquidity_points: tuple[ReplayLiquidityPoint, ...]
    max_context_age_seconds: float = 300.0

    def __post_init__(self) -> None:
        if not self.liquidity_points:
            raise ValueError("replay context requires liquidity points")
        if self.max_context_age_seconds <= 0:
            raise ValueError("max_context_age_seconds must be positive")
        previous: datetime | None = None
        for point in self.liquidity_points:
            if previous is not None and point.timestamp <= previous:
                raise ValueError("liquidity points must be strictly chronological")
            previous = point.timestamp

    def point_at(self, as_of: datetime) -> ReplayLiquidityPoint | None:
        require_utc(as_of)
        selected: ReplayLiquidityPoint | None = None
        for point in self.liquidity_points:
            if point.timestamp > as_of:
                break
            selected = point
        if selected is None:
            return None
        age = (as_of - selected.timestamp).total_seconds()
        if age > self.max_context_age_seconds:
            return None
        return selected


@dataclass(frozen=True, slots=True)
class ReplayStudyConfig:
    step_bars: int = 1
    horizon_bars: int | None = None
    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.step_bars <= 0:
            raise ValueError("step_bars must be positive")
        if self.horizon_bars is not None and self.horizon_bars <= 0:
            raise ValueError("horizon_bars must be positive when configured")
        if self.start is not None:
            require_utc(self.start)
        if self.end is not None:
            require_utc(self.end)
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValueError("study end must be after start")


@dataclass(frozen=True, slots=True)
class ReplayDecisionRecord:
    as_of: datetime
    decision_id: str
    signal_key: str | None
    decision: TradingDecision
    outcome: SignalOutcome | None


@dataclass(frozen=True, slots=True)
class ReplayStudyResult:
    schema_version: str
    study_id: str
    bundle_sha256: str
    provider_id: str
    canonical_symbol: str
    analyzed_cutoffs: int
    skipped_insufficient_history: int
    skipped_missing_context: int
    decision_records: tuple[ReplayDecisionRecord, ...]
    outcome_counts: Mapping[str, int]
    unique_tradable_signals: int
    binary_resolved_count: int
    estimated_probability: None = None


AnalysisFunction = Callable[..., Sequence[TradingDecision]]


def run_replay_study(
    bundle: MTFReplayBundle,
    context: ReplayStudyContext,
    *,
    scanner_config: RuntimeScannerConfig | None = None,
    study_config: ReplayStudyConfig | None = None,
    outcome_repository: OutcomeRepository | None = None,
    analysis_function: AnalysisFunction = analyze_candle_snapshot,
) -> ReplayStudyResult:
    """Walk an MTF bundle chronologically through the canonical analysis path.

    Market context is explicit and timestamped. Missing/stale liquidity context
    skips a cutoff instead of inventing a rank or universe size. Tradable setup
    geometry is deduplicated before Phase 11B outcome evaluation so unchanged
    consecutive snapshots do not become artificial independent signals.
    """
    scanner = scanner_config or RuntimeScannerConfig()
    study = study_config or ReplayStudyConfig()
    _validate_identity(bundle, context)

    setup_interval = scanner.setup_interval
    source_setup = bundle.datasets[setup_interval].candles
    cutoffs = [candle.close_time for candle in source_setup]
    if study.start is not None:
        cutoffs = [value for value in cutoffs if value >= study.start]
    if study.end is not None:
        cutoffs = [value for value in cutoffs if value <= study.end]
    cutoffs = cutoffs[:: study.step_bars]

    records: list[ReplayDecisionRecord] = []
    seen_signal_keys: set[str] = set()
    outcomes: list[SignalOutcome] = []
    skipped_history = 0
    skipped_context = 0
    analyzed = 0

    for cutoff in cutoffs:
        try:
            snapshot = slice_datasets_asof(
                bundle.datasets,
                as_of=cutoff,
                minimum_bars=scanner.history.interval_counts,
            )
        except ValueError as exc:
            if "insufficient" not in str(exc):
                raise
            skipped_history += 1
            continue

        point = context.point_at(cutoff)
        if point is None:
            skipped_context += 1
            continue

        candles_by_interval = {
            interval: dataset.candles
            for interval, dataset in snapshot.datasets.items()
        }
        setup_candles = candles_by_interval[setup_interval]
        ticker = NormalizedTicker(
            provider_id=context.instrument.provider_id,
            symbol=context.instrument.symbol,
            timestamp=cutoff,
            last_price=setup_candles[-1].close,
        )
        universe_candidate = UniverseCandidate(
            instrument=context.instrument,
            ticker=ticker,
            liquidity_score=point.liquidity_score,
        )
        decisions = tuple(
            analysis_function(
                config=scanner,
                instrument=context.instrument,
                universe_candidate=universe_candidate,
                liquidity_rank=point.liquidity_rank,
                universe_size=point.universe_size,
                candles_by_interval=candles_by_interval,
                now=cutoff,
            )
        )
        best = choose_best_decision(decisions)
        if best is None:
            continue
        analyzed += 1

        signal_key: str | None = None
        outcome: SignalOutcome | None = None
        if best.side in {"LONG", "SHORT"}:
            signal_key = stable_signal_key(best)
            if signal_key not in seen_signal_keys:
                seen_signal_keys.add(signal_key)
                future = tuple(
                    candle
                    for candle in source_setup
                    if candle.open_time > best.last_closed_bar
                )
                horizon_end = _horizon_end(best, study.horizon_bars, setup_interval)
                outcome = evaluate_signal_outcome(
                    best,
                    future,
                    horizon_end=horizon_end,
                    evaluated_at=bundle.manifest.as_of,
                )
                outcomes.append(outcome)
                if outcome_repository is not None:
                    outcome_repository.upsert(outcome)

        records.append(
            ReplayDecisionRecord(
                as_of=cutoff,
                decision_id=decision_fingerprint(best),
                signal_key=signal_key,
                decision=best,
                outcome=outcome,
            )
        )

    counts = Counter(outcome.status for outcome in outcomes)
    study_id = _study_id(bundle, context, scanner, study)
    return ReplayStudyResult(
        schema_version=REPLAY_STUDY_SCHEMA_VERSION,
        study_id=study_id,
        bundle_sha256=bundle.manifest.bundle_sha256,
        provider_id=bundle.manifest.provider_id,
        canonical_symbol=bundle.manifest.canonical_symbol,
        analyzed_cutoffs=analyzed,
        skipped_insufficient_history=skipped_history,
        skipped_missing_context=skipped_context,
        decision_records=tuple(records),
        outcome_counts=dict(sorted(counts.items())),
        unique_tradable_signals=len(seen_signal_keys),
        binary_resolved_count=sum(counts.get(key, 0) for key in ("WIN", "LOSS")),
    )


def stable_signal_key(decision: TradingDecision) -> str:
    if decision.side not in {"LONG", "SHORT"}:
        raise ValueError("stable signal key requires a tradable decision")
    payload = {
        "provider_id": decision.provider_id,
        "canonical_symbol": decision.canonical_symbol,
        "side": decision.side,
        "setup_type": decision.setup_type,
        "primary_level_id": decision.primary_level_id,
        "entry": _decimal(decision.entry),
        "stop": _decimal(decision.stop),
        "target": _decimal(decision.target),
    }
    return _digest(payload)


def write_replay_study(path: str | Path, result: ReplayStudyResult) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        manifest = {
            "record_type": "manifest",
            "schema_version": result.schema_version,
            "study_id": result.study_id,
            "bundle_sha256": result.bundle_sha256,
            "provider_id": result.provider_id,
            "canonical_symbol": result.canonical_symbol,
            "analyzed_cutoffs": result.analyzed_cutoffs,
            "skipped_insufficient_history": result.skipped_insufficient_history,
            "skipped_missing_context": result.skipped_missing_context,
            "outcome_counts": dict(result.outcome_counts),
            "unique_tradable_signals": result.unique_tradable_signals,
            "binary_resolved_count": result.binary_resolved_count,
            "estimated_probability": None,
        }
        handle.write(json.dumps(manifest, sort_keys=True, ensure_ascii=True) + "\n")
        for record in result.decision_records:
            payload = {
                "record_type": "decision",
                "as_of": _time(record.as_of),
                "decision_id": record.decision_id,
                "signal_key": record.signal_key,
                "decision": _jsonable(asdict(record.decision)),
                "outcome": _jsonable(asdict(record.outcome)) if record.outcome is not None else None,
            }
            handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    return target


def write_replay_context(path: str | Path, context: ReplayStudyContext) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": REPLAY_CONTEXT_SCHEMA_VERSION,
        "instrument": _serialize_instrument(context.instrument),
        "max_context_age_seconds": context.max_context_age_seconds,
        "liquidity_points": [
            {
                "timestamp": _time(point.timestamp),
                "liquidity_score": format(point.liquidity_score, "f"),
                "liquidity_rank": point.liquidity_rank,
                "universe_size": point.universe_size,
            }
            for point in context.liquidity_points
        ],
    }
    target.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    return target


def load_replay_context(path: str | Path) -> ReplayStudyContext:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != REPLAY_CONTEXT_SCHEMA_VERSION:
        raise ValueError("unsupported replay context schema version")
    instrument = _deserialize_instrument(payload["instrument"])
    points = tuple(
        ReplayLiquidityPoint(
            timestamp=_parse_time(item["timestamp"]),
            liquidity_score=Decimal(str(item["liquidity_score"])),
            liquidity_rank=int(item["liquidity_rank"]),
            universe_size=int(item["universe_size"]),
        )
        for item in payload["liquidity_points"]
    )
    return ReplayStudyContext(
        instrument=instrument,
        liquidity_points=points,
        max_context_age_seconds=float(payload.get("max_context_age_seconds", 300.0)),
    )


def _validate_identity(bundle: MTFReplayBundle, context: ReplayStudyContext) -> None:
    manifest = bundle.manifest
    instrument = context.instrument
    if instrument.provider_id != manifest.provider_id or instrument.symbol != manifest.canonical_symbol:
        raise ValueError("replay context instrument does not match bundle")
    if (instrument.provider_symbol or instrument.symbol) != manifest.provider_symbol:
        raise ValueError("replay context provider_symbol does not match bundle")
    if instrument.price_tick is None or instrument.price_tick <= 0:
        raise ValueError("replay context requires confirmed positive price_tick")


def _horizon_end(decision: TradingDecision, horizon_bars: int | None, interval: str) -> datetime | None:
    if horizon_bars is None:
        return None
    next_open = decision.last_closed_bar + timedelta(milliseconds=1)
    return next_open + timedelta(seconds=interval_seconds(interval) * horizon_bars)


def _study_id(bundle: MTFReplayBundle, context: ReplayStudyContext, scanner: RuntimeScannerConfig, study: ReplayStudyConfig) -> str:
    payload = {
        "bundle_sha256": bundle.manifest.bundle_sha256,
        "instrument": _serialize_instrument(context.instrument),
        "liquidity_points": [
            [_time(point.timestamp), format(point.liquidity_score, "f"), point.liquidity_rank, point.universe_size]
            for point in context.liquidity_points
        ],
        "max_context_age_seconds": context.max_context_age_seconds,
        "history": dict(scanner.history.interval_counts),
        "setup_interval": scanner.setup_interval,
        "ma_method": scanner.ma_method,
        "step_bars": study.step_bars,
        "horizon_bars": study.horizon_bars,
        "start": _time(study.start) if study.start is not None else None,
        "end": _time(study.end) if study.end is not None else None,
    }
    return _digest(payload)


def _serialize_instrument(instrument: NormalizedInstrument) -> dict[str, object]:
    return {
        "provider_id": instrument.provider_id,
        "symbol": instrument.symbol,
        "base_asset": instrument.base_asset,
        "quote_asset": instrument.quote_asset,
        "market_type": instrument.market_type,
        "contract_type": instrument.contract_type,
        "status": instrument.status,
        "price_tick": _decimal(instrument.price_tick),
        "quantity_step": _decimal(instrument.quantity_step),
        "provider_symbol": instrument.provider_symbol,
        "metadata": dict(instrument.metadata),
    }


def _deserialize_instrument(payload: Mapping[str, object]) -> NormalizedInstrument:
    metadata = payload.get("metadata")
    return NormalizedInstrument(
        provider_id=str(payload["provider_id"]),
        symbol=str(payload["symbol"]),
        base_asset=str(payload["base_asset"]),
        quote_asset=str(payload["quote_asset"]),
        market_type=str(payload["market_type"]),
        contract_type=str(payload["contract_type"]),
        status=str(payload["status"]),
        price_tick=_optional_decimal(payload.get("price_tick")),
        quantity_step=_optional_decimal(payload.get("quantity_step")),
        provider_symbol=str(payload["provider_symbol"]) if payload.get("provider_symbol") is not None else None,
        metadata={str(key): str(value) for key, value in metadata.items()} if isinstance(metadata, dict) else {},
    )


def _jsonable(value: object) -> object:
    if isinstance(value, datetime):
        return _time(value)
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _digest(payload: Mapping[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _optional_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _time(value: datetime) -> str:
    require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    require_utc(parsed)
    return parsed.astimezone(timezone.utc)
