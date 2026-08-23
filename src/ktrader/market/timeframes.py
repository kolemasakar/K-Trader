from __future__ import annotations

from datetime import datetime, timedelta, timezone

CANONICAL_INTERVALS = ("1d", "4h", "1h", "15m", "5m")

_INTERVAL_SECONDS = {
    "5m": 5 * 60,
    "15m": 15 * 60,
    "1h": 60 * 60,
    "4h": 4 * 60 * 60,
    "1d": 24 * 60 * 60,
}


def interval_seconds(interval: str) -> int:
    try:
        return _INTERVAL_SECONDS[interval]
    except KeyError as exc:
        raise ValueError(f"Unsupported canonical interval: {interval!r}") from exc


def interval_ms(interval: str) -> int:
    return interval_seconds(interval) * 1000


def require_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamp must be timezone-aware UTC")
    if value.utcoffset() != timedelta(0):
        raise ValueError("Timestamp must be normalized to UTC")
    return value.astimezone(timezone.utc)


def datetime_to_ms(value: datetime) -> int:
    require_utc(value)
    return int(value.timestamp() * 1000)


def datetime_from_ms(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def expected_close_time(open_time: datetime, interval: str) -> datetime:
    require_utc(open_time)
    return open_time + timedelta(milliseconds=interval_ms(interval) - 1)


def is_aligned_open(open_time: datetime, interval: str) -> bool:
    return datetime_to_ms(open_time) % interval_ms(interval) == 0
