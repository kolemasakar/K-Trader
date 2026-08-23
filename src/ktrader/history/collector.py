from __future__ import annotations

from datetime import datetime, timezone

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

    Phase 11B deliberately uses the existing provider contract without adding a
    second historical API surface. Deep multi-page archival collection can be
    added later while preserving the dataset format.
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
            f"max_bars exceeds provider page capacity {page_capacity}; deep pagination is not enabled in Phase 11B"
        )
    current = fetched_at or datetime.now(timezone.utc)
    _require_utc(current)
    request_limit = min(page_capacity, max_bars + 1)
    page = await provider.get_candles(instrument, interval, limit=request_limit)
    provider.ensure_chronological(page)
    closed = [candle for candle in page if candle.closed]
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


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be timezone-aware UTC")
