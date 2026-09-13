# K-Trader Current State

Updated: 2026-09-13 post-pause P0 accepted + first continued prospective capture  
Research checkpoint: `docs/checkpoints/2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Fresh post-pause acceptance:

- container image `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- container `running / healthy`;
- localhost and public HTTPS `/health`: `status=ok`, `mode=read_only`, `data_ready=true`, provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- host system state `running`;
- no reboot-required marker.

The 24h technical pause was not a strict host freeze because unattended-upgrade changed host Python/libc shortly after the pause began. The deployed K-Trader SHA did not change, no host reboot occurred, and post-pause runtime acceptance is PASS.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed.

## P0 catch-up acceptance

Canonical P0 catch-up at `2026-09-13T06:30:00Z` passed:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- exact frozen harness hash verified;
- technical-pause M15 continuity `PASS 19/19`;
- every symbol had exactly `96/96` pause-window M15 bars, zero gaps and zero duplicates;
- deterministic resolver completed;
- post-host-drift runtime acceptance passed.

Canonical details and P0 hashes are frozen in:

`docs/checkpoints/2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md`

## Latest accepted prospective evidence

After P0, exact frozen-v2.2 accumulation continued with the next safe closed M15 cutoff:

`2026-09-13T06:45:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T064500Z`

Capture:

- cycle: `VALID_SHADOW_CAPTURE`;
- provider: `binance_usdm`;
- panel: `19/19`;
- signal bars evaluated: `2622`;
- deduplicated events: `101`;
- eligible observations: `13`;
- unique eligible families: `10`;
- valid snapshots: `9`;
- discovered snapshots: `10`;
- one previously known invalid infrastructure snapshot remains rejected;
- holdout: unopened.

Latest hashes:

- bundle set: `e98d9aa558e8946c0a2b77becb23b3ce99c84e04a1dc6cf3d21a550511345407`;
- bundle export summary: `36e53cb999048b2f504565930232da614160b93dd6092c98357a48590437f411`;
- shadow summary: `e0976e106d54dde4818f881d014e40df936621196a4f14fdbbe07f1d902f611d`;
- event file: `4b335f5974e69485113de112fe060dfc52b7e00b0e11a35cc5f72688501a5f45`;
- ledger event set: `86e67c90ec0a8f2cde17bcebe00865c3d7cbbaf8c9b80bdd7924de0a9ac7f652`;
- outcome summary: `39c72e48eb9921ca45326f6fed9f60cef7c10e9bee6168d24818037b7a3423f6`;
- Level Context observation: `87763530a30549db1060d9a93e14d4b46f9883a5fe5ba912a372bc65c78409fa`.

## Family outcomes

Primary evidence unit remains unique resolved `setup_family_id`.

Current state:

- unique families: `10`;
- resolved primary families: `9`;
- unresolved primary families: `1`;
- resolved wins/losses: `1 / 8`;
- resolved WR: `11.11%`;
- resolved expectancy: `-0.8807054663R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

The new unresolved family is:

- `e363704d...` — `VTHOUSDT LONG`, primary entry `2026-09-13T06:30:00Z`.

The current sample is still far below the preregistered evidence threshold and does not authorize v2.2 retuning or holdout opening.

## Observation-only diagnostics

Level Context v2 across 10 primary families:

- clean-break/no-revisit: `4`;
- frozen-v2.2 vs richer open-space disagreement: `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`.

Raw VSA parity across 10 primary signal bars:

- `NONE`: `9`;
- `OPPOSING`: `1`;
- `ALIGNED`: `0`;
- only observed raw event remains one opposing `BC` on RAYSOLUSDT.

Execution observation for the 9 resolved primary families remains:

- `7 STOP`, `2 TIME_EXIT`, `0 TARGET`;
- median realized result about `-1.0330R`;
- median combined observed fee/funding/slippage contribution about `0.0407R`.

All remain diagnostic only.

## Family evidence governance

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Next hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

## Retained profile research

FAST v0 remains a negative baseline and is not promotable.

SWING v0 remains near breakeven under base assumptions but negative in validation/stress and is not promotable.

POSITION W1 remains prototype/data-architecture only.

## Repository/governance

Canonical `main`:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Research ancestry synchronization is complete without history rewrite:

- merge commit: `ae27adb125800c27b5aa5a4d41b3e91219059168`;
- parents: previous research head + canonical `4919fea...`;
- merge commit content delta: `0`;
- compare state after merge: research `ahead 94 / behind 0`;
- no rebase and no force update were used.

Before the merge, all five files changed by canonical commit `4919fea...` were synchronized/verified, including approved System Instructions v1.3, Knowledge Priority, README, Action Guide and Builder Checklist.

Production remains deployed on `81b79...`; the canonical governance/documentation ancestry change does not require redeployment.

## Next work order

1. Continue exact frozen-v2.2 prospective accumulation and deterministic outcome resolution.
2. Resolve the current `VTHOUSDT LONG` family causally as new closed M15 data becomes available.
3. Continue observation-only Level Context / VSA / execution / portfolio diagnostics.
4. Keep accumulating toward `>=30` resolved prospective primary families.
5. Create a new strategy version only through preregistration when evidence supports it.

Phase 11G remains **ACTIVE**.

Phase 12 remains **FUTURE / NOT ACTIVE**.
