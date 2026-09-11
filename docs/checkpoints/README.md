# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-11_PHASE11G_SURVIVORSHIP_AND_PRE_FREEZE_ACCEPTANCE.md`

Current accepted state at this checkpoint:

- accepted runtime/deployed SHA is `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- PR #51 single-writer hardening remains production-accepted;
- PR #53 unique-primary-level survivorship diagnostic is squash-merged and deployed;
- PR #53 PR-head CI #186 (`34624965946`) and post-merge CI #187 (`34625353779`) succeeded across Python 3.12/3.14, amd64, arm64 and `canonical-merge-gate`;
- approved production deployment run `34625823230` succeeded through the canonical rollback-capable `scripts/deploy.sh` path;
- container health is `status=ok`, `mode=read_only`, `data_ready=true`;
- survivorship CLI is packaged and passed functional production acceptance on real Phase 11G shards;
- universe capture continuity was preserved across deployment with no `>300s` context gap;
- latest additional prospective window covered `19` M5 cutoffs / `380` slots / `4853` decisions with zero analysis errors and zero tradable signals;
- cumulative non-overlap prospective evidence is now `438` cutoffs / `8760` slots / `90621` decisions;
- cumulative hard-gate funnel: `2374 -> 740 -> 527 -> 229 -> 20 -> 0 -> 0 -> 0` for HTF -> strong level -> geometry -> ATR -> TTL60 -> RR>=3 -> A/A+ -> tradable;
- recent two-window survivorship is `852 -> 309 -> 216 -> 40 -> 10 -> 0 -> 0 -> 0` by records but only `28 -> 12 -> 8 -> 4 -> 3 -> 0 -> 0 -> 0` by distinct `(canonical_symbol, primary_level_id)`;
- canonical catalogue remains `SUIUSDT` + `XRPUSDT`, with no new natural chain/outcome sample;
- planned technical development freeze is `2026-09-12 09:00 Kyiv` -> `2026-09-13 09:00 Kyiv` (`06:00Z` -> `06:00Z`);
- during the freeze, production read-only capture/monitoring continues while code/config/deploy changes and heavy production-host replay are frozen except emergency recovery;
- the exact 24h observation replay target is `288` M5 cutoffs (`06:00Z` through `05:55Z`) and up to `5760` top-20 symbol slots before readiness accounting;
- exact `300s` context age remains valid and `>300s` is stale;
- missing selected-symbol history does not promote a lower-ranked replacement;
- INTRADAY/M15 remains unresolved research-only; MEDIUM/H1 remains research-only;
- Phase 12 remains FUTURE / NOT ACTIVE;
- no RR, ATR, TTL, structural-target, HTF, strength, freshness, history, catalogue or probability rule is relaxed.

Historical checkpoints include:

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

## Related canonical documents

- Phase 11G current boundary: `../PHASE_11G_CHECKPOINT.md`;
- prospective-control contract: `../PROSPECTIVE_CONTROL_SPEC.md`;
- survivorship diagnostic contract: `../PROSPECTIVE_SURVIVORSHIP_DIAGNOSTIC.md`;
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- deployment specification: `../DEPLOYMENT.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
