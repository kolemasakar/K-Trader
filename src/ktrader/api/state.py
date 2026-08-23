from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from collections.abc import Iterable, Sequence

from ktrader.engine.models import TradingDecision
from ktrader.engine.service import choose_best_decision
from ktrader.market.universe import UniverseCandidate
from ktrader.models import NormalizedCandle


class SymbolNotFoundError(LookupError):
    pass


class AmbiguousSymbolError(LookupError):
    pass


@dataclass(frozen=True, slots=True)
class ScannerRuntimeStatus:
    status: str = "STARTING"
    provider_id: str | None = None
    universe_size: int = 0
    data_ready: bool = False
    last_scan_at: datetime | None = None
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class CandleSeriesSnapshot:
    provider_id: str
    symbol: str
    interval: str
    source_kind: str
    candles: tuple[NormalizedCandle, ...]


@dataclass(slots=True)
class ApiReadModel:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)
    _status: ScannerRuntimeStatus = field(default_factory=ScannerRuntimeStatus, init=False, repr=False)
    _universe: dict[tuple[str, str], UniverseCandidate] = field(default_factory=dict, init=False, repr=False)
    _candles: dict[tuple[str, str, str], CandleSeriesSnapshot] = field(default_factory=dict, init=False, repr=False)
    _analyses: dict[tuple[str, str], TradingDecision] = field(default_factory=dict, init=False, repr=False)
    _candidates: tuple[TradingDecision, ...] = field(default=(), init=False, repr=False)

    @staticmethod
    def _key(provider_id: str, symbol: str) -> tuple[str, str]:
        return provider_id, symbol.upper()

    def set_status(self, status: ScannerRuntimeStatus) -> None:
        with self._lock:
            self._status = status

    def get_status(self) -> ScannerRuntimeStatus:
        with self._lock:
            return self._status

    def replace_universe(self, candidates: Iterable[UniverseCandidate]) -> None:
        values = list(candidates)
        new_map = {
            self._key(item.instrument.provider_id, item.instrument.symbol): item
            for item in values
        }
        with self._lock:
            self._universe = new_map

    def list_universe(self, *, provider_id: str | None = None) -> tuple[UniverseCandidate, ...]:
        with self._lock:
            values = tuple(self._universe.values())
        if provider_id is not None:
            values = tuple(item for item in values if item.instrument.provider_id == provider_id)
        return tuple(sorted(values, key=lambda item: item.liquidity_score, reverse=True))

    def put_candles(
        self,
        *,
        provider_id: str,
        symbol: str,
        interval: str,
        candles: Sequence[NormalizedCandle],
        source_kind: str,
    ) -> None:
        if source_kind not in {"provider", "aggregate"}:
            raise ValueError("source_kind must be provider or aggregate")
        normalized_symbol = symbol.upper()
        values = tuple(candles)
        for candle in values:
            if (
                candle.provider_id != provider_id
                or candle.symbol.upper() != normalized_symbol
                or candle.interval != interval
            ):
                raise ValueError("candle series identity mismatch")
        snapshot = CandleSeriesSnapshot(
            provider_id=provider_id,
            symbol=normalized_symbol,
            interval=interval,
            source_kind=source_kind,
            candles=values,
        )
        with self._lock:
            self._candles[(provider_id, normalized_symbol, interval)] = snapshot

    def replace_decisions(self, decisions: Iterable[TradingDecision]) -> None:
        values = tuple(decisions)
        grouped: dict[tuple[str, str], list[TradingDecision]] = {}
        for decision in values:
            grouped.setdefault(
                self._key(decision.provider_id, decision.canonical_symbol), []
            ).append(decision)
        analyses = {
            key: best
            for key, items in grouped.items()
            if (best := choose_best_decision(items)) is not None
        }
        ordered = tuple(
            sorted(
                values,
                key=lambda item: (
                    item.side != "NO_TRADE",
                    item.setup_score,
                    item.raw_score,
                    item.generated_at,
                ),
                reverse=True,
            )
        )
        with self._lock:
            self._candidates = ordered
            self._analyses = analyses

    def list_candidates(
        self,
        *,
        provider_id: str | None = None,
        grade: str | None = None,
    ) -> tuple[TradingDecision, ...]:
        with self._lock:
            values = self._candidates
        if provider_id is not None:
            values = tuple(item for item in values if item.provider_id == provider_id)
        if grade is not None:
            values = tuple(item for item in values if item.grade == grade)
        return values

    def list_signals(self, *, provider_id: str | None = None) -> tuple[TradingDecision, ...]:
        return tuple(
            item
            for item in self.list_candidates(provider_id=provider_id)
            if item.side in {"LONG", "SHORT"} and item.grade in {"A+", "A"}
        )

    @staticmethod
    def _resolve_key(
        keys: Iterable[tuple[str, str]],
        *,
        symbol: str,
        provider_id: str | None,
    ) -> tuple[str, str]:
        normalized_symbol = symbol.upper()
        matches = [
            key
            for key in keys
            if key[1] == normalized_symbol
            and (provider_id is None or key[0] == provider_id)
        ]
        providers = sorted({key[0] for key in matches})
        if not matches:
            raise SymbolNotFoundError(normalized_symbol)
        if provider_id is None and len(providers) > 1:
            raise AmbiguousSymbolError(
                f"{normalized_symbol} exists on multiple providers: {', '.join(providers)}"
            )
        return matches[0]

    def resolve_market(self, symbol: str, *, provider_id: str | None = None) -> UniverseCandidate:
        with self._lock:
            key = self._resolve_key(self._universe.keys(), symbol=symbol, provider_id=provider_id)
            return self._universe[key]

    def resolve_analysis(self, symbol: str, *, provider_id: str | None = None) -> TradingDecision:
        with self._lock:
            key = self._resolve_key(self._analyses.keys(), symbol=symbol, provider_id=provider_id)
            return self._analyses[key]

    def resolve_candles(
        self,
        symbol: str,
        *,
        interval: str,
        provider_id: str | None = None,
    ) -> CandleSeriesSnapshot:
        normalized_symbol = symbol.upper()
        with self._lock:
            matching = [
                key
                for key in self._candles
                if key[1] == normalized_symbol
                and key[2] == interval
                and (provider_id is None or key[0] == provider_id)
            ]
            providers = sorted({key[0] for key in matching})
            if not matching:
                raise SymbolNotFoundError(f"{normalized_symbol}:{interval}")
            if provider_id is None and len(providers) > 1:
                raise AmbiguousSymbolError(
                    f"{normalized_symbol} {interval} exists on multiple providers: "
                    + ", ".join(providers)
                )
            return self._candles[matching[0]]
