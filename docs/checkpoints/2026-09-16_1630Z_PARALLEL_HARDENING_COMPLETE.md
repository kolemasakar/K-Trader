# K-Trader Checkpoint — 2026-09-16 16:30Z

Status: **ACCEPTED / PARALLEL HARDENING COMPLETE / PHASE 11G ACTIVE**

## Production invariants

- deployed application SHA: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- health: `ok`;
- mode: `read_only`;
- `data_ready=true`;
- provider: `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- no production deployment, restart or order/trading action occurred;
- holdout remains untouched/unauthorized;
- disk-retention timer remains disabled; destructive retention absent.

## Frozen research boundary

- strategy: `candidate_rule_set_v2_2`;
- harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA256: `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`;
- RR/max-hold/risk gates/side logic unchanged;
- Phase 11G ACTIVE;
- Phase 12 FUTURE / NOT ACTIVE;
- broad adaptive strategy research remains delegated to `K_Investigation_Forecast`.

## Accepted prospective cutoff — 16:30Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T163000Z`

Capture:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- eligible setups `49`;
- event count `299`;
- signal bars evaluated `6574`;
- bundle-set SHA256 `c5441c81e73c47724a471410fd7e9273b7531029f6b2cc87b479442695b70c02`;
- shadow summary SHA256 `d39dfd2b6ae2276a4d0346a2fd97e350a3e598522bdc9ddf5601da92daf97277`;
- holdout false;
- production action false.

Funding:

- records `1878`;
- symbols `19`;
- SHA256 `dc5e342f5e7a6857558b90c733ee37507e4a5dc5181e41dab764c0978bd9535f`.

## Resolver v1.3

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T163000Z`

Summary SHA256:

`433097e2148e52fdb506f7c69adcb5114e147a8cce834fd8e9fab56d7529799d`

State:

- eligible observations `61`;
- unique primary families `47`;
- resolved primary families `43`;
- unresolved primary families `4`;
- wins/losses `13/30`;
- win rate `30.232558%`;
- expectancy `-0.5539825538227888R`;
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- prior terminal reuse `52`;
- prior terminal path revalidated `45`;
- prior terminal source-window expired `7`;
- max prior entry delta `0.0`;
- max prior stop delta `5.643861156201524e-09`;
- network false;
- holdout false;
- production false.

New primary resolutions:

- `ADAUSDT SHORT`, entry `08:15Z` -> `TIME_EXIT 16:15Z`, `+0.3680360268R`;
- `DOGEUSDT SHORT`, entry `08:15Z` -> `TIME_EXIT 16:15Z`, `+0.0098372160R`.

Both are pre-prereg discovery context.

## Resolver runtime incident and resolution

The first 16:30Z resolver invocation used an obsolete standalone file:

`/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`

That stale file lacked canonical v1.3 scale-aware `stop_close` semantics and correctly failed closed on a RAYSOLUSDT recomputation drift.

Diagnostic result across `52` prior-resolved identities:

- all entry prices exact (`max entry delta=0`);
- maximum stop delta `5.643861156201524e-09`;
- worst stop-drift fraction of accepted initial risk `1.663724e-07`;
- no row exceeded canonical v1.3 tolerance `1e-4` of accepted initial risk.

The accepted rerun used the hash-pinned repository v1.3 implementation staged under `/tmp/ktrader-runtime-v2/` and passed.

**Recovery rule:** do not use the stale standalone `/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`. Future cycles use canonical repository pipeline v2 / hash-pinned v1.3.

## Diagnostics — 43 resolved

Descriptive SHA256:

`e2621b9c80ba60fcb8cd8ad124a3bfb2e736d3beda3084f1488a2e611a2317f4`

Statistical SHA256:

`af2b4d758f9cafd4d1103f6aa480b32d0a0f5171a2e0850d8d18e360c20e8b89`

Key results:

- LONG expectancy `-0.585215R` (`13` resolved);
- SHORT expectancy `-0.540448R` (`30` resolved);
- STOP `26`, wins `0`, expectancy `-1.066884R`;
- TIME_EXIT `17`, wins `13`, expectancy `+0.230456R`;
- no statistical contrast authorizes retuning;
- obstacle <1R/<3R remains exploratory;
- VSA remains non-authorizing.

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Evidence tracker SHA256:

`ba67252fb80cc2efb1f95a92c96dece0773a5a0e8c75bee3a539f6340647b775`

State:

- discovery families `44`;
- confirmation families `3`;
- confirmation resolved `0`;
- confirmation unresolved `3`;
- all confirmation families are `SHORT / REST`;
- prereg hypotheses remain unevaluable/underpowered;
- chronology/holdout/network/production invariants PASS.

Unresolved primary families:

- `TRUMPUSDT SHORT 12:30Z` — discovery context;
- `ADAUSDT SHORT 13:15Z` — confirmation;
- `DOGEUSDT SHORT 13:15Z` — confirmation;
- `ADAUSDT SHORT 15:00Z` — confirmation.

## Portfolio risk

16:30Z portfolio-risk report SHA256:

`ff68a829f811db426511f250e3a93769fce756dc64952bad538a13da18932e6e`

Observed:

- current open families `4`, all SHORT;
- observed max concurrent all `8`;
- observed max concurrent SHORT `8`;
- largest correlated cohort `4`.

Additional diagnostic policy simulation:

`docs/research/PORTFOLIO_RISK_POLICY_SIMULATION_2026-09-16_1630Z.md`

Runtime report SHA256:

`a336d786b7c9f061c23ddae2490f8aa96951a28f7436bd80b2d7aacb8ef5e38c`

All four tested risk-cap scenarios still had approximately `-0.60R` expectancy on accepted resolved families. Portfolio caps reduce concentration but do not repair weak alpha. No production cap selected.

## Pipeline v2

Accepted as canonical orchestration entry point for the next fresh prospective cutoff:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Eight stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Acceptance:

- pipeline v2 tests `2/2 PASS`;
- pipeline v1 regressions `6/6 PASS`;
- current complete research test directory `10/10 PASS`;
- runtime plan preflight `13` files / `8` stages PASS;
- plan manifest SHA256 `4b69ddf71296179ae0ec038ee8c9c20afca552deaa68f98f7bcb29a66fb049e6`.

Pipeline v1 remains audit/history only.

## Phase 11G closure audit

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1630Z.md`

