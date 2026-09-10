from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from collections.abc import Mapping, Sequence

from ktrader.api.state import CandleSeriesSnapshot
from ktrader.engine.geometry import build_daily_range_context
from ktrader.engine.models import TradingDecision
from ktrader.engine.service import discover_setup_candidates, evaluate_candidate
from ktrader.evidence.trap import detect_traps
from ktrader.evidence.vsa import detect_vsa_events, validate_vsa_context
from ktrader.indicators.atr import atr, atr5d
from ktrader.market.bootstrap import BootstrapError, MTFBootstrapService
from ktrader.market.universe import UniverseCandidate
from ktrader.market.validation import assess_freshness, validate_sequence
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.providers.base import MarketDataProvider
from ktrader.storage.sqlite import CandleRepository
from ktrader.structure.snapshot import build_market_structure_snapshot
from ktrader.runtime.models import RuntimeScannerConfig


@dataclass(frozen=True, slots=True)
class SymbolAnalysisResult:
    decision_set: tuple[TradingDecision, ...]
    candle_series: tuple[CandleSeriesSnapshot, ...]


def analyze_candle_snapshot(
    *,
    config: RuntimeScannerConfig,
    instrument: NormalizedInstrument,
    universe_candidate: UniverseCandidate,
    liquidity_rank: int,
    universe_size: int,
    candles_by_interval: Mapping[str, Sequence[NormalizedCandle]],
    now: datetime,
) -> tuple[TradingDecision, ...]:
    """Run the canonical analysis engine on an already-confirmed MTF snapshot.

    The live scanner and historical replay both call this function. Historical
    replay therefore cannot silently substitute a second implementation of the
    ATR/structure/Trap/VSA/geometry/scoring path.
    """
    if liquidity_rank <= 0 or universe_size <= 0 or liquidity_rank > universe_size:
        raise ValueError("invalid liquidity rank/universe size")
    if universe_candidate.instrument.instrument_id != instrument.instrument_id:
        raise ValueError("universe candidate identity mismatch")
    if universe_candidate.ticker.provider_id != instrument.provider_id or universe_candidate.ticker.symbol != instrument.symbol:
        raise ValueError("ticker/instrument identity mismatch")
    if universe_candidate.ticker.timestamp > now:
        raise ValueError("universe ticker timestamp cannot be in the future")

    normalized: dict[str, tuple[NormalizedCandle, ...]] = {}
    freshness_by_interval = {}
    for interval, count in config.history.interval_counts.items():
        source = tuple(candles_by_interval.get(interval, ()))
        if len(source) < count:
            raise BootstrapError(f"insufficient snapshot {interval} history")
        candles = source[-count:]
        validate_sequence(
            candles,
            provider_id=instrument.provider_id,
            symbol=instrument.symbol,
            interval=interval,
            require_closed=True,
            require_contiguous=True,
        )
        fresh = assess_freshness(candles[-1], policy=config.freshness, now=now)
        if fresh.stale:
            raise BootstrapError(f"stale runtime {interval} series")
        normalized[interval] = candles
        freshness_by_interval[interval] = fresh

    setup_candles = normalized[config.setup_interval]
    atr14 = atr(setup_candles, period=14)
    atr5d_value = atr5d(normalized["1d"]).atr5d
    structure = build_market_structure_snapshot(
        normalized,
        timestamp=now,
        pivot_left=config.pivot_left,
        pivot_right=config.pivot_right,
        ma_method=config.ma_method,
        volume_window=config.volume_window,
        min_relative_volume=config.min_relative_volume,
        zone_atr_fraction=config.zone_atr_fraction,
    )
    traps = detect_traps(
        setup_candles,
        structure.levels.active(),
        atr14=atr14,
        min_break_atr_fraction=config.trap_min_break_atr_fraction,
        max_return_bars=config.trap_max_return_bars,
        max_confirmation_bars=config.trap_max_confirmation_bars,
    )
    raw_vsa = detect_vsa_events(
        setup_candles,
        baseline_window=config.vsa_baseline_window,
        narrow_spread_max=config.vsa_narrow_spread_max,
        wide_spread_min=config.vsa_wide_spread_min,
        low_volume_max=config.vsa_low_volume_max,
        high_volume_min=config.vsa_high_volume_min,
        stopping_volume_min=config.vsa_stopping_volume_min,
    )
    vsa = validate_vsa_context(
        raw_vsa,
        setup_candles,
        levels=structure.levels,
        mtf_regime=structure.regime,
        traps=traps,
        atr14=atr14,
        max_level_distance_atr_fraction=config.vsa_max_level_distance_atr_fraction,
        confirmation_bars=config.vsa_confirmation_bars,
    )
    candidates = discover_setup_candidates(structure.levels, traps=traps, vsa_events=vsa)

    day_start = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    day_bars = [
        candle
        for candle in normalized["5m"]
        if candle.open_time >= day_start and candle.open_time.date() == day_start.date()
    ]
    day_range = build_daily_range_context(day_bars)
    setup_freshness = freshness_by_interval[config.setup_interval]
    decisions = tuple(
        evaluate_candidate(
            candidate,
            instrument=instrument,
            universe_candidate=universe_candidate,
            liquidity_rank=liquidity_rank,
            universe_size=universe_size,
            structure=structure,
            setup_candles=setup_candles,
            day_range=day_range,
            freshness=setup_freshness,
            atr14=atr14,
            atr5d=atr5d_value,
            generated_at=now,
            luft_atr_fraction=config.luft_atr_fraction,
            setup_max_age_seconds=config.setup_max_age_seconds,
        )
        for candidate in candidates
    )
    if not decisions:
        decisions = (
            _no_setup_decision(
                universe_candidate,
                liquidity_rank=liquidity_rank,
                structure=structure,
                atr5d_value=atr5d_value,
                freshness=setup_freshness,
                now=now,
            ),
        )
    return decisions


