from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

import pytest

from ktrader.history import (
    append_universe_snapshot,
    build_universe_archive,
    build_universe_snapshot,
    load_universe_archive,
    write_universe_archive,
)
from ktrader.market.universe import UniverseConfig
from ktrader.models import NormalizedInstrument, NormalizedTicker
from ktrader.replay import build_study_cohort, load_study_cohort, write_study_cohort


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)
CONFIG = UniverseConfig(max_price=Decimal("3"), max_candidates=2)


def _instrument(symbol: str, base: str, *, provider: str = "bybit_linear") -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=provider,
        symbol=symbol,
        provider_symbol=symbol,
        base_asset=base,
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def _ticker(
    symbol: str,
    *,
    timestamp: datetime,
    last: str,
    quote_volume: str,
    bid: str,
    ask: str,
    provider: str = "bybit_linear",
) -> NormalizedTicker:
    return NormalizedTicker(
        provider_id=provider,
        symbol=symbol,
        timestamp=timestamp,
        last_price=Decimal(last),
        quote_volume_24h=Decimal(quote_volume),
        base_volume_24h=Decimal("100000"),
        trade_count_24h=1000,
        bid_price=Decimal(bid),
        ask_price=Decimal(ask),
    )


def _snapshot(captured_at: datetime, *, reverse: bool = False):
    instruments = [_instrument("SUIUSDT", "SUI"), _instrument("DOGEUSDT", "DOGE")]
    timestamp = captured_at - timedelta(seconds=1)
    if reverse:
        tickers = [
            _ticker("SUIUSDT", timestamp=timestamp, last="0.8", quote_volume="5000000", bid="0.7999", ask="0.8001"),
            _ticker("DOGEUSDT", timestamp=timestamp, last="0.2", quote_volume="1000000", bid="0.1999", ask="0.2001"),
        ]
    else:
        tickers = [
            _ticker("SUIUSDT", timestamp=timestamp, last="0.8", quote_volume="1000000", bid="0.799", ask="0.801"),
            _ticker("DOGEUSDT", timestamp=timestamp, last="0.2", quote_volume="2000000", bid="0.1999", ask="0.2001"),
        ]
    return build_universe_snapshot("bybit_linear", instruments, tickers, CONFIG, captured_at=captured_at)


def test_snapshot_preserves_live_rank_and_raw_liquidity_inputs():
    snapshot = _snapshot(T0)
    assert snapshot.universe_size == 2
    assert [member.instrument.symbol for member in snapshot.members] == ["DOGEUSDT", "SUIUSDT"]
    assert [member.rank for member in snapshot.members] == [1, 2]
    first = snapshot.members[0]
    assert first.ticker.quote_volume_24h == Decimal("2000000")
    assert first.ticker.bid_price == Decimal("0.1999")
    assert first.ticker.ask_price == Decimal("0.2001")
    assert len(snapshot.content_sha256) == 64


def test_snapshot_rejects_cross_provider_and_future_ticker():
    instruments = [_instrument("SUIUSDT", "SUI")]
    ticker = _ticker("SUIUSDT", timestamp=T0 - timedelta(seconds=1), last="0.8", quote_volume="1", bid="0.79", ask="0.81", provider="binance_usdm")
    with pytest.raises(ValueError, match="cannot mix ticker providers"):
        build_universe_snapshot("bybit_linear", instruments, [ticker], CONFIG, captured_at=T0)

    future = replace(ticker, provider_id="bybit_linear", timestamp=T0 + timedelta(seconds=1))
    with pytest.raises(ValueError, match="after snapshot captured_at"):
        build_universe_snapshot("bybit_linear", instruments, [future], CONFIG, captured_at=T0)


def test_archive_roundtrip_append_and_tamper_detection(tmp_path):
    first = _snapshot(T0)
    second = _snapshot(T0 + timedelta(minutes=5), reverse=True)
    archive = append_universe_snapshot(None, first)
    archive = append_universe_snapshot(archive, second)
    path = write_universe_archive(tmp_path / "universe.jsonl", archive)
    loaded = load_universe_archive(path)
    assert len(loaded.snapshots) == 2
    assert loaded.archive_sha256 == archive.archive_sha256

    rows = path.read_text(encoding="utf-8").splitlines()
    manifest = json.loads(rows[0])
    manifest["archive_sha256"] = "0" * 64
    rows[0] = json.dumps(manifest, sort_keys=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="archive digest mismatch"):
        load_universe_archive(path)


def test_archive_rejects_config_and_provider_mixing():
    first = _snapshot(T0)
    changed_config = replace(first, config=UniverseConfig(max_price=Decimal("2")))
    with pytest.raises(ValueError):
        build_universe_archive((first, changed_config))

    other_provider = replace(first, provider_id="binance_usdm")
    with pytest.raises(ValueError):
        build_universe_archive((first, other_provider))


def test_cohort_builds_real_timestamped_replay_contexts():
    first = _snapshot(T0)
    second = _snapshot(T0 + timedelta(minutes=5), reverse=True)
    archive = build_universe_archive((first, second))
    cohort = build_study_cohort(archive, max_context_age_seconds=300.0)
    assert cohort.symbols == ("DOGEUSDT", "SUIUSDT")
    doge = cohort.contexts["DOGEUSDT"]
    sui = cohort.contexts["SUIUSDT"]
    assert [point.liquidity_rank for point in doge.liquidity_points] == [1, 2]
    assert [point.liquidity_rank for point in sui.liquidity_points] == [2, 1]
    assert all(point.universe_size == 2 for point in sui.liquidity_points)
    assert sui.point_at(T0 + timedelta(minutes=5)) is not None
    assert sui.point_at(T0 + timedelta(minutes=10, seconds=1)) is None
    assert cohort.cohort_sha256


def test_cohort_symbol_selection_window_and_roundtrip(tmp_path):
    first = _snapshot(T0)
    second = _snapshot(T0 + timedelta(minutes=5), reverse=True)
    archive = build_universe_archive((first, second))
    cohort = build_study_cohort(
        archive,
        start=T0 + timedelta(minutes=5),
        end=T0 + timedelta(minutes=5),
        symbols=("SUIUSDT",),
        max_context_age_seconds=600.0,
    )
    assert cohort.symbols == ("SUIUSDT",)
    assert len(cohort.snapshot_digests) == 1
    root = write_study_cohort(tmp_path / "cohort", cohort)
    loaded = load_study_cohort(root)
    assert loaded.cohort_sha256 == cohort.cohort_sha256
    assert loaded.contexts["SUIUSDT"].liquidity_points[0].liquidity_rank == 1


def test_cohort_rejects_uncaptured_symbol_and_analysis_metadata_change():
    first = _snapshot(T0)
    second = _snapshot(T0 + timedelta(minutes=5), reverse=True)
    archive = build_universe_archive((first, second))
    with pytest.raises(ValueError, match="absent from captured universe"):
        build_study_cohort(archive, symbols=("BTCUSDT",))

    changed_member = replace(second.members[0], instrument=replace(second.members[0].instrument, price_tick=Decimal("0.001")))
    changed_second = replace(second, members=(changed_member, *second.members[1:]))
    # A snapshot whose analysis metadata was altered must fail integrity before cohort creation.
    with pytest.raises(ValueError):
        build_universe_archive((first, changed_second))
