from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ktrader.models import NormalizedInstrument, NormalizedTicker


@dataclass(frozen=True, slots=True)
class UniverseConfig:
    quote_asset: str = "USDT"
    price_limit_enabled: bool = True
    max_price: Decimal = Decimal("3")
    max_candidates: int = 50


@dataclass(frozen=True, slots=True)
class UniverseCandidate:
    instrument: NormalizedInstrument
    ticker: NormalizedTicker
    liquidity_score: Decimal


def build_universe(
    instruments: list[NormalizedInstrument],
    tickers: list[NormalizedTicker],
    config: UniverseConfig,
) -> list[UniverseCandidate]:
    ticker_by_symbol = {t.symbol: t for t in tickers}
    candidates: list[UniverseCandidate] = []

    for instrument in instruments:
        if not instrument.is_tradable_perpetual:
            continue
        if instrument.quote_asset != config.quote_asset:
            continue
        ticker = ticker_by_symbol.get(instrument.symbol)
        if ticker is None or ticker.last_price <= 0:
            continue
        if config.price_limit_enabled and ticker.last_price > config.max_price:
            continue
        score = liquidity_score(ticker)
        if score <= 0:
            continue
        candidates.append(UniverseCandidate(instrument, ticker, score))

    candidates.sort(key=lambda item: item.liquidity_score, reverse=True)
    return candidates[: config.max_candidates]


def liquidity_score(ticker: NormalizedTicker) -> Decimal:
    """Deterministic v1 liquidity score based on confirmed normalized fields.

    Quote turnover is the main cross-provider comparable input. Spread penalizes
    poor executable liquidity when bid/ask data is available. No missing field
    is fabricated.
    """
    turnover = ticker.quote_volume_24h or Decimal("0")
    if turnover <= 0:
        return Decimal("0")

    spread_bps = ticker.spread_bps
    spread_penalty = Decimal("1")
    if spread_bps is not None and spread_bps > 0:
        spread_penalty = Decimal("1") + spread_bps / Decimal("10")

    return turnover / spread_penalty
