from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ktrader.history.dataset import HistoricalDataset, build_history_dataset
from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedInstrument
from ktrader.providers.base import MarketDataProvider, ProviderError


async def collect_provider_history(
    provider: MarketDataProvider,
    instrument: NormalizedInstrument,
    interval: str,
    *,
    max_bars: int = 1000,
    fetched_at: datetime | None = None,
) -> HistoricalDataset:
    """Capture the latest coherent provider-recorded closed-candle page.

    This Phase 11B compatibility path remains intentionally bounded to one
    provider-native page. Phase 11C deep archives use
    ``collect_deep_provider_history`` below.
    """
    if instrument.provider_id != provider.provider_id:
        raise ValueError("instrument/provider identity mismatch")
    provider.validate_interval(interval)
    if max_bars <= 0:
        raise ValueError("max_bars must be positive")
    page_capacity = provider.capabilities.max_kline_page_size
    if page_capacity is None or page_capacity <= 0:
        raise ProviderError("provider has no historical page capacity")
    if max_bars > page_capacity:
        raise ValueError(
            f"max_bars exceeds provider page capacity {page_capacity}; use collect_deep_provider_history"
        )
    current = fetched_at or datetime.now(timezone.utc)
    _require_utc(current)
    request_limit = min(page_capacity, max_bars + 1)
    page = await provider.get_candles(instrument, interval, limit=request_limit)
    provider.ensure_chronological(page)
    closed = [candle for candle in page if candle.closed and candle.close_time <= current]
    if not closed:
        raise ProviderError("provider returned no closed candles")
    candles = closed[-max_bars:]
    validate_sequence(
        candles,
        provider_id=provider.provider_id,
        symbol=instrument.symbol,
        interval=interval,
        require_closed=True,
        require_contiguous=True,
    )
    return build_history_dataset(
        candles,
        provider_symbol=instrument.provider_symbol or instrument.symbol,
        requested_bars=max_bars,
        fetched_at=current,
    )


async def collect_deep_provider_history(
    provider: MarketDataProvider,
    instrument: NormalizedInstrument,
    interval: str,
    *,
    max_bars: int,
    fetched_at: datetime | None = None,
    max_pages: int = 100,
) -> HistoricalDataset:
    """Collect an exact-depth closed history by paging backward provider-side.

    Pages are requested with an explicit UTC end cursor. Candle identity is
    deduplicated by open time, the cursor must make backward progress, and the
    final exact-depth series must be single-provider, closed and contiguous.
    No page from another provider may be spliced into the archive.
    """
    if instrument.provider_id != provider.provider_id:
        raise ValueError("instrument/provider identity mismatch")
    provider.validate_interval(interval)
    if max_bars <= 0:
        raise ValueError("max_bars must be positive")
    if max_pages <= 0:
        raise ValueError("max_pages must be positive")
    page_capacity = provider.capabilities.max_kline_page_size
    if page_capacity is None or page_capacity <= 0:
        raise ProviderError("provider has no historical page capacity")

    current = fetched_at or datetime.now(timezone.utc)
    _require_utc(current)
    cursor = current
    candles_by_open: dict[datetime, object] = {}
    prior_cursor: datetime | None = None

    for _ in range(max_pages):
        remaining = max_bars - len(candles_by_open)
        if remaining <= 0:
            break
        request_limit = min(page_capacity, remaining + 1)
        try:
            page = await provider.get_historical_candles(
                instrument,
                interval,
                limit=request_limit,
                end_time=cursor,
            )
        except NotImplementedError as exc:
            raise ProviderError(
                f"{provider.provider_id} does not support deep historical pagination"
            ) from exc
        provider.ensure_chronological(page)
        if not page:
            break

        for candle in page:
            if candle.provider_id != provider.provider_id or candle.symbol != instrument.symbol or candle.interval != interval:
                raise ProviderError("historical page identity mismatch")
            if candle.closed and candle.close_time <= current:
                candles_by_open[candle.open_time] = candle

        oldest_open = min(candle.open_time for candle in page)
        next_cursor = oldest_open - timedelta(milliseconds=1)
        if prior_cursor is not None and next_cursor >= prior_cursor:
            raise ProviderError("historical pagination cursor did not move backward")
        if next_cursor >= cursor:
            raise ProviderError("historical pagination cursor did not move backward")
        prior_cursor = cursor
        cursor = next_cursor

    if len(candles_by_open) < max_bars:
        raise ProviderError(
            f"insufficient deep history: requested {max_bars}, collected {len(candles_by_open)} within {max_pages} pages"
        )

    materialized = sorted(candles_by_open.values(), key=lambda candle: candle.open_time)
    candles = materialized[-max_bars:]
    validate_sequence(
        candles,
        provider_id=provider.provider_id,
        symbol=instrument.symbol,
        interval=interval,
        require_closed=True,
        require_contiguous=True,
    )
    return build_history_dataset(
        candles,
        provider_symbol=instrument.provider_symbol or instrument.symbol,
        requested_bars=max_bars,
        fetched_at=current,
    )


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be timezone-aware UTC")
