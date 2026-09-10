# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-10_PHASE11G_MONITORING_AND_READINESS_CHECKPOINT.md`

Current accepted state at the checkpoint:

- canonical repository `main`: `1e6e20fb5d0e74aaf620f3aebf69429e0c0f3198`, GitHub-verified;
- accepted production runtime remains `9a257957e033f6265b9e746cb9f15e755ff87b72` because PR #43 was docs/research-only;
- FAST/M5 TTL60 remains the only production-active profile;
- provider-recorded Binance USD-M universe capture remains active;
- next prospective signal/discovery review is manual after approximately 24 hours; the temporary automated ChatGPT signal-watch task is disabled;
- no natural tradable LONG/SHORT signal has yet been accepted and no new catalogue chain has been materialized;
- SQLite integrity check is `ok`, completed backups are present, and storage headroom is healthy;
- canonical dataset catalogue verifies successfully with two entries: SUIUSDT + XRPUSDT;
- catalogue SHA identity question is closed: `catalogue_sha256` is the semantic digest of `{schema_version, entries}`, while the raw serialized `catalogue.json` file has a separate content SHA by design;
- operational audit found continuous ~5-minute capture with no >7-minute gap across the inspected cross-day interval;
- bootstrap failure volume is concentrated only in four young contracts with insufficient D1 history; eligibility remains fail-closed, while retry-frequency hardening is the next scanner operations task;
- parallel work proceeds through scanner retry/reconciliation hardening, deterministic discovery-report and outcome-readiness audits;
- INTRADAY/M15 universal TTL remains unresolved; MEDIUM/H1 8-12h remains a research-only time-split validated lifecycle band;
- no RR, ATR, structural-target, freshness, history, catalogue or probability rule is relaxed.

Historical checkpoints include:

- `2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` — horizon time-split validation;
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
