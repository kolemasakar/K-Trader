# K-Trader Current State

Updated: 2026-09-09

Canonical operational checkpoint:

`docs/checkpoints/2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md`

Prior research checkpoint:

`docs/checkpoints/2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md`

Prior dataset checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`

## Current phase boundary

- Phase 10: COMPLETE / product accepted for the current single-provider read-only v1 scope;
- Phase 11A-11G repository-side foundation: VERIFIED;
- Phase 11F production accumulation: active and provider-coherent;
- Phase 11G physical catalogue: two canonical chains COMPLETE / VERIFIED / CATALOGUED;
- Phase 11G corrected discovery: ACTIVE;
- RR-geometry audit: COMPLETE / no geometry defect found;
- Setup Lifecycle / Expiry gate: REPOSITORY + REPLAY VALIDATED;
- approved canonical setup TTL: `60 minutes = 12 x M5 bars`;
- production deployment of the TTL implementation: PENDING;
- Phase 12 multi-provider expansion: FUTURE / NOT ACTIVE.

## Repository and production identity

Canonical repository baseline after PR #36:

- canonical `main` SHA: `1dbc41d8521daab42b3edb7ef10d3ccfdb8b68bf`;
- PR #36: `Phase 11G: enforce 60m setup expiry`;
- Tests workflow #67: PASS;
- CI workflow #138: PASS;
- CI pytest: PASS;
- CI Docker amd64: PASS;
- CI Docker arm64: PASS.

Production has not yet been rolled forward to PR #36:

- deployed implementation image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- production container: healthy at the last accepted runtime validation;
- PR #36 production rollout is a separate subsequent operational task;
- GitHub `main` + PR/CI/deploy remains canonical; no direct source mutation on PROD is permitted.

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

## Current interpretation

The RR-geometry question and the setup-lifecycle gap are now understood separately:

- RR geometry is behaving as designed under the structural-target contract;
- the missing setup TTL was a lifecycle/specification gap;
- TTL 60m removes systematic reuse of old confirmed setups without manufacturing signals;
- no change to RR, stop, target, freshness, probability or catalogue standards is justified by this work.

## Next action

The Setup Lifecycle / Expiry gate is closed at repository/specification/replay level.

Next Phase 11G sequence:

1. deploy canonical `main` through the standard production deployment workflow when rollout is authorized;
2. verify production health and runtime TTL configuration after deployment;
3. rerun corrected discovery for Windows #1-#4 under the explicit 60m lifecycle;
4. preserve exact provenance for every replay and do not force reconstructed runs to match superseded historical populations;
5. materialize/register only naturally useful deterministic chains that survive every unchanged hard gate.
