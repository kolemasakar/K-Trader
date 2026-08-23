from __future__ import annotations

from dataclasses import dataclass

from ktrader.market.universe import UniverseCandidate, UniverseConfig, build_universe
from ktrader.models import NormalizedInstrument, NormalizedTicker
from ktrader.providers.base import MarketDataProvider, ProviderError


@dataclass(frozen=True, slots=True)
class UniverseSnapshot:
    provider_id: str
    candidates: tuple[UniverseCandidate, ...]
    instruments: tuple[NormalizedInstrument, ...] = ()
    tickers: tuple[NormalizedTicker, ...] = ()


@dataclass(frozen=True, slots=True)
class ProviderFailure:
    provider_id: str
    error: str


@dataclass(frozen=True, slots=True)
class ProviderSelection:
    snapshot: UniverseSnapshot
    failures: tuple[ProviderFailure, ...] = ()


async def load_universe(
    provider: MarketDataProvider,
    config: UniverseConfig,
) -> UniverseSnapshot:
    """Build one coherent universe using one provider only.

    The raw normalized instruments/tickers are retained beside the ranked
    candidates so operations/research capture can persist the exact inputs from
    the same provider request cycle without issuing a second market-data fetch.
    """
    instruments = await provider.list_instruments()
    tickers = await provider.get_tickers()
    candidates = build_universe(instruments, tickers, config)
    return UniverseSnapshot(
        provider.provider_id,
        tuple(candidates),
        tuple(instruments),
        tuple(tickers),
    )


async def select_first_available_provider(
    providers: list[MarketDataProvider],
    config: UniverseConfig,
) -> ProviderSelection:
    """Use provider priority order without ever combining market series."""
    failures: list[ProviderFailure] = []
    for provider in providers:
        try:
            snapshot = await load_universe(provider, config)
        except ProviderError as exc:
            failures.append(ProviderFailure(provider.provider_id, str(exc)))
            continue
        return ProviderSelection(snapshot, tuple(failures))
    detail = "; ".join(f"{x.provider_id}: {x.error}" for x in failures)
    raise ProviderError(f"No market-data provider available. {detail}")
