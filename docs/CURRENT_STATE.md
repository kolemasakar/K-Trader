# K-Trader Current State

Updated: 2026-09-09

Canonical operational checkpoint:

`docs/checkpoints/2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md`

Prior research checkpoint:

`docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

Prior dataset checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`

## Current phase boundary

- Phase 10: COMPLETE / product accepted for the current single-provider read-only v1 scope;
- Phase 11A-11G repository-side foundation: VERIFIED;
- Phase 11F production accumulation: active and provider-coherent;
- Phase 11G physical catalogue: two canonical chains COMPLETE / VERIFIED / CATALOGUED;
- Phase 11G corrected historical Windows #1-#4 under FAST TTL60: COMPLETE / zero tradable signals;
- Phase 11G prospective/provider-recorded discovery: ACTIVE;
- RR-geometry audit: COMPLETE / no geometry defect found;
- Setup Lifecycle / Expiry gate: REPOSITORY + REPLAY + PRODUCTION VALIDATED;
- approved canonical FAST setup TTL: `60 minutes = 12 x M5 bars`;
- production deployment of the TTL implementation: COMPLETE / accepted on canonical `main`;
- Phase 12 multi-provider expansion: FUTURE / NOT ACTIVE.

## Repository and production identity

Current accepted production baseline:

- canonical/deployed `main` SHA: `9a257957e033f6265b9e746cb9f15e755ff87b72`;
- deployed image: `k-trader:9a257957e033f6265b9e746cb9f15e755ff87b72`;
- GitHub `Deploy Production #10`: SUCCESS;
- production container: healthy;
- provider REST/WebSocket acceptance: PASS;
- MTF API acceptance: PASS;
- public HTTPS / Phase 10 Action acceptance: PASS;
- live FAST lifecycle: `setup_interval=5m`, `setup_max_age_bars=12`, `setup_max_age_seconds=3600`;
- exact 60m age remains valid; 60m+1s is `SETUP_EXPIRED`;
- GitHub `main` + PR/CI/deploy remains canonical; no direct source mutation on PROD is permitted.

The current `main` also contains the horizon-aware research foundation. M15/H1 lifecycle profiles remain research-only; production defaults remain FAST/M5 unless a later explicit activation gate changes that contract.

## Direct production operator access

A policy-constrained SentinelX management channel from ChatGPT to the production VM is accepted and operational.

- host: `k-trader-prod-vnic`;
- platform: Oracle Cloud / Ubuntu 24.04 / ARM64;
- SentinelX agent acceptance version: `0.11.18`;
- purpose: direct production diagnostics and controlled maintenance without requiring the operator to relay every SSH command;
- approved operations include allowlisted command execution, selected file/log inspection, Docker/K-Trader diagnostics, controlled container exec and selected service inspection/restart;
- SSH remains the out-of-band bootstrap/recovery path;
- unrestricted `NOPASSWD: ALL` is prohibited;
- arbitrary root execution is denied;
- structured filesystem access is read-only and currently exposes only `/opt/k-trader/releases` and `/opt/k-trader/data`.

Canonical details: `docs/SENTINELX_REMOTE_ACCESS.md`.

## Strict Phase 11G policy

Unchanged controls:

- provider: `binance_usdm` for the current production research scope;
- `max_context_age_seconds=300`;
- historical context uses the newest recorded snapshot at or before each replay cutoff;
- no historical rank/context fabrication;
- no freshness widening to manufacture eligible history;
- canonical research MTF depths: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- full-engine replay before any materialization decision;
- structural target only; no synthetic 3R target;
- `RR >= 3` remains a hard gate;
- ATR-used threshold remains unchanged;
- outcome samples only from actual binary WIN/LOSS outcomes;
- no synthetic outcomes;
- no probability calibration;
- `estimated_probability` remains null/N/A;
- no Phase 12 expansion while current Phase 11G discovery remains active.

## Setup lifecycle contract

`docs/SETUP_SPEC.md` is now v1.1.

Canonical lifecycle:

- setup interval: `5m`;
- `setup_max_age_bars = 12`;
- `setup_age = evaluation_time - canonical_confirmation_time`;
- canonical confirmation time is the latest confirmed evidence bar that activates the selected setup;
- exactly `60 minutes` old remains valid;
- `setup_age > 60 minutes` -> hard reject `SETUP_EXPIRED`;
- fresh market candles do not refresh an old confirmed setup;
- Trap/VSA evidence-local confirmation windows are unchanged;
- stop, structural target and RR calculation are unchanged.

The lifecycle policy is enforced in the same canonical analyzer used by live analysis and historical replay.

## Current dataset catalogue

Canonical persisted dataset state remains two chains:

- path: `/data/research/phase11g/catalogue.json`;
- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- no new chain was materialized during the RR/lifecycle investigations.

The earlier checkpoint recorded catalogue SHA:

`057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`

A later runtime verification found the currently materialized catalogue file SHA as:

`d1b1c42b51a2f54c865d03e21bae3faa2a0e58166baa46c7a01a241b47eed250`

while canonical loader verification with `verify_artifacts=True` still passed. This SHA drift is not yet fully explained and must not be represented as corruption without evidence.

### Entry 1 - SUIUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- unique tradable signals: `0`;
- outcome sample: `null`.

### Entry 2 - XRPUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z`;
- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`;
- bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`;
- study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- catalogue entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- unique tradable signals: `0`;
- outcome sample: `null`.

