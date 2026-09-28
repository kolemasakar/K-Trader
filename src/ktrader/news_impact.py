"""Deterministic, read-only news impact screening. No trading or fetching."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
import hashlib
import json

UTC = timezone.utc
Action = Literal["NO_CHANGE", "REVIEW", "DEFER_NEW_ENTRY", "UNKNOWN"]

def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must contain timezone")
    return dt.astimezone(UTC)

@dataclass(frozen=True)
class NewsEvent:
    source: str
    source_id: str
    published_at: str
    received_at: str
    headline: str
    assets: tuple[str, ...]
    event_type: str
    severity: int
    confidence: float
    evidence_urls: tuple[str, ...] = ()
    scheduled_at: str | None = None
    revision: int = 1

    @classmethod
    def from_mapping(cls, obj: dict) -> "NewsEvent":
        required = ("source", "source_id", "published_at", "received_at",
                    "headline", "assets", "event_type", "severity", "confidence")
        if any(k not in obj for k in required):
            raise ValueError("missing news fields")
        return cls(source=str(obj["source"]), source_id=str(obj["source_id"]),
                   published_at=str(obj["published_at"]), received_at=str(obj["received_at"]),
                   headline=str(obj["headline"]), assets=tuple(obj["assets"]),
                   event_type=str(obj["event_type"]), severity=int(obj["severity"]),
                   confidence=float(obj["confidence"]),
                   evidence_urls=tuple(obj.get("evidence_urls", ())),
                   scheduled_at=obj.get("scheduled_at"), revision=int(obj.get("revision", 1)))

    def validate(self) -> None:
        if not self.source or not self.source_id or not self.headline:
            raise ValueError("empty provenance or headline")
        if not 0 <= self.severity <= 3 or not 0 <= self.confidence <= 1:
            raise ValueError("invalid severity/confidence")
        if self.revision < 1:
            raise ValueError("invalid revision")
        if not all(isinstance(a, str) and a for a in self.assets):
            raise ValueError("invalid assets")
        if parse_utc(self.published_at) > parse_utc(self.received_at):
            raise ValueError("received before published")
        if self.scheduled_at:
            parse_utc(self.scheduled_at)

    @property
    def identity(self) -> str:
        return hashlib.sha256(f"{self.source}|{self.source_id}|{self.revision}".encode()).hexdigest()

@dataclass(frozen=True)
class Impact:
    symbol: str
    action: Action
    event_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    as_of: str

def evaluate(events: list[NewsEvent], symbol: str, as_of: str,
             max_age_minutes: int = 360, min_confidence: float = 0.7) -> Impact:
    """Conservative decision support; never emits BUY/SELL or adjusts position size.

    A high-severity relevant recent item defers *new entries* for human/risk
    review. Unknown mapping/data returns UNKNOWN rather than inferred safety.
    """
    now = parse_utc(as_of)
    if max_age_minutes <= 0 or not 0 <= min_confidence <= 1:
        raise ValueError("invalid configuration")
    if not symbol:
        raise ValueError("symbol required")
    reasons: list[str] = []
    relevant: list[str] = []
    actions: list[Action] = []
    for event in events:
        event.validate()
        received, published = parse_utc(event.received_at), parse_utc(event.published_at)
        if received > now or published > now:
            continue  # strict as-of; no future revisions
        if symbol not in event.assets and "*" not in event.assets:
            continue
        if (now - published).total_seconds() > max_age_minutes * 60:
            continue
        relevant.append(event.identity)
        if event.confidence < min_confidence:
            actions.append("UNKNOWN")
            reasons.append("relevant_event_low_confidence")
        elif event.severity >= 3:
            actions.append("DEFER_NEW_ENTRY")
            reasons.append("relevant_high_severity_news")
        elif event.severity == 2:
            actions.append("REVIEW")
            reasons.append("relevant_moderate_news")
        else:
            reasons.append("relevant_low_severity_news")
    if not events:
        return Impact(symbol, "UNKNOWN", (), ("no_news_data_not_safe",), as_of)
    priority: tuple[Action, ...] = ("DEFER_NEW_ENTRY", "UNKNOWN", "REVIEW")
    action: Action = next((a for a in priority if a in actions), "NO_CHANGE")
    return Impact(symbol, action, tuple(sorted(set(relevant))), tuple(sorted(set(reasons))), as_of)

def canonical_record(event: NewsEvent) -> str:
    event.validate()
    return json.dumps(event.__dict__, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
