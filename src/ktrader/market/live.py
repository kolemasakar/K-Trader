from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from ktrader.market.aggregation import (
    PARENT_INTERVALS,
    aggregate_closed_candles,
    bucket_open_time,
    expected_child_count,
)
from ktrader.market.reconcile import ReconciliationService
from ktrader.market.timeframes import datetime_to_ms, interval_ms
from ktrader.market.validation import CandleValidationError, validate_candle
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.providers.base import MarketDataProvider
from ktrader.providers.live import LiveCandleEvent


@dataclass(frozen=True, slots=True)
class LiveConfig:
    base_interval: str = "5m"
    stale_after_seconds: float = 90.0
    reconnect_initial_seconds: float = 1.0
    reconnect_max_seconds: float = 30.0
    reconcile_every_closed_bars: int = 12
    reconcile_lookback: int = 3


@dataclass(slots=True)
class LiveSymbolState:
    provider_id: str
    symbol: str
    last_event_at: datetime | None = None
    last_closed_open_time: datetime | None = None
    current_open_candle: NormalizedCandle | None = None
    closed_bars_seen: int = 0
    reconnects: int = 0
    gap_recoveries: int = 0
    last_error: str | None = None

    def stale(self, *, now: datetime, stale_after_seconds: float) -> bool:
        if self.last_event_at is None:
            return True
        return (now - self.last_event_at).total_seconds() > stale_after_seconds


class LiveMarketDataService:
    def __init__(self, repository, *, config: LiveConfig | None = None) -> None:
        self.repository = repository
        self.config = config or LiveConfig()
        self.reconciler = ReconciliationService(repository)
        self.states: dict[tuple[str, str], LiveSymbolState] = {}

    def state_for(self, instrument: NormalizedInstrument) -> LiveSymbolState:
        key = (instrument.provider_id, instrument.symbol)
        return self.states.setdefault(
            key,
            LiveSymbolState(instrument.provider_id, instrument.symbol),
        )

    async def process_event(
        self,
        provider: MarketDataProvider,
        instrument: NormalizedInstrument,
        event: LiveCandleEvent,
    ) -> None:
        candle = event.candle
        if candle.interval != self.config.base_interval:
            raise CandleValidationError("Live service received non-base interval")
        validate_candle(
            candle,
            provider_id=provider.provider_id,
            symbol=instrument.symbol,
            interval=self.config.base_interval,
        )
        state = self.state_for(instrument)
        state.last_event_at = event.received_at
        state.last_error = None
        if not candle.closed:
            state.current_open_candle = candle
            return

        latest = self.repository.latest(
            provider.provider_id,
            instrument.symbol,
            self.config.base_interval,
        )
        if latest is not None:
            delta = datetime_to_ms(candle.open_time) - datetime_to_ms(
                latest.open_time
            )
            step = interval_ms(self.config.base_interval)
            if delta < 0:
                return
            if delta == 0:
                self.repository.upsert_many(
                    [candle],
                    source_kind="provider",
                    derived_from_interval=None,
                )
                state.last_closed_open_time = candle.open_time
                return
            if delta > step:
                state.gap_recoveries += 1
                missing = max(0, (delta // step) - 1)
                requested = max(self.config.reconcile_lookback, missing + 2)
                page_size = provider.capabilities.max_kline_page_size
                if page_size is not None:
                    requested = min(requested, page_size)
                await self.reconciler.reconcile_interval(
                    provider,
                    instrument,
                    self.config.base_interval,
                    limit=requested,
                )
                latest = self.repository.latest(
                    provider.provider_id,
                    instrument.symbol,
                    self.config.base_interval,
                )
                if latest is None:
                    raise CandleValidationError(
                        "Live 5m gap remains after REST reconciliation"
                    )
                remaining = datetime_to_ms(candle.open_time) - datetime_to_ms(
                    latest.open_time
                )
                if remaining > step:
                    raise CandleValidationError(
                        "Live 5m gap remains after REST reconciliation"
                    )

        self.repository.upsert_many(
            [candle],
            source_kind="provider",
            derived_from_interval=None,
        )
        state.current_open_candle = None
        state.last_closed_open_time = candle.open_time
        state.closed_bars_seen += 1
        self._aggregate_completed_parents(
            provider.provider_id,
            instrument.symbol,
            candle,
        )

        if (
            self.config.reconcile_every_closed_bars > 0
            and state.closed_bars_seen
            % self.config.reconcile_every_closed_bars
            == 0
        ):
            await self.reconciler.reconcile_interval(
                provider,
                instrument,
                self.config.base_interval,
                limit=self.config.reconcile_lookback,
            )

    def _aggregate_completed_parents(
        self,
        provider_id: str,
        symbol: str,
        closed_5m: NormalizedCandle,
    ) -> None:
        for parent in PARENT_INTERVALS:
            bucket = bucket_open_time(closed_5m.open_time, parent)
            parent_end_open_ms = (
                datetime_to_ms(bucket)
                + interval_ms(parent)
                - interval_ms(self.config.base_interval)
            )
            if datetime_to_ms(closed_5m.open_time) != parent_end_open_ms:
                continue
            required = expected_child_count(
                parent,
                self.config.base_interval,
            )
            children = self.repository.load_recent(
                provider_id,
                symbol,
                self.config.base_interval,
                limit=required,
            )
            if len(children) != required or children[0].open_time != bucket:
                continue
            aggregate = aggregate_closed_candles(
                children,
                parent_interval=parent,
                child_interval=self.config.base_interval,
            )
            self.repository.upsert_many(
                [aggregate],
                source_kind="aggregate",
                derived_from_interval=self.config.base_interval,
            )

    async def run(
        self,
        provider: MarketDataProvider,
        instruments: Sequence[NormalizedInstrument],
    ) -> None:
        backoff = self.config.reconnect_initial_seconds
        while True:
            try:
                stream = provider.stream_candles(
                    instruments,
                    self.config.base_interval,
                )
                while True:
                    event = await asyncio.wait_for(
                        anext(stream),
                        timeout=self.config.stale_after_seconds,
                    )
                    instrument = _instrument_for_event(instruments, event)
                    await self.process_event(provider, instrument, event)
                    backoff = self.config.reconnect_initial_seconds
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                for instrument in instruments:
                    state = self.state_for(instrument)
                    state.reconnects += 1
                    state.last_error = f"{type(exc).__name__}: {exc}"
                await asyncio.sleep(backoff)
                backoff = min(
                    self.config.reconnect_max_seconds,
                    max(
                        backoff * 2,
                        self.config.reconnect_initial_seconds,
                    ),
                )


def _instrument_for_event(
    instruments: Sequence[NormalizedInstrument],
    event: LiveCandleEvent,
) -> NormalizedInstrument:
    for instrument in instruments:
        if (
            instrument.provider_id == event.candle.provider_id
            and instrument.symbol == event.candle.symbol
        ):
            return instrument
    raise CandleValidationError(
        "Live event does not map to subscribed instrument"
    )
