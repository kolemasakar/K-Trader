from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

from ktrader.engine.models import TradingDecision
from ktrader.history import build_history_dataset, build_mtf_bundle
from ktrader.market.bootstrap import HistoryPlan
from ktrader.market.timeframes import CANONICAL_INTERVALS, interval_seconds
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.outcomes import OutcomeRepository, decision_fingerprint
from ktrader.replay import (
    ReplayLiquidityPoint,
    ReplayStudyConfig,
    ReplayStudyContext,
    load_replay_context,
    run_replay_study,
    stable_signal_key,
    write_replay_context,
    write_replay_study,
)
from ktrader.runtime.models import RuntimeScannerConfig


UTC = timezone.utc
AS_OF = datetime(2026, 8, 10, tzinfo=UTC)


def _interval_dataset(interval: str, count: int = 4):
    seconds = interval_seconds(interval)
    step = timedelta(seconds=seconds)
    start = AS_OF - step * count
    candles = []
    for index in range(count):
        open_time = start + step * index
        if interval == "5m":
            lows = [Decimal("99"), Decimal("99.2"), Decimal("99.5"), Decimal("100.5")]
            highs = [Decimal("101"), Decimal("100.5"), Decimal("100.7"), Decimal("102.5")]
            closes = [Decimal("100"), Decimal("100"), Decimal("100.2"), Decimal("102")]
            low = lows[index]
            high = highs[index]
            close = closes[index]
        else:
            low = Decimal("99")
            high = Decimal("101")
            close = Decimal("100")
        candles.append(
            NormalizedCandle(
                provider_id="bybit_linear",
                symbol="SUIUSDT",
                interval=interval,
                open_time=open_time,
                close_time=open_time + step - timedelta(milliseconds=1),
                open=Decimal("100"),
                high=high,
                low=low,
                close=close,
                volume=Decimal("1000"),
                quote_volume=Decimal("100000"),
                closed=True,
            )
        )
    return build_history_dataset(
        candles,
        provider_symbol="SUIUSDT",
        requested_bars=count,
        fetched_at=AS_OF,
    )


def _bundle():
    datasets = {interval: _interval_dataset(interval) for interval in CANONICAL_INTERVALS}
    return build_mtf_bundle(datasets, as_of=AS_OF)


def _instrument():
    return NormalizedInstrument(
        provider_id="bybit_linear",
        symbol="SUIUSDT",
        base_asset="SUI",
        quote_asset="USDT",
        market_type="linear_perpetual",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.001"),
        quantity_step=Decimal("0.1"),
        provider_symbol="SUIUSDT",
    )


def _context(*, max_age: float = 300.0):
    points = tuple(
        ReplayLiquidityPoint(
            timestamp=candle.close_time,
            liquidity_score=Decimal("1000000"),
            liquidity_rank=2,
            universe_size=20,
        )
        for candle in _bundle().datasets["5m"].candles
    )
    return ReplayStudyContext(_instrument(), points, max_context_age_seconds=max_age)


def _decision(now: datetime, last_closed_bar: datetime) -> TradingDecision:
    return TradingDecision(
        provider_id="bybit_linear",
        exchange="bybit_linear",
        canonical_symbol="SUIUSDT",
        provider_symbol="SUIUSDT",
        market_type="linear_perpetual",
        side="LONG",
        grade="A",
        setup_score=85,
        raw_score=85,
        setup_type="TRAP_LEVEL_CONFIRMATION",
        market_regime="BULLISH",
        trend_context="BULLISH",
        liquidity_rank=2,
        liquidity_score=Decimal("1000000"),
        sessions=("London",),
        session_overlap=False,
        strength="STRONG",
        primary_level_id="level-1",
        primary_level_strength="STRONG",
        trap_state="CONFIRMED",
        vsa_events=(),
        entry=Decimal("100"),
        luft=Decimal("0.01"),
        stop=Decimal("98"),
        target=Decimal("102"),
        rr=Decimal("1"),
        atr5d=Decimal("4"),
        atr_used_pct=Decimal("20"),
        atr_state="STRONG",
        position_size=None,
        risk_amount=None,
        risk_percent=None,
        reason_codes=(),
        data_time=now,
        last_closed_bar=last_closed_bar,
        data_age_seconds=0.0,
        freshness_status="FRESH",
        generated_at=now,
        engine_version="test-engine",
    )


