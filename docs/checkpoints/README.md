# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md`

Current accepted state:

- Phase 11G remains **ACTIVE**; Phase 12 remains **FUTURE / NOT ACTIVE**;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- production health remains `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA remains `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- holdout remains untouched and unauthorized;
- latest accepted prospective cutoff is `2026-09-16T12:00:00Z`;
- ledger state is `56` eligible observations / `43` unique families;
- outcome state remains `39` resolved primary families / `4` unresolved, `9` wins / `30` losses, expectancy `-0.6482720085510278R`;
- evidence status remains `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- resolver v1.2 hardening and provenance audit both passed;
- `50/50` previously resolved observations retain zero terminal/economic mismatches;
- four open primary families remain causal/open and must not be forced to TIME_EXIT early;
- post-30/portfolio diagnostics remain non-authorizing;
- a post-hoc `SHORT × low H1 EMA-separation/ATR` effect is registered as a **future-version hypothesis only**; it is not a frozen-v2.2 filter;
- historical context has the same sign for this hypothesis across P25/R90/R180/R365, but this is not fresh OOS validation;
- disk-retention helper/service remain validated in `DRY_RUN_ONLY` mode and the timer remains **disabled by design**;
- no general sudo or Docker privilege was broadened;
- no rebase/force update is permitted or used.

## Latest accepted research checkpoints

- `2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md` — authoritative 12:00Z parallel diagnostics, provenance/hardening acceptance and registered future-version hypothesis;
- `2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md` — resolver-v1.2 guard update and parity acceptance;
- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — post-soak catch-up and disk-retention dry-run state;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — initial 30–49-family diagnostic baseline;
- `2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md` — extended-soak closure.

## Previous transition bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`

Its active-soak instructions are superseded by the current checkpoint.

## Recent research checkpoints

- `2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md` — current accepted diagnostic state;
- `2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md` — 11:45Z resolver-v1.2 acceptance;
- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — 10:30Z catch-up and retention validation;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — post-30 baseline;
- `2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md` — soak PASS and APT restoration;
- `2026-09-14_CHAT_TRANSITION_EXTENDED_SOAK.md` — transition during soak;
- `2026-09-14_EXTENDED_SOAK_PAUSE_START.md` — soak start;
- `2026-09-13_V2_2_PROSPECTIVE_1300Z.md` — earlier prospective capture;
- `2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md` — corrected causal historical replay;
- `2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md` — post-pause acceptance;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family semantics/profile baselines;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- disk policy: `../operations/DISK_RETENTION_POLICY.md`;
- disk-retention implementation: `../../ops/disk_retention/`;
- resolver v1.2: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`;
- corrected historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- historical expansion supersession: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
