# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_PROSPECTIVE_1415Z_CONTINUITY.md`

Current accepted state:

- Phase 11G remains **ACTIVE**; Phase 12 remains **FUTURE / NOT ACTIVE**;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- production health remains `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA remains `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- holdout remains untouched and unauthorized;
- latest accepted cutoff is `2026-09-16T14:15:00Z`;
- ledger is `60` eligible observations / `46` unique primary families;
- outcome state is `39` resolved / `7` unresolved primary families, `9/30` wins/losses, expectancy `-0.6482720085510278R`;
- resolver v1.3 continuity parity remains **PASS**, `50/50` prior resolved observations with `0` terminal/economic mismatches;
- post-prereg confirmation boundary remains `entry_time >= 2026-09-16T13:00:00Z`;
- confirmation sample currently contains `2` unresolved primary families: ADAUSDT SHORT and DOGEUSDT SHORT at `13:15Z`, both H1 REST rather than LOW;
- TRUMPUSDT primary entry is `12:30Z`, so later observations from that family do not count as post-prereg primary evidence;
- max concurrent SHORT exposure has increased to `7`, diagnostic only;
- no retuning, exit-management change, direction filter, holdout access or production mutation is authorized;
- broad adaptive strategy discovery remains delegated to `K_Investigation_Forecast` and must not be reopened inside K-Trader until the user reports positive results;
- disk-retention remains `DRY_RUN_ONLY`, timer disabled by design.

## Latest accepted research checkpoints

- `2026-09-16_PROSPECTIVE_1415Z_CONTINUITY.md` — authoritative 14:15Z capture, resolver-v1.3 continuity, prereg tracking and diagnostics;
- `2026-09-16_PROSPECTIVE_1345Z_RESOLVER_V1_3.md` — resolver-v1.3 acceptance;
- `2026-09-16_PREREG_PATH_PIPELINE_HARDENING.md` — preregistration, path-quality analysis and orchestration hardening;
- `2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md` — parallel diagnostics and provenance/hardening;
- `2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md` — prior resolver-v1.2 acceptance;
- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — post-soak catch-up and retention validation;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — initial 30–49-family diagnostic baseline.

## Related documents

- current state: `../CURRENT_STATE.md`;
- resolver v1.3: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- hypothesis preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- fail-closed research orchestration: `../../research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`;
- path-quality diagnostics: `../../research/strategy_benchmark_v1/prospective_path_quality_diagnostics.py`;
- disk policy: `../operations/DISK_RETENTION_POLICY.md`;
- causal historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
