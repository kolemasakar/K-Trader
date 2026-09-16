# K-Trader New-Chat Handoff — 2026-09-16 16:30Z

Status: **READY FOR CHAT TRANSITION**

Use this package to resume K-Trader in a new chat without reopening completed work.

## 1. Authoritative repository state

Read first:

1. `docs/CURRENT_STATE.md`;
2. `docs/checkpoints/2026-09-16_1630Z_PARALLEL_HARDENING_COMPLETE.md`;
3. this handoff;
4. only then inspect deeper specifications as required.

Research branch:

`research-strategy-benchmark-v1`

Canonical main baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

## 2. Production invariant

Production application SHA remains:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Expected runtime:

- host `k-trader-prod-vnic`;
- `/health status=ok`;
- `mode=read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` is a known fail-closed/history-readiness state;
- no trading action is authorized.

At resume, verify health before research mutation. Do not deploy/restart production merely to resume research.

## 3. Frozen v2.2 boundary

Strategy:

`candidate_rule_set_v2_2`

Harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

Do not change RR, max hold, filters, sides, risk gates or frozen parameters in place.

Holdout remains `UNTOUCHED / NOT AUTHORIZED`.

Phase 11G ACTIVE. Phase 12 NOT ACTIVE.

## 4. Latest accepted prospective cutoff

`2026-09-16T16:30:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T163000Z`

Resolver output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T163000Z`

This resolver directory is the **prior accepted outcomes** input for the next fresh cycle.

State:

- observations `61`;
- primary families `47`;
- resolved `43`;
- unresolved `4`;
- wins/losses `13/30`;
- expectancy `-0.5539825538227888R`;
- governance `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`.

Newly resolved at this cutoff:

- ADAUSDT SHORT `08:15Z` -> TIME_EXIT `16:15Z`, `+0.3680360268R`;
- DOGEUSDT SHORT `08:15Z` -> TIME_EXIT `16:15Z`, `+0.0098372160R`.

## 5. Current unresolved primary families

Discovery context:

- TRUMPUSDT SHORT `12:30Z`.

Post-prereg confirmation:

- ADAUSDT SHORT `13:15Z`;
- DOGEUSDT SHORT `13:15Z`;
- ADAUSDT SHORT `15:00Z`.

Total unresolved: `4`.

## 6. Confirmation boundary

Immutable preregistration boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Current counts:

- discovery families `44`;
- confirmation families `3`;
- confirmation resolved `0`;
- confirmation unresolved `3`;
- all current confirmation families `SHORT / REST`.

Never allow pre-boundary primary families to enter confirmation counts.

## 7. Canonical resolver rule

Canonical continuation is resolver **v1.3**.

Important incident:

The standalone host/container path

`/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`

is stale and must **not** be used.

It lacks canonical scale-aware stop identity logic.

Use the repository canonical v1.3 through pipeline v2 or a fresh hash-pinned repository checkout/staging.

Canonical v1.3 semantics:

- accepted entry identity exact;
- stop recomputation accepted only under the narrow absolute guard or `<=1e-4` of accepted initial risk;
- terminal revalidation uses accepted prior entry/stop;
- accepted aged-out terminal outcomes immutable;
- mismatch => fail closed.

The 16:30Z accepted resolver run proved exact entry identity across all prior resolved observations.

## 8. Prospective pipeline v2

Use for the next fresh cycle:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Pipeline v2 is plan-only by default. Execution requires explicit `--execute`.

Acceptance evidence:

- v2 tests `2/2 PASS`;
- v1 regressions `6/6 PASS`;
- full current research tests `10/10 PASS`;
- runtime plan preflight `13` files / `8` stages PASS;
- plan manifest SHA256 `4b69ddf71296179ae0ec038ee8c9c20afca552deaa68f98f7bcb29a66fb049e6`.

Do not rerun 16:30Z merely to manufacture a pipeline-v2 execute manifest. Use v2 for the next fresh causal cutoff.

## 9. Current diagnostics

43 resolved primary families:

- overall expectancy `-0.553983R`;
- LONG `-0.585215R`;
- SHORT `-0.540448R`;
- STOP: 26, wins 0, expectancy `-1.066884R`;
- TIME_EXIT: 17, wins 13, expectancy `+0.230456R`.

These are diagnostic facts only. No exit rule or filter change is authorized.

Statistical contrasts remain non-authorizing after BH correction.

## 10. Portfolio risk

Observed maximum concurrency:

- all `8`;
- SHORT `8`;
- largest correlated cohort `4`.

A diagnostic policy simulator was added and tested. Four cap scenarios reduced concentration but left accepted resolved expectancy near `-0.60R`.

Conclusion:

portfolio controls are future risk controls; they are not an alpha repair. Do not select production caps from this already-observed sample.

Relevant docs:

- `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`;
- `docs/research/PORTFOLIO_RISK_POLICY_SIMULATION_2026-09-16_1630Z.md`.

## 11. Phase 11G closure

Audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1630Z.md`

