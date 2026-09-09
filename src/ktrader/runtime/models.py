from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ktrader.market.bootstrap import HistoryPlan
from ktrader.market.universe import UniverseConfig
from ktrader.market.validation import FreshnessPolicy
from ktrader.market.live import LiveConfig


SETUP_INTERVAL_SECONDS: dict[str, int] = {
    "5m": 5 * 60,
    "15m": 15 * 60,
    "1h": 60 * 60,
}


def setup_interval_seconds(interval: str) -> int:
    try:
        return SETUP_INTERVAL_SECONDS[interval]
    except KeyError as exc:
        raise ValueError(f"unsupported setup_interval: {interval}") from exc


@dataclass(frozen=True, slots=True)
class RuntimeScannerConfig:
    universe: UniverseConfig = field(default_factory=UniverseConfig)
    history: HistoryPlan = field(default_factory=HistoryPlan)
    freshness: FreshnessPolicy = field(default_factory=FreshnessPolicy)
    live: LiveConfig = field(default_factory=LiveConfig)
    analysis_limit: int = 20
    scan_interval_seconds: float = 60.0
    bootstrap_concurrency: int = 2
    setup_interval: str = "5m"
    setup_max_age_bars: int = 12
    ma_method: str = "sma"
    volume_window: int = 20
    min_relative_volume: Decimal = Decimal("1")
    pivot_left: int = 2
    pivot_right: int = 2
    zone_atr_fraction: Decimal = Decimal("0.15")
    trap_min_break_atr_fraction: Decimal = Decimal("0.05")
    trap_max_return_bars: int = 3
    trap_max_confirmation_bars: int = 2
    vsa_baseline_window: int = 20
    vsa_narrow_spread_max: Decimal = Decimal("0.8")
    vsa_wide_spread_min: Decimal = Decimal("1.5")
    vsa_low_volume_max: Decimal = Decimal("0.8")
    vsa_high_volume_min: Decimal = Decimal("1.8")
    vsa_stopping_volume_min: Decimal = Decimal("1.5")
    vsa_max_level_distance_atr_fraction: Decimal = Decimal("0.25")
    vsa_confirmation_bars: int = 2
    luft_atr_fraction: Decimal = Decimal("0.02")

    def __post_init__(self) -> None:
        if self.analysis_limit <= 0:
            raise ValueError("analysis_limit must be positive")
        if self.scan_interval_seconds <= 0:
            raise ValueError("scan_interval_seconds must be positive")
        if self.bootstrap_concurrency <= 0:
            raise ValueError("bootstrap_concurrency must be positive")
        setup_interval_seconds(self.setup_interval)
        if self.setup_interval not in self.history.interval_counts:
            raise ValueError("setup_interval must be present in history plan")
        if self.setup_max_age_bars <= 0:
            raise ValueError("setup_max_age_bars must be positive")

    @property
    def setup_max_age_seconds(self) -> int:
        return self.setup_max_age_bars * setup_interval_seconds(self.setup_interval)


@dataclass(frozen=True, slots=True)
class SymbolScanError:
    provider_id: str
    symbol: str
    error: str


@dataclass(frozen=True, slots=True)
class ScannerCycleResult:
    cycle_id: int
    provider_id: str | None
    universe_size: int
    symbols_ready: int
    symbols_failed: int
    errors: tuple[SymbolScanError, ...]
