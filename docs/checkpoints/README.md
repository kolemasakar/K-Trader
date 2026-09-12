# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md`

Current accepted research state:

- accepted production application SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- production remains healthy/read-only; research has not changed deployment, risk, execution or trading semantics;
- frozen candidate remains `candidate_rule_set_v2_2`;
- frozen harness SHA256 remains `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- frozen prospective boundary remains `2026-09-11T20:00:00Z`;
- holdout remains untouched and unauthorized;
- latest valid frozen shadow snapshot is `2026-09-12T02:00:00Z`;
- ledger currently has 4 eligible observations / 3 unique families / 0 resolved primary families;
- family evidence accounting is preregistered: earliest eligible observation is the immutable primary representative;
- deterministic prospective outcome resolver is active and passed STOP-first/TIME_EXIT synthetic self-tests;
- prospective Level Context v2 currently disagrees with frozen open-space classification on 2/3 primary families, observation-only;
- FAST v0 baseline is clearly negative on development, validation and stress;
- SWING v0 is near breakeven under base assumptions but negative on validation and stress;
- research-only POSITION W1 contract is built and temporal-integrity audit passes on 19/19 symbols, 47–70 W1 bars;
- no post-hoc subgroup or feature has been promoted into frozen v2.2;
- next hard evidence milestone remains `>=30 unique resolved prospective frozen-v2.2 setup families`;
- planned technical development freeze remains `2026-09-12 09:00 Kyiv` -> `2026-09-13 09:00 Kyiv` (`06:00Z` -> `06:00Z`); production read-only capture/monitoring may continue while code/config/deploy changes and heavy production-host replay remain frozen except emergency recovery;
- Phase 11G remains active;
- Phase 12 remains FUTURE / NOT ACTIVE.

## Recent research checkpoints

- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics/resolver, FAST/SWING baseline execution, POSITION W1 contract and latest prospective state;
- `2026-09-12_V2_2_FIRST_PROSPECTIVE_FAMILIES_AND_PROFILE_DATASET.md` — first non-empty frozen prospective snapshot, adaptive profile dataset and funding completeness;
- `2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md` — Level/VSA/execution/portfolio/robustness diagnostics and prospective-infrastructure hardening;
- `2026-09-11_V2_2_FIRST_PROSPECTIVE_SHADOW_CAPTURE.md` — initial prospective shadow capture state;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state;
- `2026-09-11_STRATEGY_SYNTHESIS_V2_1.md` — v2.1 synthesis;
- `2026-09-11_STRATEGY_BENCHMARK_V1_DISCOVERY_GATE.md` — first benchmark discovery gate;
- `2026-09-11_PHASE11G_STRATEGY_RESEARCH_HANDOFF.md` — Phase 11G handoff into independent strategy research;
- `2026-09-11_PHASE11G_SURVIVORSHIP_AND_PRE_FREEZE_ACCEPTANCE.md` — survivorship diagnostic deployment and pre-freeze acceptance;
- `2026-09-11_PHASE11G_PRE_PAUSE_DEPLOYMENT_AND_24H_OBSERVATION.md` — pre-freeze baseline after single-writer deployment;
- `2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_DEPLOYMENT.md` — canonical prospective-control production activation before single-writer hardening;
- `2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_HARDENING.md` — canonical prospective-control tooling hardening before production activation;
- `2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md` — 24h control, D1 backoff and recent-MTF production hardening;
- `2026-09-10_PHASE11G_MONITORING_AND_READINESS_CHECKPOINT.md` — pre-24h accumulation/readiness state;
- `2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` — horizon time-split validation;
- `2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md` — FAST production rollout + corrected W1-W4 closure;
- `2026-09-09_PHASE11G_HORIZON_PROFILE_LIFECYCLE_STUDY.md` — first horizon lifecycle sensitivity study;
- `2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md` — canonical FAST TTL60 gate;
- `2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md` — RR geometry/corrected replay checkpoint;
- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` — accepted two-chain catalogue state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- latest profile/prospective report: `../research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`;
- family outcome semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- FAST/SWING baseline preregistration: `../research/PROFILE_BASELINES_FAST_SWING_V0_PREREG.md`;
- POSITION W1 contract: `../research/POSITION_W1_DATA_CONTRACT_V0.md`;
- earlier parallel research: `../research/PARALLEL_RESEARCH_RESULTS_2026-09-11.md`;
- strategy benchmark protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- deployment specification: `../DEPLOYMENT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
