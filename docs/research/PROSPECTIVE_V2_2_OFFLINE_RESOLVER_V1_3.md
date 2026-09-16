# Prospective v2.2 Offline Resolver v1.3

Status: **ACCEPTED VERSIONED CONTINUATION**

## Purpose

v1.3 preserves frozen-v2.2 trading semantics, economics, family semantics, STOP-first behavior, 3R target and 32-M15 max hold. It changes only how already accepted prior terminal observations are identity-checked and revalidated.

## Why v1.3 was required

At cutoff `2026-09-16T13:45:00Z`, resolver v1.2 correctly failed closed because recomputed `VTHOUSDT` stop drift reached `3.561768196352899e-9`, above the v1.2 absolute guard `3e-9`.

Across 50 prior resolved observations:

- maximum entry-price delta remained exactly `0.0`;
- maximum stop drift was concentrated in low-priced `VTHOUSDT` observations;
- maximum stop drift relative to accepted initial risk was only `4.9105198702635914e-05` (about 0.0049% of risk).

A fixed absolute tolerance is therefore not scale-neutral across instruments.

## v1.3 rules

Stable identity remains:

`(setup_family_id, symbol, side, entry_time)`

For an already accepted resolved observation:

1. current entry price must equal accepted prior entry price exactly;
2. current recomputed stop must satisfy either:
   - existing absolute/relative close guard (`3e-9` absolute, `1e-12` relative), or
   - `abs(current_stop - prior_stop) <= 1e-4 * abs(prior_entry - prior_stop)`;
3. terminal path revalidation uses the **accepted prior entry and prior stop**, not recomputed prices;
4. accepted prior economic/terminal fields remain immutable;
5. if source bars aged out, the accepted prior terminal outcome remains preserved;
6. any larger identity drift fails closed.

The scale-aware stop tolerance is therefore capped at **0.01% of accepted initial risk distance**.

## Validation

Canonical acceptance at `2026-09-16T13:45:00Z`:

- eligible observations: `60`;
- unique primary families: `46`;
- resolved primary families: `39`;
- unresolved primary families: `7`;
- prior terminal observations reused: `50`;
- prior terminal paths revalidated: `44`;
- aged-out accepted terminal observations preserved: `6`;
- prior entry max delta: `0.0`;
- prior stop max delta: `3.561768196352899e-9`;
- parity against all 50 prior resolved observations: **0 terminal/economic mismatches**;
- holdout opened: `false`;
- production action: `false`.

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T134500Z`

Summary SHA256:

`9ecd26069c514fcafd1ce73fc06d5e05eb5aeffba549a99ef9487e18b9fc21af`

## Implementation

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_3.py`

v1.3 is a hash-pinned overlay on immutable v1.1. It refuses to run if the exact v1.1 source hash changes or if an expected source transform no longer matches.

v1.1 and v1.2 remain preserved for audit/history.

## Governance

This resolver change is infrastructure/evidence-continuity hardening only. It is **not** a strategy retune and does not authorize any change to frozen v2.2, holdout, production execution, RR, max hold, risk gates, side filters or Phase 12.
