from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ktrader.engine.models import TradingDecision
from ktrader.history import (
    build_history_dataset,
    build_mtf_bundle,
    build_universe_archive,
    build_universe_snapshot,
)
from ktrader.market.bootstrap import HistoryPlan
from ktrader.market.timeframes import CANONICAL_INTERVALS, interval_seconds
from ktrader.market.universe import UniverseConfig
from ktrader.models import NormalizedCandle, NormalizedInstrument, NormalizedTicker
from ktrader.replay.prospective import (
    UTC_DAY_5M_EMPTY_ERROR,
    load_prospective_control_report,
    load_prospective_control_shard,
    merge_prospective_control_shards,
    run_prospective_control_shard,
    select_recorded_snapshot,
    write_prospective_control_report,
    write_prospective_control_shard,
)
from ktrader.runtime.models import RuntimeScannerConfig


UTC = timezone.utc
PROVIDER = "binance_usdm"
END = datetime(2026, 1, 2, 0, 20, tzinfo=UTC)
CONFIG = UniverseConfig(max_price=Decimal("3"), max_candidates=2)


def _instrument(symbol: str, base: str) -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=PROVIDER,
        symbol=symbol,
        provider_symbol=symbol,
        base_asset=base,
        quote_asset="USDT",
        market_type="futures",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def _ticker(symbol: str, *, timestamp: datetime, volume: str) -> NormalizedTicker:
    return NormalizedTicker(
        provider_id=PROVIDER,
        symbol=symbol,
        timestamp=timestamp,
        last_price=Decimal("1"),
        quote_volume_24h=Decimal(volume),
        bid_price=Decimal("0.9999"),
        ask_price=Decimal("1.0001"),
    )


def _snapshot(captured_at: datetime, *, two_symbols: bool = False):
    instruments = [_instrument("SUIUSDT", "SUI")]
    tickers = [_ticker("SUIUSDT", timestamp=captured_at - timedelta(seconds=1), volume="2000000")]
    if two_symbols:
        instruments.append(_instrument("DOGEUSDT", "DOGE"))
        tickers.append(_ticker("DOGEUSDT", timestamp=captured_at - timedelta(seconds=1), volume="1000000"))
    return build_universe_snapshot(
        PROVIDER,
        instruments,
        tickers,
        CONFIG,
        captured_at=captured_at,
    )


def _candle(interval: str, open_time: datetime, *, symbol: str = "SUIUSDT") -> NormalizedCandle:
    seconds = interval_seconds(interval)
    return NormalizedCandle(
        provider_id=PROVIDER,
        symbol=symbol,
        interval=interval,
        open_time=open_time,
        close_time=open_time + timedelta(seconds=seconds) - timedelta(milliseconds=1),
        open=Decimal("1"),
        high=Decimal("1.01"),
        low=Decimal("0.99"),
        close=Decimal("1"),
        volume=Decimal("1000"),
        quote_volume=Decimal("1000"),
        closed=True,
    )


def _bundle(*, include_current_day_5m: bool):
    opens = {
        "1d": [datetime(2026, 1, 1, 0, 0, tzinfo=UTC)],
        "4h": [datetime(2026, 1, 1, 20, 0, tzinfo=UTC)],
        "1h": [datetime(2026, 1, 1, 23, 0, tzinfo=UTC)],
        "15m": [datetime(2026, 1, 1, 23, 45, tzinfo=UTC)],
        "5m": [datetime(2026, 1, 1, 23, 55, tzinfo=UTC)],
    }
    if include_current_day_5m:
        opens["5m"].extend(
            datetime(2026, 1, 2, 0, minute, tzinfo=UTC)
            for minute in (0, 5, 10, 15)
        )
    datasets = {
        interval: build_history_dataset(
            [_candle(interval, value) for value in opens[interval]],
            provider_symbol="SUIUSDT",
            requested_bars=len(opens[interval]),
            fetched_at=END,
        )
        for interval in CANONICAL_INTERVALS
    }
    return build_mtf_bundle(datasets, as_of=END)


def _scanner() -> RuntimeScannerConfig:
    return RuntimeScannerConfig(
        history=HistoryPlan({interval: 1 for interval in CANONICAL_INTERVALS}),
        setup_interval="5m",
        setup_max_age_bars=12,
    )


def _fake_analysis(**kwargs):
    now = kwargs["now"]
    candidate = kwargs["universe_candidate"]
    last_closed = kwargs["candles_by_interval"]["5m"][-1].close_time
    return (
        TradingDecision(
            provider_id=PROVIDER,
            exchange=PROVIDER,
            canonical_symbol=candidate.instrument.symbol,
            provider_symbol=candidate.instrument.provider_symbol or candidate.instrument.symbol,
            market_type=candidate.instrument.market_type,
            side="NO_TRADE",
            grade="C",
            setup_score=69,
            raw_score=75,
            setup_type="TRAP_LEVEL_CONFIRMATION",
            market_regime="BULLISH",
            trend_context="BULLISH",
            liquidity_rank=kwargs["liquidity_rank"],
            liquidity_score=candidate.liquidity_score,
            sessions=("London",),
            session_overlap=False,
            strength="STRONG",
            primary_level_id="level-1",
            primary_level_strength="STRONG",
            trap_state="CONFIRMED",
            vsa_events=(),
            entry=None,
            luft=None,
            stop=None,
            target=None,
            rr=Decimal("2"),
            atr5d=Decimal("0.1"),
            atr_used_pct=Decimal("20"),
            atr_state="STRONG",
            position_size=None,
            risk_amount=None,
            risk_percent=None,
            reason_codes=("RR_BELOW_3",),
            data_time=candidate.ticker.timestamp,
            last_closed_bar=last_closed,
            data_age_seconds=0.0,
            freshness_status="FRESH",
            generated_at=now,
            engine_version="test-engine",
        ),
    )


