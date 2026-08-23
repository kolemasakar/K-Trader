from datetime import datetime, timezone
from decimal import Decimal

from ktrader.market.service import select_first_available_provider
from ktrader.market.universe import UniverseConfig
from ktrader.models import NormalizedInstrument, NormalizedTicker, ProviderCapabilities
from ktrader.providers.base import MarketDataProvider, ProviderError


class StubProvider(MarketDataProvider):
    def __init__(self, provider_id: str, fail: bool = False):
        self.provider_id = provider_id
        self.fail = fail

    @property
    def capabilities(self):
        return ProviderCapabilities(self.provider_id, True, frozenset({"5m"}))

    async def list_instruments(self):
        if self.fail:
            raise ProviderError("offline")
        return [
            NormalizedInstrument(
                provider_id=self.provider_id,
                symbol="SUIUSDT",
                provider_symbol="native-sui",
                base_asset="SUI",
                quote_asset="USDT",
                market_type="LINEAR_FUTURES",
                contract_type="PERPETUAL",
                status="TRADING",
            )
        ]

    async def get_tickers(self):
        return [
            NormalizedTicker(
                provider_id=self.provider_id,
                symbol="SUIUSDT",
                timestamp=datetime.now(timezone.utc),
                last_price=Decimal("1"),
                quote_volume_24h=Decimal("1000000"),
            )
        ]

    async def get_candles(self, instrument, interval, *, limit):
        return []


async def test_failover_selects_new_coherent_provider_snapshot():
    selection = await select_first_available_provider(
        [StubProvider("primary", fail=True), StubProvider("secondary")],
        UniverseConfig(),
    )
    assert selection.snapshot.provider_id == "secondary"
    assert selection.snapshot.candidates[0].instrument.provider_id == "secondary"
    assert selection.snapshot.candidates[0].ticker.provider_id == "secondary"
    assert [x.provider_id for x in selection.failures] == ["primary"]
