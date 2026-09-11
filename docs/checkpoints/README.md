# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-11_PHASE11G_STRATEGY_RESEARCH_HANDOFF.md`

Current accepted state at this checkpoint:

- accepted production application SHA is `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- canonical repository `main` immediately before this handoff documentation is `35cdbdd81882064ebd59c6b49fe7f2ff95aa2b21`;
- production is healthy, read-only and continues provider-recorded `binance_usdm` universe capture;
- PR #51 single-writer hardening remains production-accepted;
- PR #53 unique-primary-level survivorship diagnostic remains production-accepted;
- cumulative non-overlap prospective evidence is `438` cutoffs / `8760` slots / `90621` decisions / `0` tradable records;
- cumulative hard-gate funnel is `2374 -> 740 -> 527 -> 229 -> 20 -> 0 -> 0 -> 0` for HTF -> strong level -> geometry -> ATR -> TTL60 -> RR>=3 -> A/A+ -> tradable;
- recent two-window survivorship is `852 -> 309 -> 216 -> 40 -> 10 -> 0 -> 0 -> 0` by records but only `28 -> 12 -> 8 -> 4 -> 3 -> 0 -> 0 -> 0` by distinct `(canonical_symbol, primary_level_id)`;
- no production trading gate was changed before the research handoff;
- the current gate-redesign discussion is paused pending an independent simple-strategy benchmark study;
- canonical benchmark protocol is `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- new-chat bootstrap is `../handoffs/BOOTSTRAP_PACKAGE_2026-09-11_K_TRADER_STRATEGY_BENCHMARK_RESEARCH.md`;
- the benchmark will research simple reproducible strategies, backtest them on existing K-Trader historical data, filter for observed win rate `>60%` subject to expectancy/robustness checks, synthesize a simple candidate rule set, and re-test it on untouched data;
- no benchmark result is production-approved without a later explicit decision;
- planned technical development freeze remains `2026-09-12 09:00 Kyiv` -> `2026-09-13 09:00 Kyiv` (`06:00Z` -> `06:00Z`);
- during the freeze, production read-only capture/monitoring continues while code/config/deploy changes and heavy production-host replay remain frozen except emergency recovery;
- Phase 11G remains active;
- Phase 12 remains FUTURE / NOT ACTIVE.

Historical checkpoints include:

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

## Related canonical documents

- strategy benchmark research protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- strategy benchmark new-chat bootstrap: `../handoffs/BOOTSTRAP_PACKAGE_2026-09-11_K_TRADER_STRATEGY_BENCHMARK_RESEARCH.md`;
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
