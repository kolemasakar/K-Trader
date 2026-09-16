# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_PREREG_PATH_PIPELINE_HARDENING.md`

Current accepted state:

- Phase 11G remains **ACTIVE**; Phase 12 remains **FUTURE / NOT ACTIVE**;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- production health remains `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA remains `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- holdout remains untouched and unauthorized;
- latest accepted prospective cutoff remains `2026-09-16T12:00:00Z`;
- ledger state is `56` eligible observations / `43` unique families;
- outcome state remains `39` resolved primary families / `4` unresolved, `9` wins / `30` losses, expectancy `-0.6482720085510278R`;
- evidence status remains `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- resolver v1.2 hardening and provenance audit remain PASS;
- post-30/portfolio diagnostics remain non-authorizing;
- future confirmation boundary is preregistered at `entry_time >= 2026-09-16T13:00:00Z`;
- the primary future hypothesis fixes `SHORT && h1_ema_sep_atr < 0.9033277894201235`; discovery observations before the boundary cannot count as confirmation;
- path-quality diagnostics show 7/26 STOP families reached at least +1R before eventual non-positive resolution, while TIME_EXIT is 9/13 profitable with `+0.189R` expectancy; these findings are hypothesis-generating only;
- execution drag averages about `0.067R`, while estimated pre-cost expectancy remains strongly negative at about `-0.581R`;
- leave-one-symbol-out expectancy remains negative for every single-symbol exclusion, while strong day/regime variation remains visible;
- fail-closed prospective research orchestrator is plan-only by default, has explicit `--execute`, writes manifests, and stops later stages after any stage failure;
- orchestration regression tests are `4/4 PASS` and synthetic failure-path validation confirmed `LATER_STAGES_BLOCKED=PASS`;
- disk-retention helper/service remain validated in `DRY_RUN_ONLY` mode and the timer remains **disabled by design**;
- no general sudo or Docker privilege was broadened;
- no rebase/force update is permitted or used.

## Latest accepted research checkpoints

- `2026-09-16_PREREG_PATH_PIPELINE_HARDENING.md` — preregistration boundary, MFE/MAE/TIME_EXIT path analysis, execution-cost decomposition and fail-closed pipeline hardening;
- `2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md` — 12:00Z parallel diagnostics, provenance/hardening acceptance and discovery-stage future-version hypothesis;
- `2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md` — resolver-v1.2 guard update and parity acceptance;
- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — post-soak catch-up and disk-retention dry-run state;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — initial 30–49-family diagnostic baseline;
- `2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md` — extended-soak closure.

## Previous transition bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`

Its active-soak instructions are superseded by the current checkpoint.

## Related documents

- current state: `../CURRENT_STATE.md`;
- hypothesis preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- path-quality diagnostics implementation: `../../research/strategy_benchmark_v1/prospective_path_quality_diagnostics.py`;
- fail-closed research orchestration: `../../research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`;
- resolver v1.2: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`;
- disk policy: `../operations/DISK_RETENTION_POLICY.md`;
- corrected historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
