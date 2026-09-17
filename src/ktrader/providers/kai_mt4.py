from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Mapping

from ktrader.providers.base import ProviderError


class KAIMT4MarketContextAdapter:
    """Transport-neutral consumer for canonical K_AI MT4 market-context bundles."""

    provider_id = "kai_mt4"
    canonical_bar_depths = {"D1": 60, "H1": 200, "M15": 300, "M5": 300}
    opaque_timestamp_semantics = "BROKER_SERVER_WALL_CLOCK_OPAQUE"

    def __init__(
        self,
        *,
        expected_bar_depths: Mapping[str, int] | None = None,
    ) -> None:
        self.expected_bar_depths = dict(
            expected_bar_depths or self.canonical_bar_depths
        )

    def accept_market_context(
        self,
        payload: Any,
        *,
        symbol: str | None = None,
        market: str | None = None,
        require_m15: bool = False,
    ) -> dict[str, Any]:
        """Validate an already-delivered canonical payload and return it unchanged.

        Cross-system delivery is deliberately outside this class until K_AI exposes
        a verified remote/read-only transport. The authoritative K_AI implementation
        currently acquires MT4 context through its local file bridge.
        """
        self.validate_market_context(
            payload,
            expected_symbol=symbol,
            expected_market=market,
            expected_bar_depths=self.expected_bar_depths,
            require_m15=require_m15,
        )
        return payload

    @classmethod
    def validate_market_context(
        cls,
        payload: Any,
        *,
        expected_symbol: str | None = None,
        expected_market: str | None = None,
        expected_bar_depths: Mapping[str, int] | None = None,
        require_m15: bool = False,
    ) -> None:
        if not isinstance(payload, dict):
            raise ProviderError("K_AI market context must be a JSON object")

        schema = str(payload.get("schema_version") or "")
        expected_scopes = {
            "1.0": {"D1", "H1", "M5"},
            "1.1": {"D1", "H1", "M15", "M5"},
        }.get(schema)
        if expected_scopes is None:
            raise ProviderError(
                f"Unsupported K_AI market-context schema: {schema or '<missing>'}"
            )
        if require_m15 and schema != "1.1":
            raise ProviderError("M15 requires K_AI MARKET_CONTEXT schema 1.1")

        required_equal = {
            "report_type": "MARKET_CONTEXT",
            "source_name": "MT4",
            "data_quality_flag": "VALID",
            "time_source": "BrokerServer",
        }
        for field, expected in required_equal.items():
            if payload.get(field) != expected:
                raise ProviderError(
                    f"Invalid K_AI market-context {field}: {payload.get(field)!r}"
                )
        if payload.get("closed_bars_only") is not True:
            raise ProviderError("K_AI market context must contain closed bars only")

        opaque_wall_clock = schema == "1.1"
        if opaque_wall_clock:
            if payload.get("timestamp_semantics") != cls.opaque_timestamp_semantics:
                raise ProviderError(
                    "K_AI schema 1.1 timestamp_semantics must be "
                    f"{cls.opaque_timestamp_semantics}"
                )
            if (
                "utc_offset_minutes" not in payload
                or payload["utc_offset_minutes"] is not None
            ):
                raise ProviderError("K_AI schema 1.1 utc_offset_minutes must be null")

        actual_symbol = str(payload.get("symbol") or "")
        actual_market = str(payload.get("market") or "").lower()
        if expected_symbol is not None and actual_symbol != expected_symbol:
            raise ProviderError(
                f"K_AI symbol mismatch: {actual_symbol!r} != {expected_symbol!r}"
            )
        if expected_market is not None and actual_market != expected_market.lower():
            raise ProviderError(
                f"K_AI market mismatch: {actual_market!r} != {expected_market.lower()!r}"
            )

        for field in ("run_id", "captured_at", "last_tick_time"):
            if not str(payload.get(field) or "").strip():
                raise ProviderError(f"K_AI market context is missing {field}")

        cls._parse_source_time(
            payload["captured_at"],
            field="captured_at",
            opaque_wall_clock=opaque_wall_clock,
        )
        cls._parse_source_time(
            payload["last_tick_time"],
            field="last_tick_time",
            opaque_wall_clock=opaque_wall_clock,
        )
        cls._validate_market_facts(payload)

        scopes = payload.get("scopes")
        if not isinstance(scopes, dict) or set(scopes) != expected_scopes:
            raise ProviderError(
                f"K_AI schema {schema} must contain exactly {sorted(expected_scopes)} scopes"
            )

        for scope in expected_scopes:
            expected_depth = None
            if expected_bar_depths is not None:
                expected_depth = expected_bar_depths.get(scope)
                if expected_depth is None:
                    raise ProviderError(f"K_AI expected bar depth is missing for {scope}")
            cls._validate_scope(
                scope,
                scopes[scope],
                expected_depth=expected_depth,
                opaque_wall_clock=opaque_wall_clock,
            )

    @staticmethod
    def _finite_number(value: Any, *, field: str) -> float:
        if isinstance(value, bool):
            raise ProviderError(f"K_AI {field} must be numeric, not boolean")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ProviderError(f"K_AI {field} must be numeric") from exc
        if not math.isfinite(number):
            raise ProviderError(f"K_AI {field} must be finite")
        return number

    @classmethod
    def _validate_market_facts(cls, payload: dict[str, Any]) -> None:
        required = (
            "bid",
            "ask",
            "spread",
            "digits",
            "point",
            "stop_level",
            "freeze_level",
            "tick_value",
            "tick_size",
            "contract_size",
            "trade_allowed",
            "terminal_connected",
            "market_open",
        )
        missing = [field for field in required if field not in payload]
        if missing:
            raise ProviderError(
                f"K_AI market context missing market facts: {', '.join(missing)}"
            )

        bid = cls._finite_number(payload["bid"], field="market fact bid")
        ask = cls._finite_number(payload["ask"], field="market fact ask")
        spread = cls._finite_number(payload["spread"], field="market fact spread")
        point = cls._finite_number(payload["point"], field="market fact point")
        stop_level = cls._finite_number(
            payload["stop_level"], field="market fact stop_level"
        )
        freeze_level = cls._finite_number(
            payload["freeze_level"], field="market fact freeze_level"
        )
        tick_value = cls._finite_number(
            payload["tick_value"], field="market fact tick_value"
        )
        tick_size = cls._finite_number(
            payload["tick_size"], field="market fact tick_size"
        )
        contract_size = cls._finite_number(
            payload["contract_size"], field="market fact contract_size"
        )

        digits_raw = payload["digits"]
        if isinstance(digits_raw, bool):
            raise ProviderError("K_AI market fact digits must be an integer")
        try:
            digits = int(digits_raw)
            digits_numeric = float(digits_raw)
        except (TypeError, ValueError) as exc:
            raise ProviderError("K_AI market fact digits must be an integer") from exc
        if (
            not math.isfinite(digits_numeric)
            or digits_numeric != digits
            or not 0 <= digits <= 12
        ):
            raise ProviderError(
                "K_AI market fact digits must be an integer in [0, 12]"
            )

        if (
            bid <= 0
            or ask < bid
            or point <= 0
            or tick_value <= 0
            or tick_size <= 0
            or contract_size <= 0
        ):
            raise ProviderError(
                "K_AI market facts violate positive-price/size invariants"
            )
        if spread < 0 or stop_level < 0 or freeze_level < 0:
            raise ProviderError(
                "K_AI market facts violate non-negative spread/level invariants"
            )

        for field in ("trade_allowed", "terminal_connected", "market_open"):
            if not isinstance(payload[field], bool):
                raise ProviderError(f"K_AI market fact {field} must be boolean")

    @staticmethod
    def _parse_source_time(
        value: Any,
        *,
        field: str,
        opaque_wall_clock: bool = False,
    ) -> datetime:
        text = str(value or "").strip()
        if not text:
            raise ProviderError(f"K_AI {field} is missing")
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ProviderError(f"K_AI {field} must be ISO-8601 compatible") from exc
        if opaque_wall_clock and parsed.tzinfo is not None:
            raise ProviderError(
                f"K_AI schema 1.1 {field} must be opaque broker-server wall-clock "
                "without UTC offset"
            )
        return parsed

    @classmethod
    def _validate_scope(
        cls,
        scope: str,
        data: Any,
        *,
        expected_depth: int | None = None,
        opaque_wall_clock: bool = False,
    ) -> None:
        if not isinstance(data, dict) or data.get("timeframe") != scope:
            raise ProviderError(f"Invalid K_AI {scope} scope")
        if not str(data.get("snapshot_id") or "").strip():
            raise ProviderError(f"K_AI {scope} scope is missing snapshot_id")

        try:
            depth = int(data.get("bar_depth") or 0)
        except (TypeError, ValueError) as exc:
            raise ProviderError(f"K_AI {scope} bar_depth must be an integer") from exc
        bars = data.get("bars")
        if depth <= 0 or not isinstance(bars, list) or len(bars) != depth:
            raise ProviderError(f"K_AI {scope} bar depth/count mismatch")
        if expected_depth is not None and depth != int(expected_depth):
            raise ProviderError(
                f"K_AI {scope} bar_depth mismatch: {depth} != {int(expected_depth)}"
            )

        times: list[datetime] = []
        time_texts: list[str] = []
        for index, bar in enumerate(bars):
            if not isinstance(bar, dict):
                raise ProviderError(f"K_AI {scope} bar {index} is invalid")
            for field in ("time", "open", "high", "low", "close", "volume"):
                if field not in bar:
                    raise ProviderError(f"K_AI {scope} bar {index} missing {field}")

            bar_time_text = str(bar["time"])
            bar_time = cls._parse_source_time(
                bar_time_text,
                field=f"{scope} bar {index} time",
                opaque_wall_clock=opaque_wall_clock,
            )
            open_ = cls._finite_number(
                bar["open"], field=f"{scope} bar {index} open"
            )
            high = cls._finite_number(
                bar["high"], field=f"{scope} bar {index} high"
            )
            low = cls._finite_number(
                bar["low"], field=f"{scope} bar {index} low"
            )
            close = cls._finite_number(
                bar["close"], field=f"{scope} bar {index} close"
            )
            volume = cls._finite_number(
                bar["volume"], field=f"{scope} bar {index} volume"
            )

            if high < low or high < max(open_, close) or low > min(open_, close):
                raise ProviderError(
                    f"K_AI {scope} bar {index} violates OHLC invariants"
                )
            if volume < 0:
                raise ProviderError(
                    f"K_AI {scope} bar {index} volume must be non-negative"
                )

            times.append(bar_time)
            time_texts.append(bar_time_text)

        try:
            ordered = times == sorted(times)
            unique = len(times) == len(set(times))
        except TypeError as exc:
            raise ProviderError(
                f"K_AI {scope} bar times mix timezone-aware and naive values"
            ) from exc
        if not ordered or not unique:
            raise ProviderError(f"K_AI {scope} bars are not strictly chronological")

        latest_text = str(data.get("latest_closed_bar_time") or "")
        if latest_text != time_texts[-1]:
            raise ProviderError(f"K_AI {scope} latest_closed_bar_time mismatch")
        latest = cls._parse_source_time(
            latest_text,
            field=f"{scope} latest_closed_bar_time",
            opaque_wall_clock=opaque_wall_clock,
        )
        current = cls._parse_source_time(
            data.get("current_bar_time"),
            field=f"{scope} current_bar_time",
            opaque_wall_clock=opaque_wall_clock,
        )
        try:
            if current <= latest:
                raise ProviderError(
                    f"K_AI {scope} current_bar_time must be after "
                    "latest_closed_bar_time"
                )
        except TypeError as exc:
            raise ProviderError(
                f"K_AI {scope} current/latest bar times mix timezone-aware and naive values"
            ) from exc
