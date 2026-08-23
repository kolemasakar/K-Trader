from __future__ import annotations

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from ktrader.market.timeframes import datetime_from_ms, datetime_to_ms
from ktrader.outcomes.evaluator import SignalOutcome


class OutcomeRepository:
    """SQLite outcome store kept separate from live TradingDecision state."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA busy_timeout=5000")
        if self.path != ":memory:":
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=NORMAL")
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS signal_outcomes (
                decision_id TEXT PRIMARY KEY,
                provider_id TEXT NOT NULL,
                canonical_symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                grade TEXT NOT NULL,
                setup_score INTEGER NOT NULL,
                setup_type TEXT NOT NULL,
                engine_version TEXT NOT NULL,
                decision_time_ms INTEGER NOT NULL,
                entry TEXT,
                stop TEXT,
                target TEXT,
                planned_rr TEXT,
                status TEXT NOT NULL,
                entry_bar_open_time_ms INTEGER,
                resolved_bar_open_time_ms INTEGER,
                bars_to_entry INTEGER,
                bars_in_trade INTEGER,
                outcome_r TEXT,
                reason TEXT,
                evaluated_at_ms INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_signal_outcomes_bucket
                ON signal_outcomes(provider_id, canonical_symbol, setup_type, grade, status);
            CREATE INDEX IF NOT EXISTS idx_signal_outcomes_time
                ON signal_outcomes(decision_time_ms);
            """
        )
        self._connection.commit()

    def upsert(self, outcome: SignalOutcome) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO signal_outcomes (
                    decision_id, provider_id, canonical_symbol, side, grade,
                    setup_score, setup_type, engine_version, decision_time_ms,
                    entry, stop, target, planned_rr, status,
                    entry_bar_open_time_ms, resolved_bar_open_time_ms,
                    bars_to_entry, bars_in_trade, outcome_r, reason,
                    evaluated_at_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    status=excluded.status,
                    entry_bar_open_time_ms=excluded.entry_bar_open_time_ms,
                    resolved_bar_open_time_ms=excluded.resolved_bar_open_time_ms,
                    bars_to_entry=excluded.bars_to_entry,
                    bars_in_trade=excluded.bars_in_trade,
                    outcome_r=excluded.outcome_r,
                    reason=excluded.reason,
                    evaluated_at_ms=excluded.evaluated_at_ms
                """,
                _serialize(outcome),
            )

    def get(self, decision_id: str) -> SignalOutcome | None:
        row = self._connection.execute(
            "SELECT * FROM signal_outcomes WHERE decision_id=?",
            (decision_id,),
        ).fetchone()
        return None if row is None else _deserialize(row)

    def counts(self) -> dict[str, int]:
        rows = self._connection.execute(
            "SELECT status, COUNT(*) AS n FROM signal_outcomes GROUP BY status ORDER BY status"
        ).fetchall()
        return {str(row["status"]): int(row["n"]) for row in rows}

    def list_binary_resolved(self, *, limit: int = 10000) -> list[SignalOutcome]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        rows = self._connection.execute(
            """
            SELECT * FROM signal_outcomes
            WHERE status IN ('WIN', 'LOSS')
            ORDER BY decision_time_ms ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_deserialize(row) for row in rows]

    def close(self) -> None:
        self._connection.close()


def _serialize(outcome: SignalOutcome) -> tuple[object, ...]:
    return (
        outcome.decision_id,
        outcome.provider_id,
        outcome.canonical_symbol,
        outcome.side,
        outcome.grade,
        outcome.setup_score,
        outcome.setup_type,
        outcome.engine_version,
        datetime_to_ms(outcome.decision_time),
        _decimal(outcome.entry),
        _decimal(outcome.stop),
        _decimal(outcome.target),
        _decimal(outcome.planned_rr),
        outcome.status,
        _time_ms(outcome.entry_bar_open_time),
        _time_ms(outcome.resolved_bar_open_time),
        outcome.bars_to_entry,
        outcome.bars_in_trade,
        _decimal(outcome.outcome_r),
        outcome.reason,
        datetime_to_ms(outcome.evaluated_at),
    )


def _deserialize(row: sqlite3.Row) -> SignalOutcome:
    return SignalOutcome(
        decision_id=str(row["decision_id"]),
        provider_id=str(row["provider_id"]),
        canonical_symbol=str(row["canonical_symbol"]),
        side=str(row["side"]),
        grade=str(row["grade"]),
        setup_score=int(row["setup_score"]),
        setup_type=str(row["setup_type"]),
        engine_version=str(row["engine_version"]),
        decision_time=datetime_from_ms(int(row["decision_time_ms"])),
        entry=_from_decimal(row["entry"]),
        stop=_from_decimal(row["stop"]),
        target=_from_decimal(row["target"]),
        planned_rr=_from_decimal(row["planned_rr"]),
        status=str(row["status"]),
        entry_bar_open_time=_from_time_ms(row["entry_bar_open_time_ms"]),
        resolved_bar_open_time=_from_time_ms(row["resolved_bar_open_time_ms"]),
        bars_to_entry=int(row["bars_to_entry"]) if row["bars_to_entry"] is not None else None,
        bars_in_trade=int(row["bars_in_trade"]) if row["bars_in_trade"] is not None else None,
        outcome_r=_from_decimal(row["outcome_r"]),
        reason=str(row["reason"]) if row["reason"] is not None else None,
        evaluated_at=datetime_from_ms(int(row["evaluated_at_ms"])),
    )


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _from_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _time_ms(value: datetime | None) -> int | None:
    return None if value is None else datetime_to_ms(value)


def _from_time_ms(value: object) -> datetime | None:
    return None if value is None else datetime_from_ms(int(value))
