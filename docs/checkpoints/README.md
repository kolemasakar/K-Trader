# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-14_CHAT_TRANSITION_EXTENDED_SOAK.md`

Current accepted state:

- Phase 11G remains ACTIVE; Phase 12 remains FUTURE / NOT ACTIVE;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- production health at soak start was `ok`, mode `read_only`, provider `binance_usdm`;
- scanner `DEGRADED` is the known fail-closed/history-readiness state;
- extended soak window is active from `2026-09-14 06:08 Europe/Kyiv` through `2026-09-16 09:00 Europe/Kyiv`;
- published K_Trader read-only analysis/data access is allowed during soak;
- deploy/restart/config mutation/package upgrade/manual prospective runs/retuning/holdout opening/new VM automation are forbidden during soak;
- `apt-daily.timer` and `apt-daily-upgrade.timer` are `masked-runtime`; corresponding services are inactive and have no next activation;
- root disk usage at soak start was `18%`;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- holdout remains untouched and unauthorized;
- latest accepted prospective cutoff is `2026-09-13T13:00:00Z`;
- accepted prospective state is 17 eligible observations, 12 unique families, 12 resolved primary families, 0 unresolved, 1 win / 11 losses, expectancy `-0.9007780994315739R`;
- evidence remains `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`;
- corrected historical inference uses causal rolling M15=400 / H1=300 replay and not superseded unbounded-context runs;
- corrected historical expectancy: P25 `+0.259415R`, R90 `+0.031637R`, R180 `-0.013131R`, R365 `-0.051000R`;
- no LONG-only or other in-place frozen-v2.2 rule change is authorized;
- disk-retention policy is approved (`>=80%` usage -> oldest 20% of explicitly eligible reproducible/temporary data), but automatic VM cleanup is not installed until after soak closure;
- no rebase/force update is permitted or used.

## New-chat bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`

Recovery instruction:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md">>`

## Recent research checkpoints

- `2026-09-14_CHAT_TRANSITION_EXTENDED_SOAK.md` — authoritative chat-transition checkpoint during the active extended soak;
- `2026-09-14_EXTENDED_SOAK_PAUSE_START.md` — extended production soak, APT freeze and allowed/forbidden operations;
- `2026-09-13_V2_2_PROSPECTIVE_1300Z.md` — latest accepted prospective capture/ledger;
- `2026-09-13_V2_2_PROSPECTIVE_1300Z_OUTCOME_ADDENDUM.md` — accepted 12/12 resolved family outcomes at 13:00Z;
- `2026-09-13_V2_2_PROSPECTIVE_1200Z.md` — prior prospective capture;
- `2026-09-13_V2_2_PROSPECTIVE_1200Z_OUTCOME_ADDENDUM.md` — accepted prior outcome state and float-cache finding;
- `2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md` — corrected bounded-context historical replay, parity gate and P25/R90/R180/R365 results;
- `2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md` — earlier dual-track checkpoint; historical inference section superseded by causal rolling replay;
- `2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md` — earlier catch-up/runtime acceptance;
- `2026-09-13_POST_PAUSE_RESUME.md` — earlier post-pause production audit;
- `2026-09-12_PRE_FREEZE_FINAL_CHECK.md` — pre-freeze verification;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics and profile baselines;
- `2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md` — parallel research diagnostics;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- active handoff: `../handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`;
- disk policy: `../operations/DISK_RETENTION_POLICY.md`;
- corrected historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- historical expansion supersession: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- offline resolver: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
