# K-Trader Current State

Updated: 2026-09-13 frozen-v2.2 prospective accumulation through `2026-09-13T07:45:00Z`  
Research checkpoint: `docs/checkpoints/2026-09-13_FROZEN_V2_2_CONTINUATION_0645Z.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest runtime check:

- container image `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- container `running / healthy`;
- `/health`: `status=ok`, `mode=read_only`, `data_ready=true`, provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- no production deploy/restart was performed during the latest research capture.

The previous 24h technical pause was not a strict host freeze because unattended-upgrade changed host Python/libc shortly after the pause began. The deployed K-Trader SHA did not change, no host reboot occurred, and post-pause runtime acceptance was PASS.

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

Exact frozen-v2.2 accumulation continued with safe closed M15 cutoff:

`2026-09-13T07:45:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T074500Z`

Capture:

- cycle: `VALID_SHADOW_CAPTURE`;
- provider: `binance_usdm`;
- panel: `19/19`;
- signal bars evaluated: `2698`;
- deduplicated events: `107`;
- eligible observations: `14`;
- unique eligible families: `10`;
- valid snapshots: `10`;
- discovered snapshots: `11`;
- raw duplicate event occurrences: `273`;
- one previously known invalid infrastructure snapshot remains rejected;
- holdout: unopened.

Latest hashes:

- bundle set: `b90009c1b78ef7f7a0a850846a4b19c1a49155e1e4b38b487f5eb04995ccf331`;
- bundle export summary: `daa9c7cbbf1cba49c44208d73e21572614d0a5e9c6b4d165c957419bb0e109e5`;
- shadow summary: `8494b8097197f042e8b4b90ef52c392317a02a6f233bebdc99c14cb89051f191`;
- event file: `0b99835f0f905812c9244c8d2bd0f1a29d93461707382e0f4d1f2d87d54538e6`;
- ledger event set: `4419fc7d00b29767c3aa0d3d7017f01f4b0862cb18419ca54ac4adaec15bcf33`;
- outcome summary: `ff5e9948e707eec3ef64238703662a2acb376229890b02898e22ed42d6b585e3`;
- family outcome set: `f138c05a5d1c5690a839a11e34fec90db1fe5b9b3803b8faddb71bb9d3d75814`;
- observation outcome set: `decb9b36427e124179f3d8c2ba777114a540f202cea7c3edc7008b46532a2e61`;
- Level Context observation: `f8840345aa311ab2fa9d7b084e40b9ef819ff2cc58f316bdf10293f5da943c51`.

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

The unresolved family remains:

- `e363704d...` — `VTHOUSDT LONG`, primary entry `2026-09-13T06:30:00Z`.

The family has accumulated a second correlated observation, but the immutable earliest eligible observation remains the primary representative. No additional independent family was created by the 07:45Z capture.

The current sample is still far below the preregistered evidence threshold and does not authorize v2.2 retuning or holdout opening.

## Observation-only diagnostics

Level Context v2 at the 07:45Z state across 10 primary families:

- clean-break/no-revisit: `4`;
- frozen-v2.2 vs richer open-space disagreement: `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`.

Raw VSA parity across 10 primary signal bars remains:

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
- canonical `main` is an ancestor of the research branch;
- no rebase and no force update were used.

Before the merge, all five files changed by canonical commit `4919fea...` were synchronized/verified, including approved System Instructions v1.3, Knowledge Priority, README, Action Guide and Builder Checklist.

Production remains deployed on `81b79...`; governance/documentation updates do not require redeployment.

## Next work order

1. Continue exact frozen-v2.2 prospective accumulation and deterministic outcome resolution.
2. Resolve the current `VTHOUSDT LONG` family causally as new closed M15 data becomes available.
3. Continue observation-only Level Context / VSA / execution / portfolio diagnostics without turning any of them into a gate.
4. Keep accumulating toward `>=30` resolved prospective primary families.
5. Prepare the 2026-09-14 pre-pause baseline before the planned 24h data-collection pause beginning 10:00 Europe/Kyiv; provide any required manual host actions at 07:00 Europe/Kyiv.
6. Create a new strategy version only through preregistration when evidence supports it.

Phase 11G remains **ACTIVE**.

Phase 12 remains **FUTURE / NOT ACTIVE**.
