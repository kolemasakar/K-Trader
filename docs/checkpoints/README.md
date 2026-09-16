# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md`

Current accepted state:

- Phase 11G remains **ACTIVE**; Phase 12 remains **FUTURE / NOT ACTIVE**;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- extended production soak completed with `PASS`;
- APT freeze was removed through the existing bounded helper; `apt-daily.timer` and `apt-daily-upgrade.timer` are `enabled / active`;
- production health remains `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- root filesystem is approximately `19%` used on the verified `45G` `/dev/sda1` filesystem;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA remains `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- holdout remains untouched and unauthorized;
- latest accepted prospective cutoff is `2026-09-16T10:30:00Z`;
- ledger state is `56` eligible observations / `43` unique families;
- accepted outcome state is `39` resolved primary families / `4` unresolved, `9` wins / `30` losses, expectancy `-0.6482720085510278R`;
- evidence status is `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- resolver v1.1 parity is accepted: `17/17` prior observations preserved and archived terminal/exit replay matched `17/17` with zero mismatches;
- diagnostic tier does not authorize retuning, direction filtering, RR/max-hold/risk-gate changes, holdout opening or production mutation;
- disk-retention dry-run planner is production-path aware (`/opt/k-trader/data/research`), has a narrow reviewed allowlist and contains no destructive mode;
- production-equivalent retention validation found `38` eligible bundle candidates and a deterministic `20`-candidate / ~`97 MB` dry-run plan at `19%` disk usage, with no deletion;
- host installation of the dry-run timer remains pending a bounded owner-side root action;
- no general sudo or Docker privilege was broadened;
- no rebase/force update is permitted or used.

## Latest accepted research checkpoints

- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — authoritative 10:30Z catch-up, resolver parity and production-path disk-retention dry-run state;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — accepted 30–49-family diagnostic baseline;
- `2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md` — earlier post-soak 09:45Z closure/catch-up checkpoint.

## Previous transition bootstrap

The previous chat-transition package remains available for historical recovery context:

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`

Its active-soak instructions are superseded because the soak has completed.

## Recent research checkpoints

- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — 10:30Z catch-up, 39/43 resolved state, resolver-v1.1 parity, retention dry-run validation;
- `2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md` — diagnostic-only statistical baseline at 39 resolved families;
- `2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md` — extended-soak PASS, APT restoration and earlier 09:45Z catch-up;
- `2026-09-14_CHAT_TRANSITION_EXTENDED_SOAK.md` — prior transition checkpoint during soak;
- `2026-09-14_EXTENDED_SOAK_PAUSE_START.md` — soak start and APT freeze;
- `2026-09-13_V2_2_PROSPECTIVE_1300Z.md` — prior accepted prospective capture/ledger;
- `2026-09-13_V2_2_PROSPECTIVE_1300Z_OUTCOME_ADDENDUM.md` — prior 12/12 resolved-family state;
- `2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md` — corrected bounded-context historical replay;
- `2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md` — earlier catch-up/runtime acceptance;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics and profile baselines;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- disk policy: `../operations/DISK_RETENTION_POLICY.md`;
- disk-retention implementation: `../../ops/disk_retention/`;
- resolver v1.1: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_1.md`;
- corrected historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- historical expansion supersession: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
