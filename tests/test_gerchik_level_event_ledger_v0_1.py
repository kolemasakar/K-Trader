"""Deterministic guard tests for the research-only Gerchik event ledger."""
import pytest
from scripts.research.gerchik_level_event_ledger_v0_1 import Evidence, LevelLedger, LEVEL_TYPES


def make(ledger, **changes):
    args = dict(symbol="SUIUSDT", timeframe="1d", price="2.125",
                tick_size="0.001", primary_type="MIRROR",
                formed_at="2026-09-01T00:00:00Z",
                formation_event_id="formation-1", source_field="high")
    args.update(changes)
    return ledger.record_formation(**args)


@pytest.mark.parametrize("kind", sorted(LEVEL_TYPES))
def test_seven_types_remain_candidates(kind):
    level = make(LevelLedger(), primary_type=kind)
    assert level.primary_type == kind and level.state == "CANDIDATE"


def test_tick_identity_and_no_duplicate_primary():
    ledger = LevelLedger()
    level = make(ledger)
    assert str(level.price) == "2.125"
    with pytest.raises(ValueError, match="already exists"):
        make(ledger, primary_type="HISTORICAL", formation_event_id="formation-2")


@pytest.mark.parametrize("field,tf", [("close", "1d"), ("high", "1h"), ("low", "5m")])
def test_reject_wrong_formation_sources(field, tf):
    with pytest.raises(ValueError):
        make(LevelLedger(), source_field=field, timeframe=tf)


def test_reject_off_tick():
    with pytest.raises(ValueError, match="exact tick"):
        make(LevelLedger(), price="2.1255")


def test_evidence_provenance_and_deduplication():
    ledger = LevelLedger()
    level = make(ledger)
    event = Evidence("e2", "TOUCH", "2026-09-02T00:00:00Z", "bar2")
    ledger.add_evidence(level, event)
    assert len(level.evidence) == 1
    with pytest.raises(ValueError, match="Duplicate"):
        ledger.add_evidence(level, event)
    with pytest.raises(ValueError, match="double-counted"):
        ledger.add_evidence(level, Evidence("formation-1", "TOUCH", "2026-09-03T00:00:00Z", "bar3"))
    with pytest.raises(ValueError, match="backdate"):
        ledger.add_evidence(level, Evidence("e0", "TOUCH", "2026-08-31T00:00:00Z", "bar0"))


def test_asof_visibility():
    ledger = LevelLedger()
    level = make(ledger)
    assert ledger.as_of("2026-08-31T23:59:59Z") == []
    assert ledger.as_of("2026-09-01T00:00:00Z") == [level]


def test_reject_non_utc_formation_and_asof():
    ledger = LevelLedger()
    for bad in ("2026-09-01T00:00:00", "2026-09-01T03:00:00+03:00", "invalid"):
        with pytest.raises(ValueError):
            make(ledger, formed_at=bad)
    make(ledger)
    for bad in ("2026-09-01T00:00:00", "2026-09-01T03:00:00+03:00", "invalid"):
        with pytest.raises(ValueError):
            ledger.as_of(bad)


def test_utc_equivalent_evidence_timestamp():
    ledger = LevelLedger()
    level = make(ledger)
    ledger.add_evidence(level, Evidence("e2", "TOUCH", "2026-09-01T00:00:01+00:00", "bar2"))
    assert ledger.as_of("2026-09-01T00:00:00+00:00") == [level]
