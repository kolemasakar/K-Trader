# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T16:30:00Z` and completion of the current parallel-hardening package.

Current checkpoint:

`docs/checkpoints/2026-09-16_1630Z_PARALLEL_HARDENING_COMPLETE.md`

## Core specifications

- resolver: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`;
- preregistration: `docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`;
- max-hold evidence semantics: `docs/research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`;
- portfolio-risk contract: `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`;
- pipeline-v2 acceptance: `docs/research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`;
- Phase 11G closure criteria: `docs/research/PHASE_11G_CLOSURE_CRITERIA.md`;
- Phase 11G current audit: `docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1630Z.md`;
- stress economics: `docs/research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`;
- execution compatibility: `docs/architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`;
- recovery: `docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`;
- Plugin migration: `docs/plugin_migration/README.md`.

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime:

- host `k-trader-prod-vnic`;
- health `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- no production deploy, restart or trading action performed by the current research/hardening work;
- current public API remains GET-only;
- container safety baseline remains accepted.

Storage:

- root filesystem rounded utilization about `20%`;
- `/data/research` measured at `1,471,489,881` bytes during the 16:30 audit;
- disk-retention remains `DRY_RUN_ONLY`;
- destructive mode absent;
- `ktrader-disk-retention.timer` disabled by design.

## Research boundary

Research branch:

`research-strategy-benchmark-v1`

Canonical main baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

No frozen rule, RR, 32-M15 max hold, risk gate, side filter or production authorization changed.

Holdout remains `UNTOUCHED / NOT AUTHORIZED`.

Phase 11G remains **ACTIVE**. Phase 12 remains **FUTURE / NOT ACTIVE**.

Broad strategy-discovery/self-improving-strategy research remains delegated to `K_Investigation_Forecast` and must not be reopened inside K-Trader until the user explicitly reports positive results.

## Latest accepted prospective state — 16:30Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T163000Z`

Capture:

- status `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- current-capture eligible setups `49`;
- event count `299`;
- signal bars evaluated `6574`;
- bundle-set SHA256 `c5441c81e73c47724a471410fd7e9273b7531029f6b2cc87b479442695b70c02`;
- shadow summary SHA256 `d39dfd2b6ae2276a4d0346a2fd97e350a3e598522bdc9ddf5601da92daf97277`;
- holdout false;
- production false.

Ledger:

- eligible observations `61`;
- unique primary families `47`;
- one historical infrastructure-invalid snapshot remains excluded;
- current causal ledger remains frozen-harness/protocol consistent.

Funding:

- symbols `19`;
- records `1878`;
- SHA256 `dc5e342f5e7a6857558b90c733ee37507e4a5dc5181e41dab764c0978bd9535f`.

## Resolver v1.3 — accepted 16:30Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T163000Z`

Summary SHA256:

`433097e2148e52fdb506f7c69adcb5114e147a8cce834fd8e9fab56d7529799d`

State:

- unique primary families `47`;
- resolved primary families `43`;
- unresolved primary families `4`;
- wins/losses `13/30`;
- win rate `30.232558%`;
- expectancy `-0.5539825538227888R`;
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prior terminal reuse `52`;
- current-path revalidated `45`;
- aged-out accepted terminal outcomes preserved `7`;
- max prior entry delta `0.0`;
- max prior stop delta `5.643861156201524e-09`;
- network false;
- holdout false;
- production false.

Newly resolved primary families:

- ADAUSDT SHORT `08:15Z` -> `TIME_EXIT 16:15Z`, `+0.3680360268R`;
- DOGEUSDT SHORT `08:15Z` -> `TIME_EXIT 16:15Z`, `+0.0098372160R`.

Both are discovery-context families and do not count toward post-prereg confirmation.

## Important resolver recovery rule

Do **not** use the obsolete standalone runtime file:

`/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`

It lacks canonical v1.3 scale-aware stop identity handling.

The 16:30Z fail-closed diagnostic proved:

- all `52` prior-resolved identities retain exact entry price;
- maximum stop drift `5.643861156201524e-09`;
- worst drift is only `1.663724e-07` of accepted initial risk;
- no accepted row exceeds canonical v1.3 tolerance `1e-4` of initial risk.

Future cycles must use repository pipeline v2 / hash-pinned canonical v1.3. The accepted 16:30Z rerun used the canonical repository implementation staged under `/tmp/ktrader-runtime-v2/`.

## Diagnostics — 43 resolved

Descriptive SHA256:

`e2621b9c80ba60fcb8cd8ad124a3bfb2e736d3beda3084f1488a2e611a2317f4`

Statistical SHA256:

`af2b4d758f9cafd4d1103f6aa480b32d0a0f5171a2e0850d8d18e360c20e8b89`

