# K-Trader Current State

Updated: 2026-09-09

Canonical operational checkpoint:

`docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

Prior dataset checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`

Current phase boundary:

- Phase 10: COMPLETE / product accepted for the current single-provider read-only v1 scope;
- Phase 11A–11G repository-side foundation: VERIFIED;
- Phase 11F production accumulation: active and provider-coherent;
- Phase 11G physical catalogue: two canonical chains COMPLETE / VERIFIED / CATALOGUED;
- Phase 11G discovery: ACTIVE;
- current research gate: RR-geometry audit of 142 otherwise surviving Window #4 candidates;
- Phase 12 multi-provider expansion: future work, not active.

## Repository and production identity

Accepted code/runtime baseline before this documentation-only checkpoint:

- canonical `main` SHA: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- PR #33: `Fix Phase 11G side-to-regime scoring contract`;
- post-merge Tests run `34177001398`: PASS;
- post-merge CI run `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- Deploy Production #9 run `34177978988`: SUCCESS;
- deployed image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- production container: healthy;
- provider REST/WebSocket acceptance: PASS;
- MTF API acceptance: PASS;
- Phase 10 Action live acceptance: PASS.

Deploy acceptance observed scanner `status=DEGRADED`, `symbols_ready=18`, `symbols_failed=2`; this did not fail service health or deployment acceptance.

## Direct production operator access

A policy-constrained SentinelX management channel from ChatGPT to the production VM was accepted on 2026-09-09.

- host: `k-trader-prod-vnic`;
- platform: Oracle Cloud Ampere A1 / Ubuntu 24.04 / ARM64;
- SentinelX agent version at acceptance: `0.11.18`;
- purpose: direct production diagnostics and controlled maintenance without requiring the operator to relay every command through SSH;
- available operations include allowlisted command execution, one-off Bash/Python scripts, selected file/log inspection, Docker/K-Trader diagnostics, approved container exec, and selected service inspection/restart;
- SSH remains the out-of-band bootstrap/recovery path;
- SentinelX does not replace GitHub PR/CI/deploy controls.

The initial unrestricted `NOPASSWD: ALL` bootstrap sudo rule was removed and replaced with a narrow operational sudo policy. Arbitrary root execution is denied. Structured filesystem access is read-only, excludes sensitive SentinelX/GitHub-runner credential files, and currently exposes only `/opt/k-trader/releases` and `/opt/k-trader/data`. No writable filesystem subtree is exposed.

Canonical details and operating rules: `docs/SENTINELX_REMOTE_ACCESS.md`.

## Strict Phase 11G policy

Unchanged controls:

- provider: `binance_usdm` for the current production research scope;
- `max_context_age_seconds=300`;
- canonical context membership uses the newest snapshot at/before each replay cutoff;
- no historical rank/context fabrication;
- no freshness widening to manufacture eligible history;
- canonical MTF depths: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- full-engine replay before any materialization decision;
- outcome samples only from actual binary WIN/LOSS outcomes;
- no synthetic outcomes;
- no probability calibration;
- `estimated_probability` remains null/N/A;
- no Phase 12 expansion while the current Phase 11G gate is unresolved.

## Current dataset catalogue

- path: `/data/research/phase11g/catalogue.json`;
- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- final prior reload with `verify_artifacts=True`: PASS;
- no new entries were added during corrected discovery.

### Entry 1 — SUIUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- unique tradable signals: `0`;
- outcome sample: `null`.

### Entry 2 — XRPUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z`;
- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`;
- bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`;
- study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- provenance SHA: `6397ce7c1786d1ebb5d1e11f297995c3b3c68abb2a44476a29c994164bfcff65`;
- catalogue entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- unique tradable signals: `0`;
- outcome sample: `null`.

## Phase 11G discovery correction

The original Window #4 rejection funnel showed `7596/7596` candidates rejected with `HTF_CONTEXT_MISMATCH`. The defect was a vocabulary mismatch between setup sides (`LONG`/`SHORT`) and MTF regimes (`BULLISH`/`BEARISH`). PR #33 introduced the explicit mapping and aligned `context_strength()` D1 fallback semantics with canonical MTF classification.

Corrected Window #4 replay:

- window: `2026-09-07T22:55Z` through `2026-09-08T00:10Z`;
- archive SHA: `bed603828a997570149f01d42e7a979d96eb6ff0247c68f045b7e65bbe2c0477`;
- strict symbols: `45`;
- MTF passed: `40`;
- MTF rejected: `5`;
- analyzed cutoffs: `600`;
- total candidate decisions: `7596`;
- HTF rejected: `7161`;
- HTF aligned: `435`;
- tradable decisions: `0`;
- unique tradable signals: `0`.

The conditional audit reproduced `435` aligned candidates exactly and found all `435` were `LONG -> BULLISH`.

Sequential downstream funnel:

```text
435 HTF aligned
  -> 202 after primary-level strength
  -> 168 after geometry
  -> 142 after ATR <= 80%
  ->   0 after RR >= 3
```

All 142 final survivors were rejected only by `RR_BELOW_3`. No unexpected hard reasons were present.

## Current interpretation and next action

PR #33 is historically replay-validated. Window #4 still has no tradable setup under unchanged production rules, but the current terminal blocker is now localized to RR geometry rather than the fixed side/regime contract.

Do not lower the RR threshold based on this result. The next task is a read-only RR-geometry audit of the 142 RR-only candidates covering entry, stop, structural target, risk/reward distances, target identity/timeframe, RR distribution and deduplication of repeated unchanged setup geometry across neighboring cutoffs.

Pre-fix zero-signal results from Windows #1–#3 must not be treated as canonical evidence of natural signal absence until rerun with the corrected engine.

No dataset materialization or catalogue registration should occur before the geometry audit is understood and a useful natural candidate is confirmed deterministically.