def test_midnight_empty_day_is_explicit_analysis_error_without_analyzer_call():
    cutoff = datetime(2026, 1, 2, 0, 0, tzinfo=UTC)
    archive = build_universe_archive((_snapshot(cutoff - timedelta(seconds=30)),))
    called = False

    def must_not_run(**_kwargs):
        nonlocal called
        called = True
        raise AssertionError("canonical analyzer must not run without current UTC-day 5m state")

    shard = run_prospective_control_shard(
        archive,
        {"SUIUSDT": _bundle(include_current_day_5m=False)},
        scanner_config=_scanner(),
        start=cutoff,
        end=cutoff,
        analysis_function=must_not_run,
    )

    assert called is False
    assert shard.complete is True
    assert len(shard.cutoffs) == 1
    slot = shard.cutoffs[0].slots[0]
    assert slot.status == "ANALYSIS_ERROR"
    assert slot.detail == UTC_DAY_5M_EMPTY_ERROR
    assert slot.decisions == ()

    report = merge_prospective_control_shards((shard,))
    assert report.analysis_error_slots == 1
    assert report.analysis_errors == {UTC_DAY_5M_EMPTY_ERROR: 1}
    assert report.decision_records == 0
    assert report.unique_tradable_signal_count == 0


def test_resume_produces_same_complete_shard_and_digest_as_one_pass(tmp_path):
    start = datetime(2026, 1, 2, 0, 5, tzinfo=UTC)
    cutoffs = tuple(start + timedelta(minutes=5 * index) for index in range(4))
    archive = build_universe_archive(
        tuple(_snapshot(value - timedelta(seconds=30), two_symbols=True) for value in cutoffs)
    )
    bundles = {"SUIUSDT": _bundle(include_current_day_5m=True)}

    partial = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        max_new_cutoffs=2,
        analysis_function=_fake_analysis,
    )
    assert partial.complete is False
    assert len(partial.cutoffs) == 2

    partial_path = write_prospective_control_shard(tmp_path / "partial.json", partial)
    loaded_partial = load_prospective_control_shard(partial_path)
    resumed = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        resume=loaded_partial,
        analysis_function=_fake_analysis,
    )
    direct = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        analysis_function=_fake_analysis,
    )

    assert resumed == direct
    assert resumed.complete is True
    assert resumed.shard_sha256 == direct.shard_sha256


def test_deterministic_shards_merge_to_same_report_as_monolithic_run(tmp_path):
    start = datetime(2026, 1, 2, 0, 5, tzinfo=UTC)
    cutoffs = tuple(start + timedelta(minutes=5 * index) for index in range(4))
    archive = build_universe_archive(
        tuple(_snapshot(value - timedelta(seconds=30), two_symbols=True) for value in cutoffs)
    )
    bundles = {"SUIUSDT": _bundle(include_current_day_5m=True)}

    monolithic = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        analysis_function=_fake_analysis,
    )
    report_one = merge_prospective_control_shards((monolithic,))

    shard_zero = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        shard_index=0,
        shard_count=2,
        analysis_function=_fake_analysis,
    )
    shard_one = run_prospective_control_shard(
        archive,
        bundles,
        scanner_config=_scanner(),
        start=start,
        end=cutoffs[-1],
        shard_index=1,
        shard_count=2,
        analysis_function=_fake_analysis,
    )
    report_two = merge_prospective_control_shards((shard_one, shard_zero))

    assert report_two == report_one
    assert report_two.report_sha256 == report_one.report_sha256
    assert report_two.logical_cutoffs == 4
    assert report_two.selected_context_cutoffs == 4
    assert report_two.symbol_slots == 8
    assert report_two.history_pass_slots == 4
    assert report_two.history_fail_slots == 4
    assert report_two.history_fail_by_symbol == {"DOGEUSDT": 4}
    assert report_two.decision_records == 4
    assert report_two.reason_counts == {"RR_BELOW_3": 4}
    assert report_two.funnel == {
        "htf_aligned": 4,
        "strong_confirmed_level": 4,
        "geometry_valid": 4,
        "atr_pass": 4,
        "ttl_pass": 4,
        "rr_pass": 0,
        "grade_pass": 0,
        "tradable": 0,
    }

    path = write_prospective_control_report(tmp_path / "report.json", report_two)
    assert load_prospective_control_report(path) == report_two


def test_recorded_context_selection_uses_newest_at_or_before_and_300s_boundary():
    cutoff = datetime(2026, 1, 2, 0, 10, tzinfo=UTC)
    older = _snapshot(cutoff - timedelta(minutes=10))
    exact = _snapshot(cutoff - timedelta(seconds=300))
    archive = build_universe_archive((older, exact))

    status, selected, age = select_recorded_snapshot(
        archive,
        cutoff,
        max_context_age_seconds=300.0,
    )
    assert status == "SELECTED"
    assert selected is not None and selected.content_sha256 == exact.content_sha256
    assert age == 300.0

    status, selected, age = select_recorded_snapshot(
        archive,
        cutoff + timedelta(milliseconds=1),
        max_context_age_seconds=300.0,
    )
    assert status == "STALE"
    assert selected is not None and selected.content_sha256 == exact.content_sha256
    assert age is not None and age > 300.0
