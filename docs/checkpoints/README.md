# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-11_PHASE11G_PRE_PAUSE_DEPLOYMENT_AND_24H_OBSERVATION.md`

Current accepted state at this checkpoint:

- PR #51 single-writer hardening is squash-merged and deployed;
- accepted runtime/deployed SHA is `b698f8744f631a1a704d40cc3b2b66cfd31a6199`;
- PR-head CI #182 (`34621302939`) and post-merge CI #183 (`34621739596`) succeeded across Python 3.12/3.14, amd64, arm64 and `canonical-merge-gate`;
- approved production deployment run `34622156136` succeeded through the canonical rollback-capable `scripts/deploy.sh` path;
- container health is `status=ok`, `mode=read_only`, `data_ready=true`;
- deployed single-writer smoke: concurrent second writer blocked PASS; lock reuse after owner exit PASS;
- universe capture continuity was preserved across deployment with no `>300s` context gap;
- FAST/M5 TTL60 remains the only production-active lifecycle profile;
- provider-recorded Binance USD-M capture remains active;
- latest incremental prospective control covered `93` M5 cutoffs / `1860` slots / `17946` decisions with zero analysis errors and zero tradable signals;
- cumulative non-overlap prospective evidence is `419` cutoffs / `8380` slots / `85768` decisions;
- cumulative hard-gate funnel: `2167 -> 671 -> 480 -> 229 -> 20 -> 0 -> 0 -> 0` for HTF -> strong level -> geometry -> ATR -> TTL60 -> RR>=3 -> A/A+ -> tradable;
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
- dataset catalogue contract: `../DATASET_CATALOGUE_SPEC.md`;
- historical replay contract: `../HISTORICAL_REPLAY_SPEC.md`;
- current project state: `../CURRENT_STATE.md`;
- deployment specification: `../DEPLOYMENT.md`;
- Phase 10 acceptance: `../PHASE_10_PRODUCT_ACCEPTANCE.md`;
- roadmap: `../../ROADMAP.md`;
- project overview: `../../README.md`;
- GPT Builder acceptance checklist: `../../custom_gpt/BUILDER_CHECKLIST.md`.

A checkpoint does not replace those specifications. It records which accepted versions/state should be used when work resumes.
