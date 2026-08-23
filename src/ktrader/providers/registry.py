from __future__ import annotations

from collections.abc import Callable

from ktrader.providers.base import MarketDataProvider
from ktrader.providers.binance_usdm import BinanceUSDMProvider
from ktrader.providers.bybit_linear import BybitLinearProvider


ProviderFactory = Callable[[], MarketDataProvider]

PROVIDERS: dict[str, ProviderFactory] = {
    "binance_usdm": BinanceUSDMProvider,
    "bybit_linear": BybitLinearProvider,
}


def create_provider(provider_id: str) -> MarketDataProvider:
    try:
        return PROVIDERS[provider_id]()
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider_id}") from exc
