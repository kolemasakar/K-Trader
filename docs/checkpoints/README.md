# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-13_POST_PAUSE_RESUME.md`

Current accepted state:

- technical pause window `2026-09-12T06:00:00Z -> 2026-09-13T06:00:00Z` has ended;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- fresh post-pause `/health` at ~`2026-09-13T06:12:54Z` is `ok`, `read_only`, `data_ready=true`, provider `binance_usdm`;
- VM uptime spans the pause with no reboot;
- strict freeze integrity failed because unattended-upgrade changed host Python 3.12 and libc6 at ~`2026-09-12T06:04Z`;
- no K-Trader deployment SHA changed during the pause;
- pause-watch automation does not provide a complete hourly evidence chain through the full 24h window;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- holdout remains untouched and unauthorized;
- latest accepted prospective snapshot remains `2026-09-12T04:45:00Z` pending authorized post-pause catch-up;
- accepted prospective state: 7 snapshots / 31 events / 6 eligible observations / 4 families / 2 resolved STOP / 2 unresolved;
- evidence remains `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`;
- full 24h pause remains inside the runner's ~100h M15 catch-up horizon;
- first resumed operation is P0 post-pause catch-up + deterministic resolver + continuity audit;
- canonical `main` is now `4919fea4397d34898ddc7d4215ea898e6caea815` after PR #57 squash merge;
- approved System Instructions v1.3 and Knowledge Priority are canonical on `main`;
- research history must be preserved when synchronizing the one new canonical main commit;
- Phase 11G remains active;
- Phase 12 remains FUTURE / NOT ACTIVE.

## New-chat bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

Recovery instruction:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md">>`

## Recent research checkpoints

- `2026-09-13_POST_PAUSE_RESUME.md` — post-pause production audit, host APT drift, evidence/catch-up boundary and resume gate;
- `2026-09-12_PRE_FREEZE_FINAL_CHECK.md` — final pre-freeze verification and authorization/freeze-integrity blockers;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics/resolver, FAST/SWING baseline execution, POSITION W1 contract;
- `2026-09-12_V2_2_FIRST_PROSPECTIVE_FAMILIES_AND_PROFILE_DATASET.md` — first non-empty prospective families, adaptive dataset and funding completeness;
- `2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md` — Level/VSA/execution/portfolio/robustness diagnostics and prospective infrastructure;
- `2026-09-11_V2_2_FIRST_PROSPECTIVE_SHADOW_CAPTURE.md` — first prospective shadow capture;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state;
- `2026-09-11_STRATEGY_SYNTHESIS_V2_1.md` — v2.1 synthesis;
- `2026-09-11_STRATEGY_BENCHMARK_V1_DISCOVERY_GATE.md` — benchmark discovery gate;
- `2026-09-11_PHASE11G_STRATEGY_RESEARCH_HANDOFF.md` — Phase 11G strategy-research handoff;
- `2026-09-11_PHASE11G_SURVIVORSHIP_AND_PRE_FREEZE_ACCEPTANCE.md` — survivorship/pre-freeze acceptance;
- `2026-09-11_PHASE11G_PRE_PAUSE_DEPLOYMENT_AND_24H_OBSERVATION.md` — pre-pause production baseline;
- `2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` — horizon time-split validation;
- `2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md` — canonical FAST TTL60 gate;
- `2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md` — RR geometry/corrected replay checkpoint;
- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` — accepted two-chain dataset state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- profile/prospective report: `../research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`;
- strategy benchmark protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
