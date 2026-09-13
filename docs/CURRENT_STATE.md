# K-Trader Current State

Updated: 2026-09-13 post-pause P0 catch-up accepted  
Research checkpoint: `docs/checkpoints/2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Fresh P0 acceptance:

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

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed during P0.

## Latest accepted prospective evidence

Canonical post-pause catch-up cutoff:

`2026-09-13T06:30:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T063000Z`

Capture:

- cycle: `VALID_SHADOW_CAPTURE`;
- panel: `19/19`;
- signal bars evaluated: `2603`;
- deduplicated events: `96`;
- eligible observations: `12`;
- unique eligible families: `9`;
- frozen harness hash: exact match;
- holdout: unopened.

Accepted hashes:

- bundle set: `646752f07e1567aefde0246d35bd61011758dff272156edc2f59da68a2e70376`;
- bundle export summary: `ccce2649dc42248db8cc4839d2b792401bd3032738dcfc859ce7569f8920fb11`;
- shadow summary: `fa1ece1af5b1e85ac123e92828de3990cc8f5c07b16d0b250290ebf7d8857528`;
- event file: `c611d4721443e4f53bd5b29b9be0c3f19e4ef9c8cd543bb2b519e7f3c4b2168b`;
- ledger event set: `60aac34c860d06f0d291d73714c31a741293ced74d0d41e5e6b957fe0a8b9b92`;
- outcome summary: `5f1d550ed439aecda7aeae2dd9c5d8f386e1f555b6b42b11ca7cbe2415edf718`;
- Level Context observation: `ea30b0183ad2f8e0b4898f07c78d0f86e532f5646975b6042c8e65c0e12eaef7`.

## Family outcomes

Primary evidence unit remains unique resolved `setup_family_id`.

Current state:

- unique families: `9`;
- resolved primary families: `9`;
- unresolved: `0`;
- wins/losses: `1 / 8`;
- resolved WR: `11.11%`;
- resolved expectancy: `-0.8807054663R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

This is a small prospective sample and does not authorize any v2.2 retuning or holdout opening.

## Pause-window data continuity

For the exact technical-pause interval `2026-09-12T06:00:00Z -> 2026-09-13T06:00:00Z`:

- 19/19 symbols have exactly 96 M15 bars;
- gaps: `0`;
- duplicates: `0`;
- two additional closed M15 bars are present from pause end to the 06:30Z catch-up cutoff.

M15 continuity: **PASS 19/19**.

The pause-watch automation still did not provide a complete hourly monitoring chain; provider-recorded catch-up artifacts establish the accepted data continuity instead.

## Observation-only diagnostics

Level Context v2 across 9 primary families:

- clean-break/no-revisit: `4`;
- frozen-v2.2 vs richer open-space disagreement: `2`;
- richer obstacle inside `3R`: `5`;
- richer obstacle inside `1R`: `4`.

Raw VSA parity on the 9 primary signal bars:

- `NONE`: `8`;
- `OPPOSING`: `1`;
- `ALIGNED`: `0`;
- only observed raw event: one opposing `BC` on RAYSOLUSDT.

Execution observation for 9 resolved primaries:

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

Governance parity between `main` and the research branch was verified before ancestry synchronization:

- `SYSTEM_K_TRADER_v1_3_COMPACT.md` blob: `5969606306e93d5798a77d79f82a559e088c8529`;
- `00_KNOWLEDGE_PRIORITY.md` blob: `e52c5817cfbd3ee0907db2711884b742752a15e3`.

Preserve research history; synchronize canonical ancestry via merge/no-rewrite only.

Production remains deployed on `81b79...`; canonical governance/documentation commits do not require redeployment.

## Next work order

1. Complete research-branch ancestry synchronization with canonical `main` without rewriting research history.
2. Continue exact frozen-v2.2 prospective accumulation and deterministic outcome resolution.
3. Continue observation-only Level Context / VSA / execution / portfolio diagnostics.
4. Keep accumulating toward `>=30` resolved prospective primary families.
5. Create a new strategy version only through preregistration when evidence supports it.

Phase 11G remains **ACTIVE**.

Phase 12 remains **FUTURE / NOT ACTIVE**.
