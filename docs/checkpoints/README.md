# K-Trader Checkpoints

This directory contains transition snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-12_PRE_FREEZE_FINAL_CHECK.md`

Current accepted research state:

- accepted/deployed production application SHA remains `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- fresh localhost and public HTTPS health checks at ~`2026-09-12T05:50:31Z` returned HTTP 200 with `status=ok`, `mode=read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate remains `candidate_rule_set_v2_2`;
- frozen harness SHA256 remains `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- frozen prospective boundary remains `2026-09-11T20:00:00Z`;
- holdout remains untouched and unauthorized;
- requested exact `2026-09-12T05:45:00Z` final shadow capture was blocked by the connected SentinelX identity lacking Docker/root permission; no substitute calculation was asserted;
- latest valid frozen shadow snapshot remains `2026-09-12T04:45:00Z`;
- latest valid ledger: 7 snapshots / 31 deduplicated events / 6 eligible observations / 4 unique families / 2 resolved primary families;
- the 2 resolved families are both STOP, with realized results about `-1.0221R` and `-1.0350R`; 2 families remain unresolved;
- evidence remains `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`;
- the two resolved STOP families are also the two current Level Context v2 disagreements with frozen open-space classification; this is diagnostic only and changes no gate;
- FAST v0 remains a negative baseline; SWING v0 remains near-breakeven base but negative validation/stress; POSITION W1 remains prototype-only;
- approved GPT Builder v1.3 and active Knowledge Priority files are present on the research branch; canonicalization is tracked in PR #57;
- PR #57 is open/mergeable at head `1543861ff9e8ee97e64371a0b41e467ee1c866d1`; CI run 195 is in progress and merge remains gated by `canonical-merge-gate`;
- no post-hoc subgroup or feature has been promoted into frozen v2.2;
- next hard evidence milestone remains `>=30 unique resolved prospective frozen-v2.2 setup families`;
- planned technical freeze remains `2026-09-12 09:00 Kyiv` -> `2026-09-13 09:00 Kyiv` (`06:00Z` -> `06:00Z`);
- production safety is PASS;
- exact 05:45Z research finalization is blocked by authorization boundary;
- strict host freeze integrity is also blocked while `apt-daily.timer` and `apt-daily-upgrade.timer` remain active with triggers inside the freeze window;
- overall clean-freeze gate is therefore **NO-GO / NOT FULL PASS** until these blockers are resolved or explicitly accepted as boundary exceptions;
- Phase 11G remains active;
- Phase 12 remains FUTURE / NOT ACTIVE.

## Recent research checkpoints

- `2026-09-12_PRE_FREEZE_FINAL_CHECK.md` — fresh production verification, latest valid 04:45Z family outcomes, exact 05:45Z authorization blocker, APT freeze-integrity blocker and freeze decision;
- `2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md` — family outcome semantics/resolver, FAST/SWING baseline execution, POSITION W1 contract;
- `2026-09-12_V2_2_FIRST_PROSPECTIVE_FAMILIES_AND_PROFILE_DATASET.md` — first non-empty frozen prospective snapshot, adaptive profile dataset and funding completeness;
- `2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md` — Level/VSA/execution/portfolio/robustness diagnostics and prospective-infrastructure hardening;
- `2026-09-11_V2_2_FIRST_PROSPECTIVE_SHADOW_CAPTURE.md` — initial prospective shadow capture state;
- `2026-09-11_STRATEGY_V2_2_PREHOLDOUT_CHECKPOINT.md` — frozen v2.2 pre-holdout state;
- `2026-09-11_STRATEGY_SYNTHESIS_V2_1.md` — v2.1 synthesis;
- `2026-09-11_STRATEGY_BENCHMARK_V1_DISCOVERY_GATE.md` — first benchmark discovery gate;
- `2026-09-11_PHASE11G_STRATEGY_RESEARCH_HANDOFF.md` — Phase 11G handoff into independent strategy research;
- `2026-09-11_PHASE11G_SURVIVORSHIP_AND_PRE_FREEZE_ACCEPTANCE.md` — survivorship diagnostic deployment and pre-freeze acceptance;
- `2026-09-11_PHASE11G_PRE_PAUSE_DEPLOYMENT_AND_24H_OBSERVATION.md` — pre-freeze baseline after single-writer deployment;
- `2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_DEPLOYMENT.md` — canonical prospective-control production activation;
- `2026-09-11_PHASE11G_PROSPECTIVE_CONTROL_HARDENING.md` — prospective-control tooling hardening;
- `2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md` — 24h control and production hardening;
- `2026-09-10_PHASE11G_MONITORING_AND_READINESS_CHECKPOINT.md` — accumulation/readiness state;
- `2026-09-09_PHASE11G_HORIZON_TIMESPLIT_VALIDATION.md` — horizon time-split validation;
- `2026-09-09_PHASE11G_PROD_TTL_AND_CORRECTED_WINDOWS_1_4.md` — FAST production rollout and corrected W1-W4 closure;
- `2026-09-09_PHASE11G_HORIZON_PROFILE_LIFECYCLE_STUDY.md` — horizon lifecycle sensitivity study;
- `2026-09-09_PHASE11G_SETUP_LIFECYCLE_60M_GATE.md` — canonical FAST TTL60 gate;
- `2026-09-08_PHASE11G_CORRECTED_REPLAY_RR_GEOMETRY_GATE.md` — RR geometry/corrected replay checkpoint;
- `2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md` — accepted two-chain catalogue state.

## Related documents

- current state: `../CURRENT_STATE.md`;
- family outcome semantics: `../research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`;
- latest profile/prospective report: `../research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`;
- strategy benchmark protocol: `../research/STRATEGY_BENCHMARK_RESEARCH_PROTOCOL.md`;
- Phase 11G boundary: `../PHASE_11G_CHECKPOINT.md`;
- deployment specification: `../DEPLOYMENT.md`;
- roadmap: `../../ROADMAP.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
