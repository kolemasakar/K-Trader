# Prospective Ledger v1.2 Acceptance — 2026-09-16

Status: **ACCEPTED / INFRASTRUCTURE-ONLY CAUSALITY HARDENING**

## Trigger

At cutoff `2026-09-16T19:00:00Z`, pipeline v2 capture and funding passed, but resolver v1.3 failed closed on:

`PRIOR_IDENTITY_PRICE_MISMATCH`

Affected family:

- symbol `VTHOUSDT`
- side `LONG`
- entry time `2026-09-13T08:00:00Z`
- entry delta `0.0`
- stop delta `8.721498982971858e-09`

The stop drift was about `1.4924e-4` of accepted initial risk, above canonical v1.3 tolerance `1e-4`. The resolver therefore behaved correctly and no tolerance was relaxed.

## Root cause

Ledger v1.1 deduplicated by event identity but replaced the stored payload with the newest recomputation when the same event reappeared in later captures. It only added `ledger_conflict_with_prior_payload=true`.

This allowed an already observed historical setup to acquire a slightly different recomputed stop over time.

For the affected VTHOUSDT setup, entry remained exactly constant while the recomputed stop drifted across repeated captures. The causal first-seen event had:

- entry `0.00089887974`
- stop `0.0008404414667906131`

That stop exactly matches the accepted terminal observation carried in prior outcomes.

## Ledger v1.2 rule

Canonical prospective ledger semantics are now:

> The first valid payload for an event key is immutable. Later observations of the same event key are duplicate/recomputation audit evidence only and must never rewrite causal history.

Versioned implementation:

`research/strategy_benchmark_v1/prospective_v2_2_shadow_ledger_v1_2.py`

Compatibility entry point:

`research/strategy_benchmark_v1/prospective_v2_2_shadow_ledger.py`

Schema:

`ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2`

Audit fields include:

- `first_seen_payload_immutable=true`
- `raw_duplicate_event_occurrences`
- `conflicting_duplicate_event_occurrences`
- `conflicting_event_key_count`

## Real-data validation

Rebuild over all available prospective captures preserved aggregate sample structure:

- deduplicated events `393`
- eligible setups `61`
- unique eligible families `47`
- status counts unchanged: `61` eligible, `156` minimum-risk rejects, `176` structural-space rejects
- raw duplicate event occurrences `5991`
- conflicting duplicate occurrences `5991`
- conflicting event keys `391`

The affected VTHOUSDT first-seen payload matched the prior accepted entry and stop exactly (`stop delta = 0`).

Canonical v1.2 ledger hashes after rebuild:

- ledger summary SHA256 `03eebcd4b09e37e9b42a2ed6d9b3dd4840bcfe7c948c726550f23f2cf3234dce`
- ledger events SHA256 `2644a7781735aa9b5f2e48e858afbcbe6e54f139d2e682f6270bb4c61eeda210`
- ledger event-set SHA256 `de631c72a5cd932b3d7e3df66671d702296dfbbf30514bacc50df9dee2f9edc6`

## Pre-migration audit snapshot

The prior v1.1 canonical ledger was preserved before rebuilding:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/ledger_snapshots/20260916T190000Z_pre_v1_2/`

Hashes:

- old `deduplicated_events.jsonl`: `a31873d863ee5be87b8171946aca42452c2c2ded0a304d6d1d1a1ca153fd251a`
- old `ledger_summary.json`: `383028c6003dc80279e2866204e9a27d01beca1464c9d5eb832f7e9f6afa2a17`

## Regression / runtime acceptance

Self-contained regression test: **PASS**.

Pipeline v2 plan/preflight after v1.2 staging: **PASS**.

Repository-exact runtime staging SHA256:

- compatibility ledger: `165f630b8fec0f55fc71ef24bdbe920e3cd4d464d50cf49f5268174c39bf3df7`
- versioned v1.2 ledger: `b9043ae20a7298eb13c40297d101e74494182dc01a1253c1c5c68cd05cbfed27`

## 19:00Z controlled recovery

The already valid `19:00Z` capture and funding artifacts were reused. Capture was not repeated.

After rebuilding ledger v1.2, resolver v1.3 and all downstream stages passed.

Accepted state:

- families `47`
- resolved `47`
- unresolved `0`
- wins/losses `13/34`
- expectancy `-0.5989123384630131R`
- confirmation `3/3` resolved
- current open families `0`
- max prior entry delta `0.0`
- max prior stop delta `3.809370596741246e-10`
- holdout false
- production action false

State manifest SHA256:

`18d9ea1956f9035951c008c06cae0ca363c39fdc89599e1fa37a4c020cc4a077`

All `5/5` referenced source hashes were independently verified with `0` mismatches.

Recovery manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T190000Z_recovery_ledger_v1_2.json`

SHA256:

`f796ecdd2d3456ae6ca727179c12b15e25dbf78bebc21fd3e5a2a29a934a57a4`

The original failed execute manifest is retained as evidence.

## Governance conclusion

This change fixes prospective ledger causality only. It does **not** change:

- frozen strategy v2.2
- RR or 32-M15 max hold
- resolver v1.3 guard thresholds
- side/risk filters
- preregistration boundary
- holdout authorization
- production trading authorization
- Phase 11G sample thresholds

Resolver v1.3 fail-closed behavior is retained unchanged.