def _fake_analysis(**kwargs):
    now = kwargs["now"]
    last_closed = kwargs["candles_by_interval"]["5m"][-1].close_time
    return (_decision(now, last_closed),)


def _scanner_config():
    return RuntimeScannerConfig(
        history=HistoryPlan({interval: 1 for interval in CANONICAL_INTERVALS}),
    )


def test_replay_context_roundtrip(tmp_path):
    path = write_replay_context(tmp_path / "context.json", _context())
    loaded = load_replay_context(path)
    assert loaded.instrument.instrument_id == "bybit_linear:SUIUSDT"
    assert loaded.liquidity_points[0].liquidity_rank == 2
    assert loaded.max_context_age_seconds == 300.0


def test_replay_study_deduplicates_same_geometry_and_persists_one_outcome():
    repository = OutcomeRepository(":memory:")
    try:
        result = run_replay_study(
            _bundle(),
            _context(),
            scanner_config=_scanner_config(),
            study_config=ReplayStudyConfig(step_bars=1, horizon_bars=3),
            outcome_repository=repository,
            analysis_function=_fake_analysis,
        )
        assert result.analyzed_cutoffs == 4
        assert result.unique_tradable_signals == 1
        assert result.outcome_counts == {"WIN": 1}
        assert result.binary_resolved_count == 1
        assert repository.counts() == {"WIN": 1}
        assert sum(record.outcome is not None for record in result.decision_records) == 1
        assert result.estimated_probability is None
    finally:
        repository.close()


def test_missing_or_stale_liquidity_context_fails_closed_per_cutoff():
    first = _bundle().datasets["5m"].candles[0].close_time
    context = ReplayStudyContext(
        _instrument(),
        (ReplayLiquidityPoint(first, Decimal("1"), 1, 10),),
        max_context_age_seconds=1.0,
    )
    result = run_replay_study(
        _bundle(),
        context,
        scanner_config=_scanner_config(),
        analysis_function=_fake_analysis,
    )
    assert result.analyzed_cutoffs == 1
    assert result.skipped_missing_context == 3


def test_signal_key_deduplicates_same_setup_but_decision_id_keeps_time_audit():
    first = _decision(AS_OF - timedelta(minutes=5), AS_OF - timedelta(minutes=5, milliseconds=1))
    second = replace(
        first,
        generated_at=AS_OF,
        data_time=AS_OF,
        last_closed_bar=AS_OF - timedelta(milliseconds=1),
    )
    assert stable_signal_key(first) == stable_signal_key(second)
    assert decision_fingerprint(first) != decision_fingerprint(second)


def test_study_artifact_contains_decisions_and_never_probability(tmp_path):
    result = run_replay_study(
        _bundle(),
        _context(),
        scanner_config=_scanner_config(),
        study_config=ReplayStudyConfig(horizon_bars=3),
        analysis_function=_fake_analysis,
    )
    path = write_replay_study(tmp_path / "study.jsonl", result)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["record_type"] == "manifest"
    assert rows[0]["estimated_probability"] is None
    assert rows[1]["record_type"] == "decision"
    assert rows[1]["decision"]["estimated_probability"] is None


def test_context_identity_mismatch_is_rejected():
    wrong = replace(_instrument(), provider_id="binance_usdm")
    point = ReplayLiquidityPoint(_bundle().datasets["5m"].candles[0].close_time, Decimal("1"), 1, 1)
    context = ReplayStudyContext(wrong, (point,))
    try:
        run_replay_study(_bundle(), context, scanner_config=_scanner_config(), analysis_function=_fake_analysis)
    except ValueError as exc:
        assert "does not match bundle" in str(exc)
    else:
        raise AssertionError("identity mismatch must fail closed")
