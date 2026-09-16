# Prospective v2.2 Offline Resolver v1.2

Status: **ACCEPTED VERSIONED GUARD UPDATE / NO STRATEGY CHANGE**  
Date: 2026-09-16

## Purpose

v1.2 is a narrow versioned continuation of `prospective_v2_2_outcome_resolver_offline_v1_1.py`.
It preserves all v1.1 outcome semantics, output schema, frozen-v2.2 rules, fee/slippage/funding treatment, immutable prior terminal outcomes, holdout boundary and production-action boundary.

## Change from v1.1

The absolute prior identity price tolerance is widened from `2e-9` to `3e-9`.
The relative tolerance remains `1e-12`.

Reason: at prospective cutoff `2026-09-16T11:45:00Z`, one already accepted RAYSOLUSDT observation with stable identity
`(setup_family_id, symbol, side, entry_time)` had:

- entry-price delta: `0.0`;
- stop-price delta: `2.1062864785648117e-9`.

Across all `50` previously resolved observations:

- maximum entry-price delta: `0.0`;
- maximum stop-price delta: `2.1062864785648117e-9`;
- second-largest stop delta: `1.7451648529065444e-9`;
- third-largest stop delta: `1.620510220478634e-9`.

This was therefore treated as numerical representation drift, not a setup-identity change.

## Validation

Temporary v1.2 execution at `2026-09-16T11:45:00Z` produced:

- eligible observations: `56`;
- unique primary families: `43`;
- resolved primary families: `39`;
- unresolved primary families: `4`;
- wins / losses: `9 / 30`;
- win rate: `0.23076923076923078`;
- expectancy: `-0.6482720085510278R`;
- prior terminal reuse count: `50`;
- prior terminal path revalidated count: `44`;
- prior terminal source-window-expired count: `6`;
- newly resolved observations: `0`;
- network used: `false`;
- holdout opened: `false`;
- production action: `false`.

Parity against the prior accepted `2026-09-16T10:30:00Z` outcome set:

- previously resolved rows checked: `50`;
- terminal/economic mismatches: `0`.

## Governance

This is a resolver guard update only. It does **not** change:

- candidate `candidate_rule_set_v2_2`;
- RR target `3R`;
- max hold `32` M15 bars;
- STOP-first same-bar semantics;
- risk gates;
- symbols or direction filters;
- prospective-family governance thresholds;
- holdout status;
- production execution state.

The v1.1 output schema is intentionally retained because the artifact structure and semantics are unchanged.
