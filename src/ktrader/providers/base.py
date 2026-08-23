from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ktrader.models import (
    NormalizedCandle,
    NormalizedInstrument,
    NormalizedTicker,
    ProviderCapabilities,
)


class ProviderError(RuntimeError):
    """Provider response or connectivity error."""


class MarketDataProvider(ABC):
    provider_id: str

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities: ...

    @abstractmethod
    async def list_instruments(self) -> list[NormalizedInstrument]: ...

    @abstractmethod
    async def get_tickers(self) -> list[NormalizedTicker]: ...

    @abstractmethod
    async def get_candles(
        self,
        instrument: NormalizedInstrument,
        interval: str,
        *,
        limit: int,
    ) -> list[NormalizedCandle]: ...

    async def close(self) -> None:
        """Release provider resources."""

    def validate_interval(self, interval: str) -> None:
        if interval not in self.capabilities.intervals:
            raise ValueError(
                f"Interval {interval!r} is not supported by {self.provider_id}"
            )

    @staticmethod
    def ensure_chronological(candles: Sequence[NormalizedCandle]) -> None:
        times = [c.open_time for c in candles]
        if times != sorted(times):
            raise ProviderError("Provider returned non-chronological normalized candles")
