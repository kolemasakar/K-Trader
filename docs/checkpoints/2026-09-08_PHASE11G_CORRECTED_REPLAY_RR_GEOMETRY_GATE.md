# Phase 11G Corrected Replay / RR Geometry Gate

Updated: 2026-09-08

Status: ACTIVE RESEARCH CHECKPOINT / PR #33 CONTRACT FIX VALIDATED / RR GEOMETRY AUDIT NEXT.

## Canonical repository and production baseline

- repository `main` SHA before this documentation checkpoint: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- commit subject: `Fix Phase 11G side-to-regime scoring contract (#33)`;
- post-merge Tests run `34177001398`: PASS;
- post-merge CI run `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Deploy Production #9 run `34177978988`: SUCCESS;
- deployed image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- production container: healthy;
- provider REST/WebSocket acceptance: PASS;
- MTF API acceptance: PASS;
- Phase 10 Action live acceptance: PASS;
- runtime scanner acceptance during deploy reported `status=DEGRADED`, `symbols_ready=18`, `symbols_failed=2`; this did not fail service health or deployment acceptance.

The deployed runtime and repository code identity were therefore aligned at `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab` before this documentation-only checkpoint.

## Dataset catalogue state remains unchanged

No new Phase 11G chain was materialized or registered during the corrected-discovery work.

Current canonical catalogue:

- path: `/data/research/phase11g/catalogue.json`;
- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- SUIUSDT entry: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- XRPUSDT entry: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- both outcome samples remain `null`;
- prior final `load_dataset_catalogue(..., verify_artifacts=True)`: PASS.

No probability calibration was performed. `estimated_probability` remains null/N/A.

## Historical discovery before the contract fix

Read-only historical discovery used four consecutive provider-recorded windows under the unchanged strict context policy.

Window summary:

- Window #1: `2026-09-07T18:55Z` through `20:10Z`, 40 MTF-passing symbol-window runs, zero signals;
- Window #2: `20:15Z` through `21:30Z`, 42 MTF-passing symbol-window runs, zero signals;
- Window #3: `21:35Z` through `22:50Z`, archive SHA `b511599cce4116aa1cd93f07e1836ab5a4ce19e2750b07f27b372cf4c9b002ff`, 41 MTF-passing runs, zero signals;
- Window #4: `22:55Z` through `00:10Z`, archive SHA `bed603828a997570149f01d42e7a979d96eb6ff0247c68f045b7e65bbe2c0477`, 40 MTF-passing runs, zero signals.

The original cross-window zero-signal result is not valid evidence that natural tradable setups were absent, because the rejection-funnel audit exposed a scoring contract bug that forced a hard reject for all directional candidates.

## Root-cause audit and PR #33

The pre-fix Window #4 rejection funnel produced:

- replay cutoffs: `600`;
- candidate decisions: `7596`;
- side: `NO_TRADE` for all `7596`;
- grade: `C` for all `7596`;
- `HTF_CONTEXT_MISMATCH`: `7596/7596` = 100%;
- `PRIMARY_LEVEL_NOT_STRONG`: `4903`;
- `RR_BELOW_3`: `3618`;
- `ATR_USED_OVER_80`: `2605`;
- `INVALID_GEOMETRY`: `1312`.

Root cause:

- setup/trap side vocabulary: `LONG` / `SHORT`;
- canonical MTF regime vocabulary: `BULLISH` / `BEARISH` / `RANGE` / `MIXED`;
- scoring compared regime and side directly, making `BULLISH != LONG` and `BEARISH != SHORT` a deterministic false mismatch.

PR #33 introduced the explicit side-to-regime mapping:

- `LONG -> BULLISH`;
- `SHORT -> BEARISH`.

The same PR also corrected `context_strength()` fallback semantics so 4h+1h alignment cannot be marked STRONG when D1 is directionally opposite; lower-timeframe fallback is allowed only when D1 is non-directional, matching canonical MTF classification semantics.

## Corrected Window #4 replay

The corrected replay used the exact deployed PR #33 engine and canonical context selection semantics:

- newest snapshot at or before each cutoff;
- `max_context_age_seconds=300` unchanged;
- 16 selected snapshots;
- context ages approximately 259–260 seconds;
- strict symbol intersection: `45`;
- MTF passed: `40`;
- MTF rejected: `5`;
- replay analyzed cutoffs: `600`;
- skipped insufficient-history replay cutoffs: `0`;
- skipped missing-context replay cutoffs: `0`;
- total candidate decisions: `7596`.

The five deep-history rejects remained:

- `CFGUSDT`: 176/300 daily bars;
- `MARSCOINUSDT`: 7/300;
- `PIEVERSEUSDT`: 298/300;
- `PONSUSDT`: 2/300;
- `牛来USDT`: 9/300.

Post-fix aggregate outcome:

- `HTF_CONTEXT_MISMATCH`: `7161/7596`;
- HTF-aligned candidates: `435`;
- `PRIMARY_LEVEL_NOT_STRONG`: `4903` total across all candidate decisions;
- `RR_BELOW_3`: `3618` total;
- `ATR_USED_OVER_80`: `2605` total;
- `INVALID_GEOMETRY`: `1312` total;
- tradable decisions: `0`;
- unique tradable signals: `0`.

This validates that PR #33 removed the guaranteed 100% directional mismatch: exactly `435` candidates now pass the HTF direction contract.

## Conditional audit of the 435 HTF-aligned candidates

The follow-up read-only conditional audit reproduced the expected reference count exactly:

- `htf_aligned_candidates = 435`;
- `reference_aligned_candidates = 435`;
- `reference_match = true`;
- all 435 were `LONG -> BULLISH`;
- no `SHORT -> BEARISH` sample occurred in Window #4;
- all 435 remained `NO_TRADE` / grade `C` because at least one hard reject remained.

Independent hard-reason counts within the aligned subset:

- `PRIMARY_LEVEL_NOT_STRONG`: `233`;
- `RR_BELOW_3`: `271`;
- `INVALID_GEOMETRY`: `87`;
- `ATR_USED_OVER_80`: `68`.

Reason combinations:

- `RR_BELOW_3` only: `142`;
- `PRIMARY_LEVEL_NOT_STRONG | RR_BELOW_3`: `129`;
- `PRIMARY_LEVEL_NOT_STRONG` only: `9`;
- `INVALID_GEOMETRY` only: `34`;
- `INVALID_GEOMETRY | PRIMARY_LEVEL_NOT_STRONG`: `53`;
- `ATR_USED_OVER_80` only: `26`;
- `ATR_USED_OVER_80 | PRIMARY_LEVEL_NOT_STRONG`: `42`.

Sequential conditional funnel:

```text
435 HTF aligned
  -> 202 after PRIMARY_LEVEL_NOT_STRONG
  -> 168 after geometry
  -> 142 after ATR_USED_OVER_80
  ->   0 after RR_BELOW_3
