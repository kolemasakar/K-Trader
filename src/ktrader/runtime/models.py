from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ktrader.market.bootstrap import HistoryPlan
from ktrader.market.universe import UniverseConfig
from ktrader.market.validation import FreshnessPolicy
from ktrader.market.live import LiveConfig


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
        if self.setup_interval != "5m":
            raise ValueError("phase8.5 canonical setup_interval is 5m")
        if self.setup_max_age_bars <= 0:
            raise ValueError("setup_max_age_bars must be positive")


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
