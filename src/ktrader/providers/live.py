from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ktrader.models import NormalizedCandle


@dataclass(frozen=True, slots=True)
class LiveCandleEvent:
    candle: NormalizedCandle
    event_time: datetime
    received_at: datetime
    connection_id: int = 0
    raw_topic: str | None = None

    @classmethod
    def now(
        cls,
        candle: NormalizedCandle,
        *,
        event_time: datetime | None = None,
        connection_id: int = 0,
        raw_topic: str | None = None,
    ) -> "LiveCandleEvent":
        current = datetime.now(timezone.utc)
        return cls(
            candle=candle,
            event_time=event_time or current,
            received_at=current,
            connection_id=connection_id,
            raw_topic=raw_topic,
        )