```

Therefore all `142` candidates that passed HTF direction, primary-level strength, geometry and ATR were rejected only by `RR_BELOW_3`.

There were no unexpected hard reasons.

## High-score near misses

The aligned subset includes high raw-score setups that are capped to grade C / setup score <=69 only because of hard rejects. Examples include:

- `WLDUSDT`, raw score `90`, STRONG level/context, only `RR_BELOW_3`, RR `0.225`;
- `WLDUSDT`, raw score `88`, only `INVALID_GEOMETRY` on later cutoffs;
- `NEARUSDT`, raw score `83`, only `RR_BELOW_3`, RR about `1.3889`.

These examples do not justify lowering the RR threshold. They justify auditing how entry/stop/structural-target geometry produces the observed RR values.

## Current interpretation

Validated conclusions:

1. PR #33 fixed a real side/regime contract defect and is historically replay-validated.
2. Window #4 still contains no natural tradable signal under the unchanged production rules.
3. The terminal blocker for the `142` otherwise surviving candidates is `RR_BELOW_3`.
4. The aggregate zero-signal results from pre-fix Windows #1–#3 must not be treated as canonical evidence of natural signal absence until those windows are rerun with the corrected engine.
5. No threshold, freshness, catalogue, probability or materialization rule was relaxed.

## Next gate

The next Phase 11G task is a read-only RR-geometry audit of the `142` RR-only candidates.

Required audit dimensions:

- entry;
- stop;
- structural target;
- risk distance;
- reward distance;
- calculated RR;
- target level ID/type/timeframe;
- candidate/setup identity and repeated observations across neighboring cutoffs;
- RR distribution after deduplicating unchanged setup geometry.

The purpose is to distinguish a genuinely unfavorable market window from a target-selection or geometry-construction bias before any rule change is considered.

Do not lower the `RR >= 3` gate merely to manufacture signals.

After geometry is understood, rerun corrected historical discovery across Windows #1–#4. Materialize and catalogue only naturally useful, coherent chains after deterministic replay/outcome inspection.

Phase 12 multi-provider expansion remains future work and is not active.
