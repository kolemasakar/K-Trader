# K-Trader Checkpoints

This directory contains accepted snapshots used to recover the exact project state between work sessions/chats.

## Current checkpoint

`2026-09-16_1630Z_PARALLEL_HARDENING_COMPLETE.md`

Current accepted state:

- Phase 11G **ACTIVE**; Phase 12 **FUTURE / NOT ACTIVE**;
- production SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`, health `ok`, mode `read_only`, `data_ready=true`, provider `binance_usdm`;
- frozen candidate `candidate_rule_set_v2_2`, harness SHA `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- holdout untouched/unauthorized;
- latest accepted cutoff `2026-09-16T16:30:00Z`;
- ledger `61` eligible observations / `47` unique primary families;
- outcome state `43` resolved / `4` unresolved, wins/losses `13/30`, expectancy `-0.5539825538227888R`;
- ADAUSDT/DOGEUSDT `08:15Z` primary families resolved as positive TIME_EXIT at `16:15Z`;
- confirmation sample remains `3` unresolved primary families, all SHORT/REST;
- evidence tracker/provenance invariants PASS;
- max observed concurrent all/SHORT `8`, largest correlated cohort `4`; no production caps selected;
- portfolio policy simulation confirms concentration can be reduced but does not repair negative strategy expectancy;
- pipeline v2 accepted as canonical future orchestration entry point, with full current research tests `10/10 PASS`;
- Phase 11G closure audit: infrastructure/evidence/economic packaging complete, Path A `43/100`, Path B not selected;
- future execution compatibility contract documented; production remains read-only;
- storage/provenance audit PASS, retention timer disabled;
- Phase 10P Plugin Migration preparation includes skill/integration/regression/implementation blueprint; current Custom GPT remains legacy compatibility wrapper until replacement acceptance;
- broad adaptive strategy discovery remains delegated to `K_Investigation_Forecast` until the user reports positive results.

## Latest accepted research checkpoints

- `2026-09-16_1630Z_PARALLEL_HARDENING_COMPLETE.md` — authoritative 16:30Z state after causal resolution and full parallel-hardening package;
- `2026-09-16_1615Z_HARDENING_PLUGIN_MIGRATION.md` — prior 16:15Z evidence/hardening state;
- `2026-09-16_PROSPECTIVE_1415Z_CONTINUITY.md` — prior 14:15Z continuity state;
- `2026-09-16_PROSPECTIVE_1345Z_RESOLVER_V1_3.md` — resolver-v1.3 acceptance;
- `2026-09-16_PREREG_PATH_PIPELINE_HARDENING.md` — preregistration, path-quality and pipeline hardening;
- `2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md` — parallel diagnostics/provenance;
- `2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md` — prior resolver-v1.2 acceptance;
- `2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md` — post-soak catch-up/retention validation.

## Related documents

- current state: `../CURRENT_STATE.md`;
- new-chat handoff: `../operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1630Z.md`;
- resolver v1.3: `../research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- max-hold evidence semantics: `../research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`;
- hypothesis preregistration: `../research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- portfolio-risk contract: `../research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`;
- portfolio simulation: `../research/PORTFOLIO_RISK_POLICY_SIMULATION_2026-09-16_1630Z.md`;
- pipeline v2 acceptance: `../research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`;
- recovery: `../operations/RESEARCH_RECOVERY_RUNBOOK.md`;
- Phase 11G closure: `../research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1630Z.md`;
- stress economics: `../research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`;
- execution compatibility: `../architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`;
- storage/provenance: `../operations/STORAGE_PROVENANCE_AUDIT_2026-09-16_1630Z.md`;
- Plugin migration: `../plugin_migration/README.md`.

A checkpoint does not replace canonical specifications. It records the accepted state to resume from.
