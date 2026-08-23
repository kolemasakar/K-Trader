from datetime import datetime, timezone
from decimal import Decimal

from ktrader.market.universe import UniverseConfig, build_universe
from ktrader.models import NormalizedInstrument, NormalizedTicker


def instrument(symbol: str, status: str = "TRADING", contract: str = "PERPETUAL"):
    return NormalizedInstrument(
        provider_id="p",
        symbol=symbol,
        base_asset=symbol.removesuffix("USDT"),
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type=contract,
        status=status,
    )


def ticker(symbol: str, price: str, turnover: str, bid=None, ask=None):
    return NormalizedTicker(
        provider_id="p",
        symbol=symbol,
        timestamp=datetime.now(timezone.utc),
        last_price=Decimal(price),
        quote_volume_24h=Decimal(turnover),
        bid_price=Decimal(bid) if bid else None,
        ask_price=Decimal(ask) if ask else None,
    )


def test_universe_filters_and_ranks_liquidity():
    instruments = [
        instrument("AAAUSDT"),
        instrument("BBBUSDT"),
        instrument("CCCUSDT", status="CLOSED"),
        instrument("DDDUSDT", contract="DELIVERY"),
    ]
    tickers = [
        ticker("AAAUSDT", "1.0", "1000000", "0.999", "1.001"),
        ticker("BBBUSDT", "2.0", "2000000", "1.999", "2.001"),
        ticker("CCCUSDT", "1.0", "9000000"),
        ticker("DDDUSDT", "1.0", "9000000"),
    ]
    result = build_universe(instruments, tickers, UniverseConfig(max_candidates=10))
    assert [x.instrument.symbol for x in result] == ["BBBUSDT", "AAAUSDT"]


def test_price_limit_can_be_disabled():
    instruments = [instrument("BTCUSDT")]
    tickers = [ticker("BTCUSDT", "70000", "100000000")]
    enabled = build_universe(instruments, tickers, UniverseConfig())
    disabled = build_universe(
        instruments,
        tickers,
        UniverseConfig(price_limit_enabled=False),
    )
    assert enabled == []
    assert len(disabled) == 1
