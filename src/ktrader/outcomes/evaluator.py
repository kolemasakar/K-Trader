from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import json
from collections.abc import Sequence

from ktrader.engine.models import TradingDecision
from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle


@dataclass(frozen=True, slots=True)
class SignalOutcome:
    decision_id: str
    provider_id: str
    canonical_symbol: str
    side: str
    grade: str
    setup_score: int
    setup_type: str
    engine_version: str
    decision_time: datetime
    entry: Decimal | None
    stop: Decimal | None
    target: Decimal | None
    planned_rr: Decimal | None
    status: str
    entry_bar_open_time: datetime | None
    resolved_bar_open_time: datetime | None
    bars_to_entry: int | None
    bars_in_trade: int | None
    outcome_r: Decimal | None
    reason: str | None
    evaluated_at: datetime

    @property
    def binary_resolved(self) -> bool:
        return self.status in {"WIN", "LOSS"}


def decision_fingerprint(decision: TradingDecision) -> str:
    payload = {
        "provider_id": decision.provider_id,
        "canonical_symbol": decision.canonical_symbol,
        "side": decision.side,
        "grade": decision.grade,
        "setup_score": decision.setup_score,
        "setup_type": decision.setup_type,
        "primary_level_id": decision.primary_level_id,
        "entry": _decimal(decision.entry),
        "stop": _decimal(decision.stop),
        "target": _decimal(decision.target),
        "rr": _decimal(decision.rr),
        "last_closed_bar": _time(decision.last_closed_bar),
        "generated_at": _time(decision.generated_at),
        "engine_version": decision.engine_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()


def evaluate_signal_outcome(
    decision: TradingDecision,
    future_candles: Sequence[NormalizedCandle],
    *,
    horizon_end: datetime | None = None,
    evaluated_at: datetime | None = None,
) -> SignalOutcome:
    """Evaluate target/stop touches from confirmed future OHLC bars.

    This is deliberately conservative. If entry and an exit level are touched
    in the same bar, or target and stop are both touched in one post-entry bar,
    the result is AMBIGUOUS because OHLC data cannot prove intrabar ordering.
    """
    now = evaluated_at or datetime.now(timezone.utc)
    _require_utc(now)
    if horizon_end is not None:
        _require_utc(horizon_end)
        if horizon_end <= decision.last_closed_bar:
            raise ValueError("horizon_end must be after decision last_closed_bar")

    decision_id = decision_fingerprint(decision)
    if decision.side not in {"LONG", "SHORT"}:
        return _outcome(
            decision,
            decision_id=decision_id,
            status="NOT_ELIGIBLE",
            reason="DECISION_NOT_TRADABLE",
            evaluated_at=now,
        )
    if decision.entry is None or decision.stop is None or decision.target is None:
        return _outcome(
            decision,
            decision_id=decision_id,
            status="NOT_ELIGIBLE",
            reason="MISSING_GEOMETRY",
            evaluated_at=now,
        )
    if not future_candles:
        return _outcome(
            decision,
            decision_id=decision_id,
            status="PENDING_ENTRY",
            reason="NO_FUTURE_BARS",
            evaluated_at=now,
        )

    first = future_candles[0]
    validate_sequence(
        future_candles,
        provider_id=decision.provider_id,
        symbol=decision.canonical_symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )
    if first.open_time <= decision.last_closed_bar:
        raise ValueError("future outcome bars must begin after decision last_closed_bar")

    bars = [
        candle
        for candle in future_candles
        if horizon_end is None or candle.open_time < horizon_end
    ]
    entered_at: datetime | None = None
    entry_index: int | None = None

    for index, candle in enumerate(bars):
        if entered_at is None:
            if not _touches(candle, decision.entry):
                continue
            entry_index = index
            entered_at = candle.open_time
            stop_hit = _touches(candle, decision.stop)
            target_hit = _touches(candle, decision.target)
            if stop_hit or target_hit:
                return _outcome(
                    decision,
                    decision_id=decision_id,
                    status="AMBIGUOUS",
                    entry_bar_open_time=entered_at,
                    resolved_bar_open_time=candle.open_time,
                    bars_to_entry=index + 1,
                    bars_in_trade=1,
                    reason="ENTRY_AND_EXIT_LEVEL_TOUCHED_SAME_BAR",
                    evaluated_at=now,
                )
            continue

        stop_hit = _touches(candle, decision.stop)
        target_hit = _touches(candle, decision.target)
        bars_in_trade = index - entry_index + 1 if entry_index is not None else None
        if stop_hit and target_hit:
            return _outcome(
                decision,
                decision_id=decision_id,
                status="AMBIGUOUS",
                entry_bar_open_time=entered_at,
                resolved_bar_open_time=candle.open_time,
                bars_to_entry=(entry_index + 1) if entry_index is not None else None,
                bars_in_trade=bars_in_trade,
                reason="TARGET_AND_STOP_TOUCHED_SAME_BAR",
                evaluated_at=now,
            )
        if target_hit:
            return _outcome(
                decision,
                decision_id=decision_id,
                status="WIN",
                entry_bar_open_time=entered_at,
                resolved_bar_open_time=candle.open_time,
                bars_to_entry=(entry_index + 1) if entry_index is not None else None,
                bars_in_trade=bars_in_trade,
                outcome_r=_planned_win_r(decision),
                evaluated_at=now,
            )
        if stop_hit:
            return _outcome(
                decision,
                decision_id=decision_id,
                status="LOSS",
                entry_bar_open_time=entered_at,
                resolved_bar_open_time=candle.open_time,
                bars_to_entry=(entry_index + 1) if entry_index is not None else None,
                bars_in_trade=bars_in_trade,
                outcome_r=Decimal("-1"),
                evaluated_at=now,
            )

    expired = horizon_end is not None and future_candles[-1].close_time + timedelta(milliseconds=1) >= horizon_end
    if entered_at is None:
        return _outcome(
            decision,
            decision_id=decision_id,
            status="EXPIRED_NO_ENTRY" if expired else "PENDING_ENTRY",
            reason="HORIZON_REACHED_WITHOUT_ENTRY" if expired else "ENTRY_NOT_YET_TOUCHED",
            evaluated_at=now,
        )
    return _outcome(
        decision,
        decision_id=decision_id,
        status="EXPIRED_OPEN" if expired else "OPEN",
        entry_bar_open_time=entered_at,
        bars_to_entry=(entry_index + 1) if entry_index is not None else None,
        bars_in_trade=(len(bars) - entry_index) if entry_index is not None else None,
        reason="HORIZON_REACHED_WITH_OPEN_POSITION" if expired else "NO_TERMINAL_LEVEL_TOUCHED",
        evaluated_at=now,
    )


def _outcome(
    decision: TradingDecision,
    *,
    decision_id: str,
    status: str,
    evaluated_at: datetime,
    entry_bar_open_time: datetime | None = None,
    resolved_bar_open_time: datetime | None = None,
    bars_to_entry: int | None = None,
    bars_in_trade: int | None = None,
    outcome_r: Decimal | None = None,
    reason: str | None = None,
) -> SignalOutcome:
    return SignalOutcome(
        decision_id=decision_id,
        provider_id=decision.provider_id,
        canonical_symbol=decision.canonical_symbol,
        side=decision.side,
        grade=decision.grade,
        setup_score=decision.setup_score,
        setup_type=decision.setup_type,
        engine_version=decision.engine_version,
        decision_time=decision.generated_at,
        entry=decision.entry,
        stop=decision.stop,
        target=decision.target,
        planned_rr=decision.rr,
        status=status,
        entry_bar_open_time=entry_bar_open_time,
        resolved_bar_open_time=resolved_bar_open_time,
        bars_to_entry=bars_to_entry,
        bars_in_trade=bars_in_trade,
        outcome_r=outcome_r,
        reason=reason,
        evaluated_at=evaluated_at,
    )


def _touches(candle: NormalizedCandle, price: Decimal) -> bool:
    return candle.low <= price <= candle.high


def _planned_win_r(decision: TradingDecision) -> Decimal:
    assert decision.entry is not None and decision.stop is not None and decision.target is not None
    risk = abs(decision.entry - decision.stop)
    if risk <= 0:
        raise ValueError("decision geometry has non-positive risk distance")
    return abs(decision.target - decision.entry) / risk


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _time(value: datetime) -> str:
    _require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be timezone-aware UTC")
