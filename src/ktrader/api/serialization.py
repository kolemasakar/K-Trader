from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from ktrader.api.state import CandleSeriesSnapshot, ScannerRuntimeStatus
from ktrader.engine.models import TradingDecision
from ktrader.market.universe import UniverseCandidate
from ktrader.models import NormalizedCandle


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _time(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def serialize_ticker_age(timestamp: datetime, *, now: datetime) -> float:
    return max(0.0, (now.astimezone(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds())


def serialize_universe_candidate(item: UniverseCandidate, *, now: datetime) -> dict[str, Any]:
    instrument = item.instrument
    ticker = item.ticker
    return {
        "provider_id": instrument.provider_id,
        "canonical_symbol": instrument.symbol,
        "provider_symbol": instrument.provider_symbol or instrument.symbol,
        "market_type": instrument.market_type,
        "contract_type": instrument.contract_type,
        "status": instrument.status,
        "base_asset": instrument.base_asset,
        "quote_asset": instrument.quote_asset,
        "price_tick": _decimal(instrument.price_tick),
        "quantity_step": _decimal(instrument.quantity_step),
        "last_price": _decimal(ticker.last_price),
        "quote_volume_24h": _decimal(ticker.quote_volume_24h),
        "base_volume_24h": _decimal(ticker.base_volume_24h),
        "trade_count_24h": ticker.trade_count_24h,
        "bid_price": _decimal(ticker.bid_price),
        "ask_price": _decimal(ticker.ask_price),
        "spread_bps": _decimal(ticker.spread_bps),
        "open_interest": _decimal(ticker.open_interest),
        "liquidity_score": _decimal(item.liquidity_score),
        "data_time": _time(ticker.timestamp),
        "data_age_seconds": serialize_ticker_age(ticker.timestamp, now=now),
    }


def serialize_candle(candle: NormalizedCandle) -> dict[str, Any]:
    return {
        "provider_id": candle.provider_id,
        "canonical_symbol": candle.symbol,
        "interval": candle.interval,
        "open_time": _time(candle.open_time),
        "close_time": _time(candle.close_time),
        "open": _decimal(candle.open),
        "high": _decimal(candle.high),
        "low": _decimal(candle.low),
        "close": _decimal(candle.close),
        "volume": _decimal(candle.volume),
        "quote_volume": _decimal(candle.quote_volume),
        "trade_count": candle.trade_count,
        "taker_buy_volume": _decimal(candle.taker_buy_volume),
        "taker_buy_quote_volume": _decimal(candle.taker_buy_quote_volume),
        "closed": candle.closed,
    }


def serialize_candle_series(series: CandleSeriesSnapshot, *, limit: int) -> dict[str, Any]:
    selected = series.candles[-limit:]
    return {
        "provider_id": series.provider_id,
        "canonical_symbol": series.symbol,
        "interval": series.interval,
        "source_kind": series.source_kind,
        "count": len(selected),
        "candles": [serialize_candle(candle) for candle in selected],
    }


def serialize_decision(decision: TradingDecision) -> dict[str, Any]:
    return {
        "provider_id": decision.provider_id,
        "exchange": decision.exchange,
        "canonical_symbol": decision.canonical_symbol,
        "provider_symbol": decision.provider_symbol,
        "market_type": decision.market_type,
        "side": decision.side,
        "grade": decision.grade,
        "setup_score": decision.setup_score,
        "raw_score": decision.raw_score,
        "setup_type": decision.setup_type,
        "market_regime": decision.market_regime,
        "trend_context": decision.trend_context,
        "liquidity_rank": decision.liquidity_rank,
        "liquidity_score": _decimal(decision.liquidity_score),
        "sessions": list(decision.sessions),
        "session_overlap": decision.session_overlap,
        "strength": decision.strength,
        "primary_level_id": decision.primary_level_id,
        "primary_level_strength": decision.primary_level_strength,
        "trap_state": decision.trap_state,
        "vsa_events": list(decision.vsa_events),
        "entry": _decimal(decision.entry),
        "luft": _decimal(decision.luft),
        "stop": _decimal(decision.stop),
        "target": _decimal(decision.target),
        "rr": _decimal(decision.rr),
        "atr5d": _decimal(decision.atr5d),
        "atr_used_pct": _decimal(decision.atr_used_pct),
        "atr_state": decision.atr_state,
        "position_size": _decimal(decision.position_size),
        "risk_amount": _decimal(decision.risk_amount),
        "risk_percent": _decimal(decision.risk_percent),
        "reason_codes": list(decision.reason_codes),
        "data_time": _time(decision.data_time),
        "last_closed_bar": _time(decision.last_closed_bar),
        "data_age_seconds": decision.data_age_seconds,
        "freshness_status": decision.freshness_status,
        "generated_at": _time(decision.generated_at),
        "engine_version": decision.engine_version,
        "estimated_probability": decision.estimated_probability,
    }


def serialize_status(status: ScannerRuntimeStatus, *, started_at: datetime) -> dict[str, Any]:
    return {
        "status": status.status,
        "provider_id": status.provider_id,
        "universe_size": status.universe_size,
        "data_ready": status.data_ready,
        "last_scan_at": _time(status.last_scan_at),
        "last_error": status.last_error,
        "cycle_id": status.cycle_id,
        "symbols_ready": status.symbols_ready,
        "symbols_failed": status.symbols_failed,
        "live_streaming": status.live_streaming,
        "last_cycle_duration_seconds": status.last_cycle_duration_seconds,
        "started_at": _time(started_at),
    }
