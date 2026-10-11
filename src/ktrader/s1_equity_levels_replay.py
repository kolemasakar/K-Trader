"""Read-only ACHC.us Gerchik candidate replay using existing PR94 logic."""
from scripts.research.gerchik_seven_types_v0_1 import ResearchPolicy
from ktrader.s1_equity_level_rows import completed_daily, completed_weekly
from datetime import datetime, timezone
from ktrader.s1_existing_levels_bridge import detect_existing_levels

def candidate_levels(d1_candles):
    policy=ResearchPolicy(
        provenance="RESEARCH_CANDIDATE_US_EQUITY_SESSION_V1",
        directional_transitions=2,trend_defenses=2,
        historical_repetitions=2,mirror_defenses=2,
        paranormal_reference_bars=20,paranormal_multiple="2",
        calendar="US_EQUITY_SESSION_WALL_CLOCK")
    d1=completed_daily(d1_candles)
    w1=completed_weekly(d1_candles)
    daily=detect_existing_levels(d1,"D1",policy,asset_class="us_equity",calendar=policy.calendar)
    weekly=detect_existing_levels(w1,"W1",policy,asset_class="us_equity",calendar=policy.calendar)
    availability=[]
    for row in w1:
        after=next(x for x in d1_candles if int(datetime.fromisoformat(x["open_time"]).replace(tzinfo=timezone.utc).timestamp()*1000)>row[6])
        availability.append(int(datetime.fromisoformat(after["close_time"]).replace(tzinfo=timezone.utc).timestamp()*1000))
    for level in weekly:
        level["known_at_ms"]=max(level["known_at_ms"],availability[level["confirmation_index"]])
        for event in level["additional_patterns"]:
            # First subsequent closed D1 establishes availability of that weekly prefix.
            event["known_at_ms"]=next((a for row,a in zip(w1,availability) if row[6]+1>=event["known_at_ms"]),event["known_at_ms"])
    return {"D1":daily,"W1":weekly,"daily_bars":len(d1),"closed_weekly_bars":len(w1),
            "level_evidence_status":"AUTOMATED_RESEARCH_CANDIDATE_NOT_REVIEWED"}
