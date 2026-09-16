# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_1930Z_PROJECT_SYNC.md`

Current accepted state:

- Phase 11G **ACTIVE**; Phase 12 **FUTURE / NOT ACTIVE**;
- production SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, health `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate `candidate_rule_set_v2_2`, harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- resolver v1.3; ledger v1.2 with immutable first-seen event payload;
- holdout untouched/unauthorized;
- latest accepted cutoff `2026-09-16T19:30:00Z`;
- prospective state `61` eligible observations / `47` primary families / `47` resolved / `0` unresolved;
- wins/losses `13/34`, expectancy `-0.5989123384630131R`;
- confirmation sample `3/3 resolved`, still underpowered;
- current open primary families `0`;
- state provenance `5/5 PASS`, `0` mismatches;
- Phase 11G Path A `47/100`, shortfall `53`; Path B not selected;
- production remains read-only; no trading action authorized;
- Phase 10P Plugin migration preparation includes the typed eight-tool read-only MCP/App surface; no cutover performed;
- broad adaptive strategy discovery remains delegated to `K_Investigation_Forecast` until the user explicitly reports positive results.

## Latest accepted research checkpoints

- `2026-09-16_1930Z_PROJECT_SYNC.md` — authoritative 19:30Z project synchronization and resume state;
- `2026-09-16_1900Z_LEDGER_V1_2_RECOVERY.md` — ledger-v1.2 causality recovery and accepted 19:00Z state;
- `2026-09-16_1830Z_PROSPECTIVE_MATERIAL_UPDATE.md` — fully resolved `47/47` prospective sample after 18:15Z material change;
- `2026-09-16_1630Z_PARALLEL_HARDENING_COMPLETE.md` — prior 16:30Z causal/hardening state;
- `2026-09-16_1615Z_HARDENING_PLUGIN_MIGRATION.md` — prior evidence/hardening state;
- `2026-09-16_PROSPECTIVE_1415Z_CONTINUITY.md` — earlier continuity state;
- `2026-09-16_PROSPECTIVE_1345Z_RESOLVER_V1_3.md` — resolver-v1.3 acceptance.

## Related documents

- current state: `../CURRENT_STATE.md`;
- current new-chat handoff: `../operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`;
- current Phase 11G closure audit: `../research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`;
- ledger v1.2 acceptance: `../research/PROSPECTIVE_LEDGER_V1_2_ACCEPTANCE_2026-09-16.md`;
- resolver v1.3: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- max-hold evidence semantics: `../research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`;
- hypothesis preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- pipeline v2 acceptance: `../research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`;
- recovery: `../operations/RESEARCH_RECOVERY_RUNBOOK.md`;
- stress economics: `../research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`;
- execution compatibility: `../architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`;
- Plugin migration: `../plugin_migration/README.md`;
- Plugin typed tool surface: `../plugin_migration/MCP_TOOL_SURFACE_V1.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