## Historical Window #4 reference checkpoint

The original corrected historical Window #4 checkpoint remains a historical audit record:

- strict symbols: `45`;
- MTF/history pass: `40`;
- MTF rejected: `5`;
- analyzed cutoffs: `600`;
- candidate decisions: `7596`;
- HTF aligned: `435`;
- sequential funnel: `435 -> 202 -> 168 -> 142 -> 0`;
- all 142 final survivors were rejected only by `RR_BELOW_3`.

Exact old Window #4 input artifacts are not persisted on the VM, so later reconstructions must be labelled separately rather than forced to reproduce this population exactly.

## Reconstructed Window #4 V2 baseline

Using the currently available recorded universe snapshots and deep history:

- logical cutoffs: `16`;
- selected snapshots: `16` unique;
- strict symbols: `47`;
- history pass: `43`;
- history failures: `4`;
- analyzed cutoffs: `645`;
- candidate decisions: `8874`;
- pre-expiry stage funnel: `8874 -> 454 -> 166 -> 133 -> 81 -> 0`;
- tradable decisions: `0`.

History failures:

- `MARSCOINUSDT`: 8/300;
- `PONSUSDT`: 3/300;
- `牛来USDT`: 10/300;
- `龙虾USDT`: 182/300.

The current V2 population differs from the old historical checkpoint. A roughly one-day pause between research sessions is a plausible source of archive/provider drift, but this has not been proven.

## RR geometry audit conclusion

The read-only RR geometry audit traced all `81/81` V2 RR-only decisions before public decision masking.

Results:

- real unique geometries: `21`;
- all were LONG;
- targets were real active structural resistance levels;
- no synthetic 3R target was observed;
- RR range was approximately `0.026` through `1.0`;
- no arithmetic RR defect was found;
- low RR was structurally explained by small available reward relative to stop risk.

Therefore the geometry implementation and `RR >= 3` threshold were not relaxed.

## Setup recency audit and policy study

RR-only setup age before expiry:

- minimum: `0m`;
- median: `545m`;
- maximum: `1295m`;
- older than 1h: `78/81`;
- older than 3h: `65/81`;
- older than 6h: `53/81`.

The approved expiry mode is canonical trigger age, not independent component age.

The 60m policy sensitivity study produced:

```text
470 -> 24 -> 5 -> 3 -> 3 -> 0
```

with three RR-only survivors, all `NEARUSDT`, and no `RR >= 3` trade.

## Control replay after PR #36

Read-only control job:

`job_d77dc7277002`

Result:

- status: succeeded;
- exit code: `0`;
- duration: `386.38s`;
- candidate decisions: `8874`;
- `SETUP_EXPIRED`: `6563`;
- exact RR-only after all hard reasons: `3`;
- unique RR-only geometry after expiry: `3`;
- all three: `NEARUSDT`;
- RR approximately `0.0851`, `0.1316`, `0.1316`;
- RR pass: `0`;
- tradable decisions: `0`.

The old stage counters still show `81` before expiry because those helper counters are evaluated before the new lifecycle reason is applied. The operational post-expiry result is the exact RR-only population of `3`.

## Production TTL rollout and corrected Windows #1-#4 closure

Canonical checkpoint: `docs/checkpoints/2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md`.

The accepted production rollout and historical rerun produced:

- deployed SHA/image: `9a257957e033f6265b9e746cb9f15e755ff87b72`;
- corrected W1-W4 analyzed cutoffs: `2445`;
- candidate decisions: `29508`;
- `SETUP_EXPIRED` reason occurrences: `23952`;
- HTF-aligned decisions: `1987`;
- strong primary-level stage: `944`;
- tradable decisions: `0`;
- skipped selected context after strict selection: `0`;
- skipped replay history after symbol-level qualification: `0`;
- W4 reproduced the historical high-level population exactly: `45` strict symbols, `40` history pass, `600` analyzed cutoffs, `7596` decisions, `435` HTF aligned, `202` strong-level stage.
- corrected W4 conditional funnel: `435 -> 202 -> 168 -> 142 -> 0 -> 0` for HTF -> strong -> geometry -> ATR -> TTL60 -> RR>=3; the first four stages exactly reproduce the historical pre-TTL audit.

The `SETUP_EXPIRED` count overlaps other rejection reasons and is not a disjoint funnel stage. Public `TradingDecision` masks entry/stop/target for `NO_TRADE`, so conditional geometry audits must not infer geometry absence from those masked fields.

No new dataset chain was materialized. Catalogue remains SUIUSDT + XRPUSDT.

## Current interpretation

- RR geometry is behaving as designed under the structural-target contract;
- the setup-lifecycle gap is closed for the FAST/M5 production profile;
- TTL60 removes systematic reuse of old confirmed setups without manufacturing signals;
- corrected W1-W4 yielded zero natural tradable signals under unchanged hard gates;
- no change to RR, stop, target, freshness, probability or catalogue standards is justified by this work.

## Next action

1. keep provider-recorded production research capture active;
2. materialize/register a new Phase 11G chain only when a naturally useful deterministic setup survives every unchanged hard gate;
3. continue INTRADAY/M15 and MEDIUM/H1 lifecycle work as research profiles only, with an explicit replay/activation gate before any production use;
4. keep probability calibration inactive until sufficient real binary outcomes and a separately approved out-of-sample methodology exist;
5. keep Phase 12 multi-provider expansion inactive until the current Phase 11G research boundary is explicitly closed.