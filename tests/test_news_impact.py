from datetime import datetime, timedelta, timezone
import pytest
from ktrader.news_impact import NewsEvent, evaluate, parse_utc

NOW = "2026-09-28T12:00:00Z"

def event(**changes):
    data = dict(source="kgm", source_id="evt1", published_at="2026-09-28T11:00:00Z",
                received_at="2026-09-28T11:05:00Z", headline="Test event",
                assets=("BTCUSDT",), event_type="geopolitical", severity=3, confidence=0.9)
    data.update(changes)
    return NewsEvent.from_mapping(data)

def test_high_severity_defer():
    r = evaluate([event()], "BTCUSDT", NOW)
    assert r.action == "DEFER_NEW_ENTRY" and len(r.event_ids) == 1

def test_unrelated_not_blocked():
    assert evaluate([event()], "ETHUSDT", NOW).action == "NO_CHANGE"

def test_future_received_excluded():
    assert evaluate([event(received_at="2026-09-28T13:00:00Z",
                           published_at="2026-09-28T11:00:00Z")], "BTCUSDT", NOW).action == "NO_CHANGE"

def test_stale_excluded():
    assert evaluate([event(published_at="2026-09-27T01:00:00Z",
                           received_at="2026-09-27T01:01:00Z")], "BTCUSDT", NOW).action == "NO_CHANGE"

def test_low_confidence_unknown():
    assert evaluate([event(confidence=0.2)], "BTCUSDT", NOW).action == "UNKNOWN"

def test_missing_feed_unknown():
    assert evaluate([], "BTCUSDT", NOW).action == "UNKNOWN"

def test_timezone_required():
    with pytest.raises(ValueError):
        parse_utc("2026-09-28T12:00:00")

def test_invalid_provenance():
    with pytest.raises(ValueError):
        event(source="").validate()

def test_duplicate_identity():
    assert len(evaluate([event(), event()], "BTCUSDT", NOW).event_ids) == 1

def test_no_direction_or_trade_execution():
    r = evaluate([event()], "BTCUSDT", NOW)
    assert not hasattr(r, "direction") and not hasattr(r, "lot")
