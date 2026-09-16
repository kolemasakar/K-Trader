# Checkpoint — 2026-09-16 16:15Z

Status: **ACCEPTED**

## Scope

This checkpoint closes the parallel hardening package requested on 2026-09-16 and records the latest causally available frozen-v2.2 prospective state. It also records the architecture adjustment required by OpenAI's announced Custom GPT retirement and Plugin migration.

No frozen strategy rule, holdout state or production trading authorization changed.

## Production safety

Production remains:

- health `ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- container identity `uid=1002(ktrader)`;
- Linux effective/permitted/bounding capabilities all zero;
- Docker socket absent inside container;
- current public API surface GET-only;
- no exchange order credentials observed by environment-name audit;
- no production deploy/restart/order action performed.

Filesystem `/dev/sda1` is approximately 19.1% used by exact byte calculation (20% rounded by `df`), inode use approximately 5%.

## Latest prospective capture — 16:15Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T161500Z`

Capture:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- signal bars evaluated `6574`;
- current-capture eligible setups `49`;
- current-capture unique eligible families `38`;
- event count `299`;
- bundle set SHA256 `b929050728d0a07158f92775746c62ba861d6323fe751ff2e4ee59e7d6bca78a`;
- bundle export summary SHA256 `ec70fdc41024d7fb55f7f922251e735d1ca1f4761aad86cfbac5a4101aa6abdd`;
- event file SHA256 `bcdcbaf3c47496c537a4d01127e4ba4ad16624f6b943cf9ae15931d80c8ef61d`;
- shadow summary SHA256 `a08597e26583516048e1c9e3596ded387e2d5a5bbd171f4795396055bbdc0abb`;
- holdout false;
- production action false.

Ledger:

- eligible observations `61`;
- unique primary families `47`;
- valid snapshots `22`;
- one historical infrastructure-invalid first snapshot remains rejected;
- ledger event-set SHA256 `0fac0e8ed782b37090ca91b3388618724214bc2148c376e9ac580eecc0d8ba5c`.

Funding:

- `1878` records;
- `19` symbols;
- SHA256 `88882f4aa563438ea9723366d7f30c2b596174e8d4ac381960ffcbf1577f29a0`.

## Resolver v1.3 — 16:15Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T161500Z`

Summary SHA256:

`c579ac1684fa6d2f74d970601f69946559619341f9386e6747e3f829a9d0de75`

State:

- unique families `47`;
- resolved primary families `41`;
- unresolved primary families `6`;
- wins/losses `11/30`;
- win rate `26.8293%`;
- expectancy `-0.5902225135899566R`;
- evidence status `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- holdout false;
- production false;
- network used false.

Two discovery-context families resolved since the prior accepted state:

- SUIUSDT SHORT, entry `08:00Z` -> `TIME_EXIT` at `16:00Z`, realized `+0.0991586118R`;
- XRPUSDT SHORT, entry `08:00Z` -> `TIME_EXIT` at `16:00Z`, realized `+0.9843266645R`.

Both are pre-prereg families and do not count toward confirmation evidence.

## Max-hold semantics clarification

Frozen v2.2 holds through 32 M15 bars, then exits at the open of the next bar. The prospective resolver uses closed-bar-only bundles, so it confirms that next-bar open one M15 evidence interval later.

Thus:

- SUI/XRP strategy exit timestamp `16:00Z`; confirmation available at `16:15Z`;
- ADA/DOGE entry `08:15Z` strategy TIME_EXIT timestamp `16:15Z`; confirmation available at `16:30Z` if no earlier STOP/3R.

This is evidence lag, not a strategy/max-hold change.

Canonical clarification:

`docs/research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`

## Confirmation evidence tracker

Preregistered confirmation boundary remains:

`entry_time >= 2026-09-16T13:00:00Z`

Tracker report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_evidence_tracker/20260916T161500Z/report.json`

SHA256:

`92378aaca9c3b60faf5a24cfb6371dcd66aa6f93ec648be1a9ebe019598373a3`

Counts:

- discovery primary families `44`;
- confirmation primary families `3`;
- confirmation resolved `0`;
- confirmation unresolved `3`;
- all three current confirmation families are SHORT/REST;
- H1 LOW resolved `0`;
- confirmation obstacle-inside-1R/3R count `0`;
- chronology/governance invariants PASS.

Confirmation families:

- ADAUSDT SHORT `13:15Z`;
- DOGEUSDT SHORT `13:15Z`;
- ADAUSDT SHORT `15:00Z`.

No preregistered hypothesis can yet be evaluated.

## Post-30 diagnostics

Descriptive SHA256:

`b2ffefbe71352e737e699feeba9ecb50f4d0df716a389e7c6a9a0714eb59f275`

Statistical SHA256:

`b4fdd55d1db88ce33bfe5778d4dc2220b80e1cdb7495cdeb52fba1c16c94ebd7`

Current key metrics:

