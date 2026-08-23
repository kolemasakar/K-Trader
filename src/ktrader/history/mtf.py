from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from ktrader.history.bundle import MTFReplayBundle, build_mtf_bundle
from ktrader.history.collector import collect_deep_provider_history
from ktrader.history.dataset import HistoricalDataset
from ktrader.market.timeframes import CANONICAL_INTERVALS, require_utc
from ktrader.models import NormalizedInstrument
from ktrader.providers.base import MarketDataProvider


DEFAULT_MTF_REPLAY_DEPTHS: Mapping[str, int] = {
    "1d": 250,
    "4h": 250,
    "1h": 250,
    "15m": 250,
    "5m": 300,
}


async def collect_mtf_history_bundle(
    provider: MarketDataProvider,
    instrument: NormalizedInstrument,
    *,
    bars_by_interval: Mapping[str, int] = DEFAULT_MTF_REPLAY_DEPTHS,
    as_of: datetime | None = None,
    max_pages_per_interval: int = 100,
) -> MTFReplayBundle:
    """Collect a coherent provider-native MTF archive at one UTC cutoff.

    Each timeframe is paged independently through the same provider. The shared
    ``as_of`` cutoff prevents later-closing candles from leaking into an older
    replay snapshot. Provider fallback/splicing is intentionally prohibited.
    """
    if instrument.provider_id != provider.provider_id:
        raise ValueError("instrument/provider identity mismatch")
    cutoff = as_of or datetime.now(timezone.utc)
    require_utc(cutoff)
    if set(bars_by_interval) != set(CANONICAL_INTERVALS):
        raise ValueError("bars_by_interval must define all canonical intervals exactly")

    datasets: dict[str, HistoricalDataset] = {}
    for interval in CANONICAL_INTERVALS:
        bars = int(bars_by_interval[interval])
        if bars <= 0:
            raise ValueError("MTF replay depths must be positive")
        datasets[interval] = await collect_deep_provider_history(
            provider,
            instrument,
            interval,
            max_bars=bars,
            fetched_at=cutoff,
            max_pages=max_pages_per_interval,
        )
    return build_mtf_bundle(datasets, as_of=cutoff)
