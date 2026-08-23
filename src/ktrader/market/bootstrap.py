from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping

from ktrader.market.validation import (
    CandleValidationError,
    FreshnessPolicy,
    FreshnessResult,
    assess_freshness,
    validate_candle,
    validate_sequence,
)
from ktrader.models import NormalizedCandle, NormalizedInstrument
from ktrader.providers.base import MarketDataProvider
from ktrader.storage.sqlite import CandleRepository

DEFAULT_HISTORY_COUNTS: dict[str, int] = {
    "1d": 250,
    "4h": 250,
    "1h": 250,
    "15m": 250,
    "5m": 300,
}


class BootstrapError(RuntimeError):
    """Historical MTF bootstrap failed closed."""


@dataclass(frozen=True, slots=True)
class HistoryPlan:
    interval_counts: Mapping[str, int] = field(
        default_factory=lambda: dict(DEFAULT_HISTORY_COUNTS)
    )

    def __post_init__(self) -> None:
        if not self.interval_counts:
            raise ValueError("History plan cannot be empty")
        for interval, count in self.interval_counts.items():
            if count <= 0:
                raise ValueError(f"History count for {interval} must be positive")


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    provider_id: str
    symbol: str
    interval_counts: Mapping[str, int]
    freshness: Mapping[str, FreshnessResult]
    stored_total: int
    started_at: datetime
    completed_at: datetime


class MTFBootstrapService:
    def __init__(
        self,
        repository: CandleRepository,
        *,
        freshness_policy: FreshnessPolicy | None = None,
    ) -> None:
        self.repository = repository
        self.freshness_policy = freshness_policy or FreshnessPolicy()

    async def bootstrap(
        self,
        provider: MarketDataProvider,
        instrument: NormalizedInstrument,
        *,
        plan: HistoryPlan | None = None,
        now: datetime | None = None,
    ) -> BootstrapResult:
        history_plan = plan or HistoryPlan()
        started_at = datetime.now(timezone.utc)
        current = now or started_at
        staged: dict[str, list[NormalizedCandle]] = {}
        freshness: dict[str, FreshnessResult] = {}

        try:
            if instrument.provider_id != provider.provider_id:
                raise BootstrapError("Instrument/provider mismatch")
            if not instrument.is_tradable_perpetual:
                raise BootstrapError("Instrument is not a tradable perpetual contract")

            for interval, target_count in history_plan.interval_counts.items():
                provider.validate_interval(interval)
                page_size = provider.capabilities.max_kline_page_size
                request_limit = target_count + 1
                if page_size is not None:
                    request_limit = min(request_limit, page_size)
                if request_limit < target_count:
                    raise BootstrapError(
                        f"Provider page size cannot satisfy {target_count} bars for {interval}"
                    )

                raw = await provider.get_candles(
                    instrument,
                    interval,
                    limit=request_limit,
                )
                for candle in raw:
                    validate_candle(
                        candle,
                        provider_id=provider.provider_id,
                        symbol=instrument.symbol,
                        interval=interval,
                    )

                closed = [candle for candle in raw if candle.closed]
                if len(closed) < target_count:
                    raise BootstrapError(
                        f"Insufficient closed {interval} bars: "
                        f"required={target_count}, received={len(closed)}"
                    )
                selected = closed[-target_count:]
                validate_sequence(
                    selected,
                    provider_id=provider.provider_id,
                    symbol=instrument.symbol,
                    interval=interval,
                    require_closed=True,
                    require_contiguous=True,
                )
                freshness_result = assess_freshness(
                    selected[-1],
                    policy=self.freshness_policy,
                    now=current,
                )
                if freshness_result.stale:
                    raise BootstrapError(
                        f"Stale {interval} data: age={freshness_result.age_seconds:.3f}s "
                        f"> max={freshness_result.max_age_seconds:.3f}s"
                    )
                staged[interval] = selected
                freshness[interval] = freshness_result

            flattened = [
                candle
                for interval in history_plan.interval_counts
                for candle in staged[interval]
            ]
            stored_total = self.repository.upsert_many(flattened)
            completed_at = datetime.now(timezone.utc)
            counts = {interval: len(candles) for interval, candles in staged.items()}
            self.repository.record_bootstrap_run(
                provider_id=provider.provider_id,
                symbol=instrument.symbol,
                started_at=started_at,
                completed_at=completed_at,
                status="SUCCESS",
                interval_counts=counts,
            )
            return BootstrapResult(
                provider_id=provider.provider_id,
                symbol=instrument.symbol,
                interval_counts=counts,
                freshness=freshness,
                stored_total=stored_total,
                started_at=started_at,
                completed_at=completed_at,
            )
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            try:
                self.repository.record_bootstrap_run(
                    provider_id=provider.provider_id,
                    symbol=instrument.symbol,
                    started_at=started_at,
                    completed_at=completed_at,
                    status="FAILED",
                    interval_counts={interval: len(value) for interval, value in staged.items()},
                    error=f"{type(exc).__name__}: {exc}",
                )
            except Exception:
                pass
            if isinstance(exc, BootstrapError):
                raise
            if isinstance(exc, CandleValidationError):
                raise BootstrapError(str(exc)) from exc
            raise BootstrapError(str(exc)) from exc