- overall expectancy `-0.590223R`;
- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.592547R`;
- TIME_EXIT: `15` resolved, `11` wins, expectancy `+0.235991R`;
- STOP: `26` resolved, `0` wins, expectancy `-1.066884R`;
- no listed broad exploratory contrast survives BH adjustment as a retuning authorization;
- no in-place frozen-v2.2 change authorized.

## Portfolio-risk layer

Current unresolved primary families at 16:15Z: `6`, all SHORT.

Current open symbols:

- ADAUSDT x3;
- DOGEUSDT x2;
- TRUMPUSDT x1.

Historical/prospective diagnostic maxima now include:

- max concurrent all `8`;
- max concurrent SHORT `8`;
- largest correlated cohort `4`.

At hypothetical equal 2% risk per family, an 8-family concurrent state corresponds to 16% gross stop-risk; this is a diagnostic exposure calculation, not an approved risk policy.

Canonical contract:

`docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`

## Automation hardening

New components:

- `prospective_evidence_tracker.py`;
- `prospective_portfolio_risk_layer.py`;
- `generate_current_research_state.py`;
- `run_prospective_research_pipeline_v2.py`;
- `test_prospective_research_pipeline_v2.py`;
- `research_storage_growth_diagnostics.py`.

Pipeline v2 stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Properties:

- plan-only default;
- explicit `--execute`;
- fail-closed stage sequencing;
- output collision protection;
- resolver v1.3;
- confirmation-boundary tracking;
- machine-readable state manifest.

Tests:

- v1 pipeline tests `6/6 PASS`;
- v2 pipeline tests `2/2 PASS`;
- current research Python compile PASS.

16:15 machine-readable state:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T161500Z.json`

SHA256:

`348a31f0fbc7735660abab1203a4f25ed566def5ae17366386b9395883fc2d01`

## Storage growth

Research data approximately `1.446 GB`; filesystem approximately 19.1% used.

Scenario planning indicates ~24.09 GB additional data to reach 70% and ~28.82 GB to reach 80%.

Retention timer remains disabled by design. No destructive mode authorized.

Canonical planning doc:

`docs/operations/RESEARCH_STORAGE_GROWTH_2026-09-16.md`

## Production safety / execution compatibility

Audit result: **PASS WITH FUTURE EXECUTION-CONTRACT GAP**.

Current read-only backend/container boundary remains appropriate for Phase 11G. Before any future real execution, a separate versioned exchange/broker execution specification is required for min/max qty, min notional, leverage/margin, position mode, order constraints and idempotency.

Canonical audit:

`docs/operations/PRODUCTION_SAFETY_EXECUTION_COMPATIBILITY_AUDIT_2026-09-16.md`

## Recovery and closure governance

Created:

- `docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`;
- `docs/research/PHASE_11G_CLOSURE_CRITERIA.md`.

Phase 11G closure paths:

- Path A: evidence-complete benchmark at >=100 resolved primary prospective families plus final reproducible report;
- Path B: explicit user decision to terminate v2.2 collection earlier and archive as negative/inconclusive benchmark.

Closure does not itself authorize Phase 12, holdout or production trading.

## OpenAI product-layer migration

OpenAI's announced Custom GPT retirement changes the ChatGPT-facing integration layer.

K-Trader decision:

- current Custom GPT remains working legacy compatibility path until replacement acceptance;
- `custom_gpt/openapi.yaml` is now classified as legacy Custom Action transport;
- durable behavior extracted into a Plugin skill draft;
- target integration is Plugin skill + app/connector, with thin MCP adapter as fallback if needed;
- existing HTTPS read-only backend remains canonical and integration-neutral;
- no order/account capability is added.

Prepared migration package:

- `docs/plugin_migration/README.md`;
- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`;
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`;
- `docs/plugin_migration/REGRESSION_SUITE.md`;
- `docs/plugin_migration/SOURCE_ASSESSMENT_2026-09-16.md`;
- `custom_gpt/LEGACY_MIGRATION_NOTICE_2026-09-16.md`;
- `docs/ROADMAP_ADDENDUM_PLUGIN_MIGRATION_2026-09-16.md`.

New roadmap workstream: **Phase 10P — Plugin Migration**, preparation active, activation pending platform/account migration availability.

Phase 10P is independent of Phase 11G evidence collection.

## Boundaries preserved

- frozen v2.2 unchanged;
- holdout unopened;
- production trading unauthorized;
- K_Investigation_Forecast adaptive strategy-discovery track not reopened;
- disk retention remains dry-run only/timer disabled;
- no sudo/Docker privilege broadening.

## Next causal work

At 16:15Z the remaining early ADA/DOGE discovery families have completed the frozen 32-bar holding interval but their strategy TIME_EXIT at `16:15Z` becomes confirmable from the closed-bar evidence bundle at `16:30Z`.

Next meaningful prospective cycle: `as_of >= 2026-09-16T16:30:00Z`, unless a new causal STOP/3R event is captured first.