class EngineSymbolAnalyzer:
    def __init__(self, repository: CandleRepository, *, config: RuntimeScannerConfig) -> None:
        self.repository = repository
        self.config = config
        self.bootstrap = MTFBootstrapService(repository, freshness_policy=config.freshness)

    async def analyze(
        self,
        provider: MarketDataProvider,
        universe_candidate: UniverseCandidate,
        *,
        liquidity_rank: int,
        universe_size: int,
        now: datetime,
    ) -> SymbolAnalysisResult:
        instrument = universe_candidate.instrument
        await self._ensure_ready(provider, instrument, now=now)
        candles_by_interval: dict[str, tuple[NormalizedCandle, ...]] = {}
        series: list[CandleSeriesSnapshot] = []
        for interval, count in self.config.history.interval_counts.items():
            candles = tuple(self.repository.load_recent(provider.provider_id, instrument.symbol, interval, limit=count))
            validate_sequence(candles, provider_id=provider.provider_id, symbol=instrument.symbol, interval=interval, require_closed=True, require_contiguous=True)
            fresh = assess_freshness(candles[-1], policy=self.config.freshness, now=now)
            if fresh.stale:
                raise BootstrapError(f"stale runtime {interval} series")
            candles_by_interval[interval] = candles
            first_source = self.repository.source_info(provider.provider_id, instrument.symbol, interval, candles[0].open_time)
            last_source = self.repository.source_info(provider.provider_id, instrument.symbol, interval, candles[-1].open_time)
            first_kind = first_source[0] if first_source else "provider"
            last_kind = last_source[0] if last_source else "provider"
            source_kind = first_kind if first_kind == last_kind else "mixed"
            series.append(CandleSeriesSnapshot(provider.provider_id, instrument.symbol, interval, source_kind, candles))

        decisions = analyze_candle_snapshot(
            config=self.config,
            instrument=instrument,
            universe_candidate=universe_candidate,
            liquidity_rank=liquidity_rank,
            universe_size=universe_size,
            candles_by_interval=candles_by_interval,
            now=now,
        )
        return SymbolAnalysisResult(decisions, tuple(series))

    async def _ensure_ready(self, provider, instrument, *, now: datetime) -> None:
        needs_bootstrap = False
        for interval, count in self.config.history.interval_counts.items():
            if self.repository.count(provider.provider_id, instrument.symbol, interval) < count:
                needs_bootstrap = True
                break
            latest = self.repository.latest(provider.provider_id, instrument.symbol, interval)
            if latest is None or assess_freshness(latest, policy=self.config.freshness, now=now).stale:
                needs_bootstrap = True
                break
        if needs_bootstrap:
            latest_run = self.repository.latest_bootstrap_run(
                provider.provider_id, instrument.symbol
            )
            if latest_run is not None:
                error = str(latest_run.get("error") or "")
                completed_at = latest_run.get("completed_at")
                if (
                    latest_run.get("status") == "FAILED"
                    and "Insufficient closed 1d bars" in error
                    and isinstance(completed_at, datetime)
                ):
                    completed_utc = completed_at.astimezone(timezone.utc)
                    retry_date = completed_utc.date() + timedelta(days=1)
                    retry_after = datetime.combine(
                        retry_date, time.min, tzinfo=timezone.utc
                    )
                    if now < retry_after:
                        raise BootstrapError(
                            "insufficient closed 1d history retry deferred until "
                            f"{retry_after.isoformat()}"
                        )
            await self.bootstrap.bootstrap(
                provider, instrument, plan=self.config.history, now=now
            )

    @staticmethod
    def _no_setup_decision(item: UniverseCandidate, *, liquidity_rank: int, structure, atr5d_value: Decimal, freshness, now: datetime) -> TradingDecision:
        return _no_setup_decision(
            item,
            liquidity_rank=liquidity_rank,
            structure=structure,
            atr5d_value=atr5d_value,
            freshness=freshness,
            now=now,
        )


def _no_setup_decision(item: UniverseCandidate, *, liquidity_rank: int, structure, atr5d_value: Decimal, freshness, now: datetime) -> TradingDecision:
    instrument = item.instrument
    return TradingDecision(
        provider_id=instrument.provider_id,
        exchange=instrument.provider_id,
        canonical_symbol=instrument.symbol,
        provider_symbol=instrument.provider_symbol or instrument.symbol,
        market_type=instrument.market_type,
        side="NO_TRADE",
        grade="C",
        setup_score=0,
        raw_score=0,
        setup_type="NO_SETUP",
        market_regime=structure.regime.regime,
        trend_context=structure.regime.regime,
        liquidity_rank=liquidity_rank,
        liquidity_score=item.liquidity_score,
        sessions=structure.session.active_sessions,
        session_overlap=structure.session.overlap,
        strength="N/A",
        primary_level_id=None,
        primary_level_strength=None,
        trap_state=None,
        vsa_events=(),
        entry=None,
        luft=None,
        stop=None,
        target=None,
        rr=None,
        atr5d=atr5d_value,
        atr_used_pct=None,
        atr_state=None,
        position_size=None,
        risk_amount=None,
        risk_percent=None,
        reason_codes=("NO_CONFIRMED_SETUP",),
        data_time=item.ticker.timestamp,
        last_closed_bar=freshness.latest_close_time,
        data_age_seconds=freshness.age_seconds,
        freshness_status="FRESH",
        generated_at=now,
        engine_version="phase8.5-v1",
    )