All currently available infrastructure/evidence/portfolio/economic packaging work is complete.

Path A:

- requires `>=100` resolved primary prospective families;
- current `43`;
- shortfall `57`;
- confirmation hypotheses underpowered.

Path B:

- explicit user termination of v2.2 collection;
- not selected.

Therefore Phase 11G remains ACTIVE.

## 12. Historical stress baseline

Packaged in:

`docs/research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`

Key causal corrected windows:

- P25 BASE `+0.259415R`, STRESS `+0.224861R`;
- R90 BASE `+0.031637R`, STRESS `-0.009676R`;
- R180 BASE `-0.013131R`, STRESS `-0.042896R`;
- R365 BASE `-0.051000R`, STRESS `-0.074531R`.

Historical trades never count toward prospective evidence thresholds.

## 13. Execution architecture

Current production remains read-only.

Future execution prerequisite:

`docs/architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`

It defines required normalized execution metadata and fail-closed pre-trade gates. Do not activate execution simply because this contract exists.

## 14. OpenAI Plugin migration / Phase 10P

The existing Custom GPT remains the compatibility product until replacement acceptance.

Prepared package:

- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`;
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`;
- `docs/plugin_migration/REGRESSION_SUITE.md`;
- `docs/plugin_migration/SOURCE_ASSESSMENT_2026-09-16.md`;
- `docs/plugin_migration/PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md`.

Target:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only backend`

Do not disable the current Custom GPT or expose a write/trading tool during migration.

## 15. Storage / retention

Latest audit:

`docs/operations/STORAGE_PROVENANCE_AUDIT_2026-09-16_1630Z.md`

- root disk about 20% used;
- research data ~1.47 GB;
- retention timer disabled;
- destructive mode absent;
- state-manifest provenance hashes `5/5 PASS`.

No cleanup activation required.

## 16. External research boundary

Broad market-pattern discovery, self-improving strategies and unconstrained strategy search were delegated to `K_Investigation_Forecast`.

Do **not** reopen that research in K-Trader until the user explicitly reports positive results.

K-Trader v2.2 remains a benchmark/control and prospective evidence stream.

## 17. Resume work order

On the first turn in the new chat:

1. recover this handoff and `docs/CURRENT_STATE.md`;
2. verify production health/read-only invariant;
3. verify current research branch/head;
4. determine the latest fully closed M15 cutoff;
5. use pipeline v2 with prior outcomes `20260916T163000Z`;
6. inspect whether any of the four current unresolved primary families resolved;
7. preserve prereg confirmation separation;
8. update diagnostics/checkpoint only on material state change;
9. do not open holdout, activate Phase 12, retune v2.2 or deploy production without an explicit new decision.

## 18. Transition readiness

This handoff is intentionally created after:

- 16:30Z causal resolution;
- resolver continuity validation;
- pipeline v2 acceptance;
- portfolio-risk simulation;
- Phase 11G closure audit;
- execution compatibility design;
- Plugin migration blueprint;
- storage/provenance audit.

The project is therefore at a clean transition boundary for a new chat.
