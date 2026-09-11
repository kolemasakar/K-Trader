# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_DEPLOYMENT.md`

Current accepted state at this checkpoint:

- accepted runtime/deployed SHA is now `a73ba261a3ca97d2df3deac20b1459b7b4c38fff`; approved GitHub Actions deployment run `34612617730` succeeded;
- `Deploy Production #11`: SUCCESS;
- K-Trader container healthy; provider REST/WebSocket, MTF API and public Phase 10 Action acceptance PASS;
- FAST/M5 TTL60 remains the only production-active lifecycle profile;
- provider-recorded Binance USD-M capture remains active;
- PR #45 D1 retry backoff remains production-verified;
- PR #46 recent-MTF gap heal remains production-verified;
- scanner remains usable with expected young-contract D1 ineligibility and no live signal in the accepted observation;
- the 2026-09-10→11 causal prospective control analyzed `5448` valid symbol-cutoffs and `67822` decisions from `326` causal M5 cutoffs;
- 24h sequential funnel: `1522 -> 431 -> 311 -> 189 -> 10 -> 0 -> 0 -> 0` for HTF -> strong level -> geometry -> ATR -> TTL60 -> RR>=3 -> A/A+ -> tradable;
- no new catalogue chain or binary outcome sample was materialized;
- canonical catalogue remains SUIUSDT + XRPUSDT;
- Phase 11G prospective-control methodology is now repository-owned with explicit UTC-midnight error handling, deterministic sharding, checkpoint/resume and deterministic merge;
- exact `300s` context age remains valid and `>300s` is stale;
- missing selected-symbol history does not promote a lower-ranked replacement;
- focused prospective-control regression is present and repository-wide CI remains the merge authority;
- INTRADAY/M15 remains unresolved research-only; MEDIUM/H1 8-12h remains a research-only lifecycle design band;
- Phase 12 remains FUTURE / NOT ACTIVE;
- no RR, ATR, TTL, structural-target, HTF, strength, freshness, history, catalogue or probability rule is relaxed.

Historical checkpoints include:

- `2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_HARDENING.md` — canonical prospective-control tooling hardening before production activation;
- `2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md` — 24h control, D1 backoff and recent-MTF production hardening;
- `2026-09-10_PHASE11G_MONITORING_AND_READINESS_CHECKPOINT.md` — pre-24h accumulation/readiness state;
- `2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` — horizon time-split validation;
- `2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md` — FAST production rollout + corrected W1-W4 closure;
- `2026-09-09_PHASE11G_HORIZON_PROFILE_LIFECYCLE_STUDY.md` — first horizon lifecycle sensitivity study;
- `2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md` — canonical FAST TTL60 gate;
- `2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md` — RR geometry/corrected replay checkpoint;
- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` — accepted two-chain catalogue state.

## Related canonical documents

- Phase 11G current boundary: `../PHASE_11G_CHECKPOINT.md`;
- prospective-control contract: `../PROSPECTIVE_CONTROL_SPEC.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- deployment specification: `../DEPLOYMENT.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.