Key state:

- overall expectancy `-0.553983R`;
- LONG expectancy `-0.585215R`, `13` resolved;
- SHORT expectancy `-0.540448R`, `30` resolved;
- STOP `26`, wins `0`, expectancy `-1.066884R`;
- TIME_EXIT `17`, wins `13`, expectancy `+0.230456R`;
- no exploratory contrast currently authorizes a frozen-v2.2 retune;
- obstacle <1R/<3R remains exploratory;
- VSA remains non-authorizing.

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Evidence tracker SHA256:

`ba67252fb80cc2efb1f95a92c96dece0773a5a0e8c75bee3a539f6340647b775`

Counts:

- discovery primary families `44`;
- confirmation primary families `3`;
- confirmation resolved `0`;
- confirmation unresolved `3`;
- all current confirmation families are `SHORT / REST`;
- no preregistered hypothesis can yet be evaluated;
- chronology/governance invariants PASS.

Unresolved primary families:

Discovery context:

- TRUMPUSDT SHORT `12:30Z`.

Post-prereg confirmation:

- ADAUSDT SHORT `13:15Z`;
- DOGEUSDT SHORT `13:15Z`;
- ADAUSDT SHORT `15:00Z`.

## Portfolio risk

16:30Z risk-report SHA256:

`ff68a829f811db426511f250e3a93769fce756dc64952bad538a13da18932e6e`

Observed:

- current open families `4`, all SHORT;
- observed max concurrent all `8`;
- observed max concurrent SHORT `8`;
- largest correlated cohort `4`.

Policy simulation:

`docs/research/PORTFOLIO_RISK_POLICY_SIMULATION_2026-09-16_1630Z.md`

Runtime SHA256:

`a336d786b7c9f061c23ddae2490f8aa96951a28f7436bd80b2d7aacb8ef5e38c`

All tested cap scenarios reduced concentration but left resolved accepted expectancy near `-0.60R`. Portfolio caps are risk controls, not an alpha repair. No production cap selected.

## Prospective pipeline v2

Canonical future orchestration entry point:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Acceptance:

- v2 tests `2/2 PASS`;
- v1 regressions `6/6 PASS`;
- current complete research test directory `10/10 PASS`;
- runtime plan preflight `13` files, `8` stages, PASS;
- plan manifest SHA256 `4b69ddf71296179ae0ec038ee8c9c20afca552deaa68f98f7bcb29a66fb049e6`.

Pipeline v1 is retained for history/audit but is no longer preferred.

## Phase 11G closure state

Audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1630Z.md`

All currently available infrastructure, evidence-governance and portfolio/economic packaging gates are complete.

Stress baseline:

`docs/research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`

Closure paths:

- Path A is not ready: `43/100` resolved primary families, shortfall `57`, confirmatory hypotheses underpowered;
- Path B has not been selected by the user.

Therefore Phase 11G remains ACTIVE.

## Execution compatibility

Future execution architecture contract:

`docs/architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`

It defines normalized tick/step/min-max quantity/notional/order/margin/leverage/position-mode constraints and fail-closed pre-trade gates. It does not enable execution.

## Storage / provenance

Audit:

`docs/operations/STORAGE_PROVENANCE_AUDIT_2026-09-16_1630Z.md`

Machine state:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T163000Z.json`

SHA256:

`0608850f392f2f5beb5cf7be993b6c30effd67b615b9dc44c253e0f67c8aa8a5`

All five referenced source hashes independently recomputed with `0` mismatches.

## OpenAI product migration — Phase 10P

The Custom GPT remains a supported legacy compatibility wrapper until replacement acceptance.

Prepared migration package:

- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`;
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`;
- `docs/plugin_migration/REGRESSION_SUITE.md`;
- `docs/plugin_migration/SOURCE_ASSESSMENT_2026-09-16.md`;
- `docs/plugin_migration/PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md`;
- legacy Custom GPT assets retained under `custom_gpt/`.

Target architecture:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only K-Trader backend`

Do not cut over until Plugin product-side integration/auth/permissions/regression/sharing acceptance passes.

## Next work order

1. Continue causal prospective collection with pipeline v2 and resolver v1.3.
2. Use `.../prospective_v2_2_outcomes_offline_v1_3/20260916T163000Z` as the next prior accepted outcomes state.
3. Preserve prereg boundary `2026-09-16T13:00:00Z` and keep confirmation evidence separate.
4. Refresh diagnostics only on material sample change.
5. Keep frozen v2.2, holdout closure, production read-only state and retention timer state unchanged.
6. Continue Phase 10P preparation without disabling the existing Custom GPT before replacement acceptance.
7. Do not reopen broad `K_Investigation_Forecast` strategy discovery until the user explicitly returns positive results.
