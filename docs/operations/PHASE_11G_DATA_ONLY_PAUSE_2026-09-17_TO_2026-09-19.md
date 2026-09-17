# Phase 11G Data-Only Pause Window

Status: **APPROVED OPERATING BOUNDARY**

Window (Europe/Kyiv): `2026-09-17 09:00` through `2026-09-19 10:00`.
UTC equivalent: `2026-09-17T06:00:00Z` through `2026-09-19T07:00:00Z`.

## Purpose

Continue causal prospective evidence collection and verification while development work is paused. This window is data-only: no candidate redesign, no production promotion and no integration cutover.

## Allowed

- sequential closed-bar M15 prospective pipeline execution;
- resolver v1.3 continuation using immediately previous accepted outcomes;
- immutable ledger/evidence/state artifact creation;
- data-quality watchdog checks;
- provenance/hash/invariant verification;
- descriptive/statistical diagnostics already authorized by the current evidence tier;
- MFE/MAE and failure-mode diagnostics;
- portfolio concentration diagnostics without policy selection;
- storage/health monitoring;
- material checkpoint creation when an evidence-tier boundary is crossed.

## Frozen / prohibited during the pause

- no mutation of `candidate_rule_set_v2_2`;
- no change to RR, SL/TP, max-hold, filters, sides or entry logic;
- no holdout access;
- no Phase 12 activation;
- no production trading or trading authorization;
- no production risk-policy selection;
- no Plugin cutover;
- no broad strategy discovery inside K-Trader;
- no code/config development commits except an emergency fix required to restore causal collection, which must be explicitly documented as such.

## Causal collection contract

For each accepted M15 cutoff:

1. cutoff must be a fully closed M15 bar;
2. `prior_outcomes` must point to the immediately preceding accepted cutoff;
3. pipeline must stop on the first non-PASS stage;
4. immutable output collision must fail closed;
5. resolver must remain `v1.3`;
6. strategy must remain `candidate_rule_set_v2_2`;
7. `holdout_opened=false`;
8. `production_action=false`;
9. frozen harness/protocol hashes must remain pinned;
10. accepted prior terminal outcomes remain immutable.

## Evidence-tier behavior

- `30-49` resolved primary families: diagnostics only.
- `50-99`: hypotheses/ablation proposals may be produced, but frozen v2.2 remains unchanged.
- `>=100`: recalibration proposal may be considered only after the pause and only under the Phase 11G closure contract; this milestone does not promote production.

If a tier boundary is crossed, record a material checkpoint. Do not automatically open holdout or Phase 12.

## Periodic verification

At least periodically during collection verify:

- latest state manifest and all source hashes;
- unique/resolved/unresolved family accounting;
- discovery/confirmation boundary;
- candle continuity, duplicate timestamps and future/equal-bar contamination;
- current open families and max-hold boundaries;
- production health/read-only invariant;
- disk utilization and artifact-write availability.

Any invariant failure changes state to `FAIL_CLOSED` and stops advancement until the cause is understood.

## Resume checkpoint at end of pause

At or after `2026-09-19T07:00:00Z` produce a final accepted control slice containing:

- latest accepted cutoff;
- unique/resolved/unresolved families;
- confirmation counts;
- wins/losses/expectancy;
- evidence tier and Path-A shortfall;
- latest state/pipeline/evidence hashes;
- data-quality result;
- path-quality result;
- portfolio concentration diagnostics;
- health/storage state;
- any failures or gaps during the pause;
- exact development resume work order.
