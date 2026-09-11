# Phase 11G Checkpoint — Canonical Prospective-Control Hardening

Date: 2026-09-11

Status: **REPOSITORY TOOLING HARDENED / TRADING SEMANTICS UNCHANGED / PRODUCTION NOT REDEPLOYED**

## Purpose

This checkpoint closes the engineering follow-up identified by the accepted 2026-09-10→11 24h prospective control: the long-run control/report path is now repository-owned, deterministic, resumable and explicitly fail-closed at the UTC-midnight daily-range boundary.

It does **not** close Phase 11G continuous discovery and does **not** activate Phase 12.

## Change set

PR #48 introduces:

- `src/ktrader/replay/prospective.py` — canonical prospective-control core;
- `scripts/run_prospective_control.py` — operator CLI for shard execution/resume and merge;
- `tests/test_phase11g_prospective_control.py` — focused regression suite;
- `docs/PROSPECTIVE_CONTROL_SPEC.md` — canonical control contract;
- `src/ktrader/replay/__init__.py` exports;
- CI focused Phase 11G test execution plus amd64/arm64 image packaging checks for the new CLI.

## Causal context contract

At each logical cutoff `T` the utility:

- selects the newest recorded universe snapshot with `captured_at <= T`;
- accepts exact `300s` context age;
- rejects context strictly older than `300s` as stale;
- uses the recorded top-N order exactly as captured;
- never substitutes a lower-ranked symbol when a selected symbol lacks sufficient history;
- uses only provider-recorded MTF candles closed by `T` through canonical `slice_datasets_asof()`;
- calls the same canonical `analyze_candle_snapshot()` path used by replay/live analysis.

No current market state may backfill an older logical cutoff.

## UTC-midnight handling

The 24h control exposed 17 instances of:

`ValueError: 5m day sequence is empty`

at the UTC-day boundary after history-ready slots had no closed current-day M5 bar yet.

The canonical behavior is now explicit:

- detect the absence of a current-UTC-day closed M5 bar before invoking the analyzer;
- record slot state `ANALYSIS_ERROR` with the exact error identity;
- do not carry forward the previous UTC day's observed range;
- do not synthesize a `00:00` candle;
- do not fabricate a daily range;
- do not emit a synthetic `NO_TRADE` decision.

This preserves the canonical ATR-used contract instead of weakening it to remove a reporting edge case.

## Deterministic long-run execution

Logical cutoffs are assigned to shards by stable global cutoff index:

`shard_index = cutoff_index mod shard_count`

Each shard records exact archive/config/bundle provenance, deterministic cutoff records, completion state and semantic SHA-256.

Partial shards may be checkpointed atomically and resumed only when archive/config/window/shard/bundle provenance matches exactly.

Merge requires:

- every shard index exactly once;
- every shard complete;
- identical non-shard provenance;
- exact reconstruction of the full logical cutoff sequence.

Equivalent monolithic and sharded/resumed runs therefore produce the same final report payload and `report_sha256`.

## Explicit accounting

Every selected symbol/cutoff slot is one of:

- `ANALYZED`;
- `HISTORY_FAIL`;
- `ANALYSIS_ERROR`.

Missing/stale context remains cutoff-level fail-closed state and creates no symbol slots.

The report preserves explicit counts for history failures, analysis errors, decision records, reason codes, setup types, hard-gate funnel, tradable records and unique stable signals.

## Validation

Focused regression added for:

- UTC-midnight empty-current-day-M5 behavior;
- exact `300s` context-age boundary and `>300s` stale boundary;
- partial checkpoint + resume equivalence to uninterrupted execution;
- two-shard merge equivalence to monolithic execution;
- deterministic report semantic SHA equivalence;
- missing selected-symbol bundle remaining `HISTORY_FAIL` with no shortlist substitution.

Pre-documentation CI evidence on PR #48:

- Phase 11G focused tests: `4 passed`;
- Python 3.12 repository-wide regression: `208 passed`;
- Python 3.14 repository-wide regression: PASS.

The final PR head remains subject to the canonical `canonical-merge-gate`, including amd64 and arm64 image checks. PR #48 becomes accepted canonical state only after GitHub merges it under the active repository ruleset.

## Invariants preserved

No change was made to:

- FAST production profile `M5 / 60m`;
- setup expiry boundary (`<=60m` valid, `>60m` expired);
- `RR >= 3`;
- ATR-used calculation or `>80%` hard reject;
- HTF directional-alignment rules;
- STRONG/confirmed primary-level requirement;
- structural stop or nearest structural target;
- Setup Score / Grade semantics;
- D1/MTF history requirements;
- provider/context freshness rules;
- outcome semantics;
- probability/calibration policy;
- dataset-catalogue materialization rules.

INTRADAY/M15 and MEDIUM/H1 remain research-only.

## Production boundary

Accepted production runtime remains:

`30119a44fa82b1029d2de6e3a6f76320a7705079`

This checkpoint does not authorize or perform a new production deployment. Repository `main` may therefore contain the prospective-control utility while the running production image remains on the previous accepted runtime SHA until a separate deployment decision.

## Next work

1. keep provider-recorded Binance USD-M capture active;
2. use the canonical prospective-control utility for future long-window controls instead of temporary ad-hoc scripts;
3. continue natural FAST/M5 discovery under unchanged hard gates;
4. materialize/register a new Phase 11G chain only after a natural LONG/SHORT signal survives every hard gate with exact provenance;
5. evaluate outcomes only from subsequent real provider bars;
6. keep M15/H1 research-only and Phase 12 inactive until a separate explicit approval gate.
