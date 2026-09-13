# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-13_V2_2_PROSPECTIVE_1200Z.md`

Current accepted state:

- Phase 11G remains ACTIVE; Phase 12 remains FUTURE / NOT ACTIVE;
- production deployed SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, healthy and read-only;
- frozen candidate remains `candidate_rule_set_v2_2` with harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- holdout remains untouched and unauthorized;
- Track B historical inference uses the corrected causal rolling-context replay, not the earlier unbounded-context Historical Expansion v1 results;
- corrected replay uses `400` M15 + `300` H1 closed bars per historical decision and passed prospective parity with `0` mismatches across 19/19 symbols, 1824 checked M15 decisions, 70 signal cases and 69 structural cases;
- corrected historical base expectancy: P25 `+0.2594R`, R90 `+0.0316R`, R180 `-0.0131R`, R365 `-0.0510R`;
- frozen stress expectancy: P25 `+0.2249R`, R90 `-0.0097R`, R180 `-0.0429R`, R365 `-0.0745R`;
- interpretation: v2.2 is currently a recent/regime-dependent candidate, not a long-horizon historically robust strategy;
- no LONG-only or other in-place rule change is authorized;
- latest accepted prospective capture/ledger cutoff is `2026-09-13T12:00:00Z`;
- latest prospective capture: `VALID_SHADOW_CAPTURE`, panel `19/19`, 124 deduplicated events, 17 eligible observations, 12 unique families;
- new family `f7c6c400...` is `VTHOUSDT LONG`, primary entry `2026-09-13T09:00:00Z`;
- Level Context at 12 families remains diagnostic-only: clean-break `4`, disagreements `2`, obstacle-inside-3R `5`, inside-1R `4`;
- fresh deterministic resolver for the 12:00Z ledger is pending because the execution channel blocked the invocation before server execution;
- last accepted resolver state remains 9 resolved primary families / 2 unresolved, 1 win / 8 losses, expectancy `-0.8807054663R` at 08:30Z;
- historical trades are never merged into prospective family-count thresholds;
- no rebase/force update is permitted or used.

## New-chat bootstrap

`../handoffs/BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md`

Recovery instruction:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md">>`

## Recent research checkpoints

- `2026-09-13_V2_2_PROSPECTIVE_1200Z.md` — latest accepted prospective capture/ledger and Level Context state; outcome resolver refresh pending;
- `2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md` — accepted corrected bounded-context historical replay, parity gate, and corrected P25/R90/R180/R365 results;
- `2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md` — earlier dual-track checkpoint; historical inference section superseded by the causal rolling-replay acceptance checkpoint;
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
- corrected historical replay protocol: `../research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`;
- historical expansion supersession: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`;
- historical expansion original protocol: `../research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_PROTOCOL.md`;
- family semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- prospective protocol: `../research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`;
- profile/prospective report: `../research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`;
- strategy benchmark protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
