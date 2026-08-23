from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Mapping

from ktrader.evidence.trap import TrapEvent
from ktrader.evidence.vsa import VSAEvent
from ktrader.structure.levels import PriceLevel


@dataclass(frozen=True, slots=True)
class DailyRangeContext:
    provider_id: str
    symbol: str
    open_time: datetime
    last_closed_bar: datetime
    observed_high: Decimal
    observed_low: Decimal


@dataclass(frozen=True, slots=True)
class RiskContext:
    balance: Decimal
    risk_per_trade_pct: Decimal
    quantity_value_per_price_unit: Decimal
    quantity_step: Decimal


@dataclass(frozen=True, slots=True)
class SetupCandidate:
    direction: str
    setup_type: str
    primary_level: PriceLevel
    trap: TrapEvent | None = None
    vsa: VSAEvent | None = None


@dataclass(frozen=True, slots=True)
class SetupGeometry:
    confirmation_time: datetime
    entry: Decimal
    luft: Decimal
    stop: Decimal
    target: Decimal
    target_level_id: str
    rr: Decimal
    atr_used_pct: Decimal
    atr_state: str


@dataclass(frozen=True, slots=True)
class PositionRisk:
    position_size: Decimal | None
    risk_amount: Decimal | None
    risk_percent: Decimal | None


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    components: Mapping[str, int]
    raw_score: int
    setup_score: int
    grade: str
    hard_rejects: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TradingDecision:
    provider_id: str
    exchange: str
    canonical_symbol: str
    provider_symbol: str
    market_type: str
    side: str
    grade: str
    setup_score: int
    raw_score: int
    setup_type: str
    market_regime: str
    trend_context: str
    liquidity_rank: int
    liquidity_score: Decimal
    sessions: tuple[str, ...]
    session_overlap: bool
    strength: str
    primary_level_id: str | None
    primary_level_strength: str | None
    trap_state: str | None
    vsa_events: tuple[str, ...]
    entry: Decimal | None
    luft: Decimal | None
    stop: Decimal | None
    target: Decimal | None
    rr: Decimal | None
    atr5d: Decimal | None
    atr_used_pct: Decimal | None
    atr_state: str | None
    position_size: Decimal | None
    risk_amount: Decimal | None
    risk_percent: Decimal | None
    reason_codes: tuple[str, ...]
    data_time: datetime
    last_closed_bar: datetime
    data_age_seconds: float
    freshness_status: str
    generated_at: datetime
    engine_version: str = "phase7-v1"
    estimated_probability: None = None
