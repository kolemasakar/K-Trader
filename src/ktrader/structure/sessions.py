from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class SessionDefinition:
    name: str
    timezone: str
    start_local: time
    end_local: time


@dataclass(frozen=True, slots=True)
class SessionContext:
    timestamp_utc: datetime
    active_sessions: tuple[str, ...]
    overlap: bool
    presentation_time: datetime


DEFAULT_SESSIONS = (
    SessionDefinition("TOKYO", "Asia/Tokyo", time(9, 0), time(18, 0)),
    SessionDefinition("LONDON", "Europe/London", time(8, 0), time(17, 0)),
    SessionDefinition("NEW_YORK", "America/New_York", time(8, 0), time(17, 0)),
)


def _inside(local_time: time, start: time, end: time) -> bool:
    if start < end:
        return start <= local_time < end
    return local_time >= start or local_time < end


def classify_sessions(
    timestamp_utc: datetime,
    *,
    definitions: tuple[SessionDefinition, ...] = DEFAULT_SESSIONS,
    presentation_timezone: str = "Europe/Kyiv",
) -> SessionContext:
    if timestamp_utc.tzinfo is None or timestamp_utc.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    utc = timestamp_utc.astimezone(ZoneInfo("UTC"))

    active: list[str] = []
    for definition in definitions:
        local = utc.astimezone(ZoneInfo(definition.timezone))
        if _inside(
            local.timetz().replace(tzinfo=None),
            definition.start_local,
            definition.end_local,
        ):
            active.append(definition.name)

    return SessionContext(
        timestamp_utc=utc,
        active_sessions=tuple(active),
        overlap=len(active) >= 2,
        presentation_time=utc.astimezone(ZoneInfo(presentation_timezone)),
    )
