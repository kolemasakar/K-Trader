# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md`

Current accepted state at the checkpoint:

- FAST/M5 TTL60 is production-validated and remains the only production-active profile;
- corrected historical Windows #1-#4 are closed with zero tradable signals under unchanged hard gates;
- canonical catalogue remains two verified chains: SUIUSDT + XRPUSDT;
- INTRADAY/M15 universal TTL is unresolved after an eight-symbol time-separated validation;
- the earlier 4-6h M15 band is not approved as a universal production rule;
- MEDIUM/H1 8-12h is time-split validated as a lifecycle design band, research-only;
- no non-FAST profitability optimum is claimed because tradable/outcome evidence remains insufficient;
- no symbol/evidence/primary-level adaptive TTL table is approved;
- no RR, ATR, structural-target, freshness, catalogue or probability rule was relaxed.

Historical checkpoints include:

- `2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md` — FAST production rollout + corrected W1-W4 closure;
- `2026-09-09_PHASE11G_HORIZON_PROFILE_LIFECYCLE_STUDY.md` — first horizon lifecycle sensitivity study;
- `2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md` — canonical FAST TTL60 gate;
- `2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md` — RR geometry/corrected replay checkpoint;
- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` — accepted two-chain catalogue state.

## Related canonical documents

- Phase 11G checkpoint: `../PHASE_11G_CHECKPOINT.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- deployment state: `../DEPLOYMENT.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