- mandatory infrastructure/evidence gates PASS;
- portfolio/economic packaging PASS;
- stress baseline packaged;
- no critical infrastructure blocker;
- Path A not ready: `43/100` resolved, shortfall `57`;
- Path B not selected;
- Phase 11G remains ACTIVE.

Stress economics package:

`docs/research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`

## Execution compatibility

Created:

`docs/architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`

This defines the future versioned execution-spec fields and fail-closed gates for tick/step/min-max quantity/notional/margin/leverage/position-mode/order constraints. It does not authorize execution.

## Plugin migration / Phase 10P

Prepared migration architecture now includes:

- skill draft;
- integration contract;
- regression suite;
- source assessment;
- implementation blueprint;
- legacy Custom GPT compatibility boundary.

New blueprint:

`docs/plugin_migration/PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md`

Target remains:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only K-Trader backend`

Current Custom GPT remains supported until replacement acceptance.

## Storage / provenance

Audit:

`docs/operations/STORAGE_PROVENANCE_AUDIT_2026-09-16_1630Z.md`

- root filesystem ~20% displayed utilization;
- research tree `1,471,489,881` bytes;
- retention timer disabled;
- state manifest source hashes `5/5 PASS`, mismatches `0`.

Machine state manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T163000Z.json`

SHA256:

`0608850f392f2f5beb5cf7be993b6c30effd67b615b9dc44c253e0f67c8aa8a5`

## Next work order

- continue fresh causal prospective collection using **pipeline v2**;
- prior accepted outcomes for the next run: `.../prospective_v2_2_outcomes_offline_v1_3/20260916T163000Z`;
- keep prereg boundary `13:00Z` immutable;
- accumulate confirmation families separately;
- refresh diagnostics only when sample materially changes;
- no in-place retune / holdout / Phase 12 / production execution;
- prepare Plugin replacement but do not cut over before product-side acceptance;
- do not reopen K_Investigation_Forecast strategy discovery until user reports positive results.
