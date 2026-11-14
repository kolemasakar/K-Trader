# Shared D1/W1 strong levels — implementation checkpoint (2026-11-14)

Owner decision: automatic strong D1/W1 level selection is a SINGLE upstream
research service for S1, S2A, S2B, S3, S4, S5A and S5B.
K-Trader is analytics/research only and never executes broker trades.

## Implemented on this branch
- `src/ktrader/shared_strong_levels.py`: immutable causal shared registry.
- `tests/test_shared_strong_levels.py`: shared access, causal cutoff,
  rejection of unqualified candidates, stable deduplication.
- The shared registry intentionally does not invent or replace the owner's
  previously approved strong-level selection criteria.

## Integration NOT YET COMPLETE
- Retrieve the authoritative November S1 automatic strong-level algorithm and
  its tests. The available October `gerchik_seven_types_v0_1.py` returns
  `RESEARCH_CANDIDATE` and explicitly restricts itself to continuous UTC data;
  it is NOT an adequate replacement for the approved strong-level selector.
- Wire the authoritative selector's output to `shared_levels` for all S1-S5
  research replay entrypoints; remove independent human review requirement
  only for this research path.
- Execute tests on Oracle and replay S1 regression and S2A/S2B A/B.
- Record source hashes and results. No CI/runtime claims before execution.

This checkpoint prevents treating an incomplete October admission mechanism
as a new owner approval requirement, while also preventing unqualified
archetypes from silently becoming strong levels.
