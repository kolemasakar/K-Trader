from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterable
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from ktrader.market.timeframes import datetime_from_ms, datetime_to_ms, require_utc
from ktrader.models import NormalizedCandle

_SCHEMA_VERSION = 2


class CandleRepository:
    """SQLite-backed normalized candle repository with WAL persistence."""

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._configure()
        self._initialize_schema()

    @property
    def journal_mode(self) -> str:
        row = self._connection.execute("PRAGMA journal_mode").fetchone()
        return str(row[0]).lower()

    def _configure(self) -> None:
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA busy_timeout=5000")
        if self.path != ":memory:":
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=NORMAL")

    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS candles (
                provider_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                open_time_ms INTEGER NOT NULL,
                close_time_ms INTEGER NOT NULL,
                open_price TEXT NOT NULL,
                high_price TEXT NOT NULL,
                low_price TEXT NOT NULL,
                close_price TEXT NOT NULL,
                volume TEXT NOT NULL,
                quote_volume TEXT,
                trade_count INTEGER,
                taker_buy_volume TEXT,
                taker_buy_quote_volume TEXT,
                closed INTEGER NOT NULL CHECK (closed IN (0, 1)),
                ingested_at_ms INTEGER NOT NULL,
                source_kind TEXT NOT NULL DEFAULT 'provider',
                derived_from_interval TEXT,
                PRIMARY KEY (provider_id, symbol, interval, open_time_ms)
            );

            CREATE INDEX IF NOT EXISTS idx_candles_recent
                ON candles(provider_id, symbol, interval, open_time_ms DESC);

            CREATE TABLE IF NOT EXISTS bootstrap_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                started_at_ms INTEGER NOT NULL,
                completed_at_ms INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED')),
                interval_counts_json TEXT NOT NULL,
                error TEXT
            );
            """
        )
        columns = {
            str(row["name"])
            for row in self._connection.execute("PRAGMA table_info(candles)").fetchall()
        }
        if "source_kind" not in columns:
            self._connection.execute(
                "ALTER TABLE candles ADD COLUMN source_kind TEXT NOT NULL DEFAULT 'provider'"
            )
        if "derived_from_interval" not in columns:
            self._connection.execute(
                "ALTER TABLE candles ADD COLUMN derived_from_interval TEXT"
            )
        self._connection.execute(f"PRAGMA user_version={_SCHEMA_VERSION}")
        self._connection.commit()

    def upsert_many(
        self,
        candles: Iterable[NormalizedCandle],
        *,
        source_kind: str = "provider",
        derived_from_interval: str | None = None,
    ) -> int:
        if source_kind not in {"provider", "aggregate"}:
            raise ValueError("source_kind must be provider or aggregate")
        if source_kind == "provider" and derived_from_interval is not None:
            raise ValueError("provider candles cannot set derived_from_interval")
        if source_kind == "aggregate" and not derived_from_interval:
            raise ValueError("aggregate candles require derived_from_interval")
        materialized = list(candles)
        if not materialized:
            return 0
        ingested_at_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        rows = [
            self._serialize(
                candle,
                ingested_at_ms,
                source_kind=source_kind,
                derived_from_interval=derived_from_interval,
            )
            for candle in materialized
        ]
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO candles (
                    provider_id, symbol, interval, open_time_ms, close_time_ms,
                    open_price, high_price, low_price, close_price, volume,
                    quote_volume, trade_count, taker_buy_volume,
                    taker_buy_quote_volume, closed, ingested_at_ms,
                    source_kind, derived_from_interval
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider_id, symbol, interval, open_time_ms)
                DO UPDATE SET
                    close_time_ms=excluded.close_time_ms,
                    open_price=excluded.open_price,
                    high_price=excluded.high_price,
                    low_price=excluded.low_price,
                    close_price=excluded.close_price,
                    volume=excluded.volume,
                    quote_volume=excluded.quote_volume,
                    trade_count=excluded.trade_count,
                    taker_buy_volume=excluded.taker_buy_volume,
                    taker_buy_quote_volume=excluded.taker_buy_quote_volume,
                    closed=excluded.closed,
                    ingested_at_ms=excluded.ingested_at_ms,
                    source_kind=excluded.source_kind,
                    derived_from_interval=excluded.derived_from_interval
                """,
                rows,
            )
        return len(materialized)

    def load_recent(
        self,
        provider_id: str,
        symbol: str,
        interval: str,
        *,
        limit: int,
    ) -> list[NormalizedCandle]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        rows = self._connection.execute(
            """
            SELECT * FROM candles
            WHERE provider_id=? AND symbol=? AND interval=?
            ORDER BY open_time_ms DESC
            LIMIT ?
            """,
            (provider_id, symbol, interval, limit),
        ).fetchall()
        return [self._deserialize(row) for row in reversed(rows)]

    def latest(self, provider_id: str, symbol: str, interval: str) -> NormalizedCandle | None:
        rows = self.load_recent(provider_id, symbol, interval, limit=1)
        return rows[0] if rows else None

    def count(self, provider_id: str, symbol: str, interval: str) -> int:
        row = self._connection.execute(
            """
            SELECT COUNT(*) FROM candles
            WHERE provider_id=? AND symbol=? AND interval=?
            """,
            (provider_id, symbol, interval),
        ).fetchone()
        return int(row[0])

    def source_info(
        self,
        provider_id: str,
        symbol: str,
        interval: str,
        open_time: datetime,
    ) -> tuple[str, str | None] | None:
        require_utc(open_time)
        row = self._connection.execute(
            """
            SELECT source_kind, derived_from_interval FROM candles
            WHERE provider_id=? AND symbol=? AND interval=? AND open_time_ms=?
            """,
            (provider_id, symbol, interval, datetime_to_ms(open_time)),
        ).fetchone()
        if row is None:
            return None
        return str(row["source_kind"]), (
            str(row["derived_from_interval"])
            if row["derived_from_interval"] is not None
            else None
        )

    def interval_counts(self, provider_id: str, symbol: str) -> dict[str, int]:
        rows = self._connection.execute(
            """
            SELECT interval, COUNT(*) AS n FROM candles
            WHERE provider_id=? AND symbol=?
            GROUP BY interval
            """,
            (provider_id, symbol),
        ).fetchall()
        return {str(row["interval"]): int(row["n"]) for row in rows}

    def record_bootstrap_run(
        self,
        *,
        provider_id: str,
        symbol: str,
        started_at: datetime,
        completed_at: datetime,
        status: str,
        interval_counts: dict[str, int],
        error: str | None = None,
    ) -> int:
        require_utc(started_at)
        require_utc(completed_at)
        if status not in {"SUCCESS", "FAILED"}:
            raise ValueError("status must be SUCCESS or FAILED")
        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT INTO bootstrap_runs (
                    provider_id, symbol, started_at_ms, completed_at_ms,
                    status, interval_counts_json, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider_id,
                    symbol,
                    datetime_to_ms(started_at),
                    datetime_to_ms(completed_at),
                    status,
                    json.dumps(interval_counts, sort_keys=True),
                    error,
                ),
            )
        return int(cursor.lastrowid)

    def latest_bootstrap_run(self, provider_id: str, symbol: str) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT * FROM bootstrap_runs
            WHERE provider_id=? AND symbol=?
            ORDER BY id DESC LIMIT 1
            """,
            (provider_id, symbol),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": int(row["id"]),
            "provider_id": str(row["provider_id"]),
            "symbol": str(row["symbol"]),
            "started_at": datetime_from_ms(int(row["started_at_ms"])),
            "completed_at": datetime_from_ms(int(row["completed_at_ms"])),
            "status": str(row["status"]),
            "interval_counts": json.loads(str(row["interval_counts_json"])),
            "error": row["error"],
        }

    def backup_to(self, destination: str | Path) -> Path:
        """Create an atomic, integrity-checked online SQLite backup."""
        if self.path == ":memory:":
            raise ValueError("cannot create durable backup from in-memory repository")
        target = Path(destination).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(target.suffix + ".tmp")
        temp.unlink(missing_ok=True)
        try:
            with sqlite3.connect(str(temp)) as backup_connection:
                self._connection.backup(backup_connection)
                row = backup_connection.execute("PRAGMA integrity_check").fetchone()
                if row is None or str(row[0]).lower() != "ok":
                    raise RuntimeError("SQLite backup integrity_check failed")
            os.replace(temp, target)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
        return target

    @staticmethod
    def verify_database(path: str | Path) -> bool:
        target = Path(path).expanduser().resolve()
        if not target.is_file():
            return False
        try:
            connection = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
            try:
                row = connection.execute("PRAGMA integrity_check").fetchone()
                return row is not None and str(row[0]).lower() == "ok"
            finally:
                connection.close()
        except sqlite3.DatabaseError:
            return False

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _serialize(
        candle: NormalizedCandle,
        ingested_at_ms: int,
        *,
        source_kind: str,
        derived_from_interval: str | None,
    ) -> tuple[object, ...]:
        return (
            candle.provider_id,
            candle.symbol,
            candle.interval,
            datetime_to_ms(candle.open_time),
            datetime_to_ms(candle.close_time),
            str(candle.open),
            str(candle.high),
            str(candle.low),
            str(candle.close),
            str(candle.volume),
            _decimal_text(candle.quote_volume),
            candle.trade_count,
            _decimal_text(candle.taker_buy_volume),
            _decimal_text(candle.taker_buy_quote_volume),
            1 if candle.closed else 0,
            ingested_at_ms,
            source_kind,
            derived_from_interval,
        )

    @staticmethod
    def _deserialize(row: sqlite3.Row) -> NormalizedCandle:
        return NormalizedCandle(
            provider_id=str(row["provider_id"]),
            symbol=str(row["symbol"]),
            interval=str(row["interval"]),
            open_time=datetime_from_ms(int(row["open_time_ms"])),
            close_time=datetime_from_ms(int(row["close_time_ms"])),
            open=Decimal(str(row["open_price"])),
            high=Decimal(str(row["high_price"])),
            low=Decimal(str(row["low_price"])),
            close=Decimal(str(row["close_price"])),
            volume=Decimal(str(row["volume"])),
            quote_volume=_decimal_from_db(row["quote_volume"]),
            trade_count=int(row["trade_count"]) if row["trade_count"] is not None else None,
            taker_buy_volume=_decimal_from_db(row["taker_buy_volume"]),
            taker_buy_quote_volume=_decimal_from_db(row["taker_buy_quote_volume"]),
            closed=bool(row["closed"]),
        )


def _decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else str(value)


def _decimal_from_db(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))
