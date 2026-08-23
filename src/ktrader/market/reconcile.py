from __future__ import annotations

from dataclasses import dataclass

from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.providers.base import MarketDataProvider


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    interval: str
    fetched: int
    corrected: int
    inserted: int


def candles_equal(left: NormalizedCandle, right: NormalizedCandle) -> bool:
    return (
        left.provider_id == right.provider_id
        and left.symbol == right.symbol
        and left.interval == right.interval
        and left.open_time == right.open_time
        and left.close_time == right.close_time
        and left.open == right.open
        and left.high == right.high
        and left.low == right.low
        and left.close == right.close
        and left.volume == right.volume
        and left.quote_volume == right.quote_volume
        and left.trade_count == right.trade_count
        and left.taker_buy_volume == right.taker_buy_volume
        and left.taker_buy_quote_volume == right.taker_buy_quote_volume
        and left.closed == right.closed
    )


class ReconciliationService:
    def __init__(self, repository) -> None:
        self.repository = repository

    async def reconcile_interval(
        self,
        provider: MarketDataProvider,
        instrument: NormalizedInstrument,
        interval: str,
        *,
        limit: int = 3,
    ) -> ReconciliationResult:
        rows = await provider.get_candles(instrument, interval, limit=limit)
        closed = [candle for candle in rows if candle.closed]
        if not closed:
            return ReconciliationResult(interval, 0, 0, 0)
        validate_sequence(
            closed,
            provider_id=provider.provider_id,
            symbol=instrument.symbol,
            interval=interval,
            require_closed=True,
            require_contiguous=True,
        )
        existing = {
            candle.open_time: candle
            for candle in self.repository.load_recent(
                provider.provider_id,
                instrument.symbol,
                interval,
                limit=max(limit, len(closed)),
            )
        }
        corrected = 0
        inserted = 0
        for candle in closed:
            current = existing.get(candle.open_time)
            if current is None:
                inserted += 1
            elif not candles_equal(current, candle):
                corrected += 1
        self.repository.upsert_many(
            closed,
            source_kind="provider",
            derived_from_interval=None,
        )
        return ReconciliationResult(
            interval=interval,
            fetched=len(closed),
            corrected=corrected,
            inserted=inserted,
        )
