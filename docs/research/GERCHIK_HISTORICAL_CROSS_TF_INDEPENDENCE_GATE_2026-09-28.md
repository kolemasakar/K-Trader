# Historical D1/W1 physical-event independence gate

The historical candidate aggregator now requires explicit UTC source-bar `opened_at` and `closed_at` for each independently reviewed event. A group with overlapping source-bar intervals is conservatively withheld from historical candidate formation even if the D1/W1 bars have different identifiers. Missing or reversed intervals fail closed. Two genuinely disjoint reviewed bars at the same exact tick price may still form a HISTORICAL research candidate. This is not an intrabar event-order inference or automatic structural detector.

Updated regression fixtures in both historical and compatibility-wrapper suites. Added overlapping D1/W1 and missing-bar-start regressions. **Test status: not yet independently run on this new commit; prior 14/14 results do not apply to this change.**

Scope limitation: the separate `gerchik_cross_tf_luft_v0_2.py` confirmation view still checks differing event IDs, not physical-bar overlap; do not use its pair confirmation as proof of independent market events until its evidence schema and overlap gate are aligned. A D1/W1 overlap can represent the same physical move, but overlapping bars do not invariably prove the same move; this intentionally prioritizes false-positive prevention pending event-level provenance. No live trading.
