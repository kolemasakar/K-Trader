# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md`

Current accepted state:

- Phase 11G remains ACTIVE; Phase 12 remains FUTURE / NOT ACTIVE;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, healthy and read-only;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- holdout remains untouched and unauthorized;
- research now operates two separated evidence tracks: prospective accumulation plus preregistered historical confirmatory expansion;
- Historical Expansion v1 uses the fixed external window `2026-08-11T14:45:00Z -> 2026-09-05T14:44:59.999Z`, 2400 M15 bars per symbol, panel `19/19`, official Binance funding and no symbol substitution;
- Historical Expansion v1 base result: 117 completed trades, WR `42.7350%`, expectancy `+0.1863256189R`, PF_R `1.347812099`, max DD `19.09473870R`;
- frozen stress-slippage result: expectancy `+0.1742143868R`, PF_R `1.326332898`;
- historical direction diagnostic: LONG `+0.3260R` vs SHORT `-0.5343R`; diagnostic only, no rule change authorized;
- latest prospective cutoff is `2026-09-13T08:30:00Z`;
- prospective capture: `VALID_SHADOW_CAPTURE`, panel `19/19`, 110 deduplicated events, 15 eligible observations, 11 unique families;
- deterministic resolver: 9 resolved primary families, 2 unresolved, 1 win / 8 losses, expectancy `-0.8807054663R`;
- prospective evidence remains `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`;
- historical trades are not merged into prospective family-count thresholds;
- no rebase/force update is permitted or used.

## New-chat bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

Recovery instruction:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md">>`

## Recent research checkpoints

- `2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md` — first accepted dual-track state: prospective evidence plus preregistered 25-day historical expansion;
- `2026-09-13_FROZEN_V2_2_CONTINUATION_0645Z.md` — first continued frozen-v2.2 snapshot after P0 plus completed research/main ancestry synchronization;
- `2026-09-13_POST_PAUSE_CATCHUP_ACCEPTANCE.md` — canonical catch-up, family resolution, continuity and runtime acceptance;
- `2026-09-13_POST_PAUSE_RESUME.md` — post-pause production audit, host APT drift, evidence/catch-up boundary and resume gate;
- `2026-09-12_PRE_FREEZE_FINAL_CHECK.md` — final pre-freeze verification and authorization/freeze-integrity blockers;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics/resolver, FAST/SWING baseline execution, POSITION W1 contract;
- `2026-09-12_V2_2_FIRST_PROSPECTIVE_FAMILIES_AND_PROFILE_DATASET.md` — first non-empty prospective families, adaptive dataset and funding completeness;
- `2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md` — Level/VSA/execution/portfolio/robustness diagnostics and prospective infrastructure;
- `2026-09-11_V2_2_FIRST_PROSPECTIVE_SHADOW_CAPTURE.md` — first prospective shadow capture;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state;
- `2026-09-11_STRATEGY_SYNTHESIS_V2_1.md` — v2.1 synthesis;
- `2026-09-11_STRATEGY_BENCHMARK_V1_DISCOVERY_GATE.md` — benchmark discovery gate.

## Related documents

- current state: `../CURRENT_STATE.md`;
- historical expansion protocol: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_PROTOCOL.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- profile/prospective report: `../research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`;
- strategy benchmark protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
