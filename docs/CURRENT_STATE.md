# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T19:00:00Z`.

Current checkpoint:

`docs/checkpoints/2026-09-16_1900Z_LEDGER_V1_2_RECOVERY.md`

Current Phase 11G audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1900Z.md`

Ledger v1.2 acceptance:

`docs/research/PROSPECTIVE_LEDGER_V1_2_ACCEPTANCE_2026-09-16.md`

## Core specifications

- resolver: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_3.md`
- preregistration: `docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`
- max-hold semantics: `docs/research/MAX_HOLD_CAUSAL_EVIDENCE_SEMANTICS.md`
- portfolio-risk contract: `docs/research/PORTFOLIO_RISK_RESEARCH_CONTRACT_V1.md`
- pipeline-v2 acceptance: `docs/research/PROSPECTIVE_PIPELINE_V2_ACCEPTANCE.md`
- Phase 11G closure criteria: `docs/research/PHASE_11G_CLOSURE_CRITERIA.md`
- stress economics: `docs/research/PHASE_11G_STRESS_ECONOMICS_BASELINE.md`
- execution compatibility: `docs/architecture/EXECUTION_COMPATIBILITY_CONTRACT_V1.md`
- recovery: `docs/operations/RESEARCH_RECOVERY_RUNBOOK.md`
- Plugin migration: `docs/plugin_migration/README.md`
- Plugin account-surface precheck: `docs/plugin_migration/ACCOUNT_SURFACE_PRECHECK_2026-09-16.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime after 19:00Z recovery:

- host `k-trader-prod-vnic`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage
- no production deploy, restart or trading action performed
- public API remains GET-only

SentinelX hub reconnect incident was handled by `Sentinel-Remote` and closed as recovered. Remote connectivity is operational.

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

## Causal continuation

Accepted sequence after Sentinel recovery:

- `17:15Z` PASS
- `17:30Z` PASS
- `17:45Z` PASS
- `18:00Z` PASS
- `18:15Z` PASS — material sample change
- `18:30Z` PASS
- `18:45Z` PASS
- `19:00Z` capture/funding PASS; resolver v1.3 initially failed closed on prior-stop identity drift; ledger v1.2 causality fix accepted; existing capture/funding reused; resolver and downstream stages recovered PASS

The original failed `19:00Z` execute manifest is retained as evidence. The accepted state is represented by the recovery manifest and current-state manifest below.

## Latest accepted prospective state — 19:00Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T190000Z`

Capture:

- status `VALID_SHADOW_CAPTURE`
- panel `19/19`
- current-capture eligible setups `49`
- event count `298`
- signal bars evaluated `6574`
- bundle export summary SHA256 `562c5a0ac8f90c60892e1833ddaa79326aba621a17bd44b108a79dc789ecb1d7`
- event file SHA256 `dcd5785a52429e1ad595ff81819d43ee272700f919a317e86f101074c7779978`
- shadow summary SHA256 `2629c5b901a989b8b9e3ff7cf80ce9463a7def5d590fa48ce44817fbf4b45b0f`
- holdout false
- production false

Funding:

- symbols `19`
- summary SHA256 `8da69589ff966f0fdc4dfb9872df4f964215d333fa68941fdbe43268cccb127d`

## Prospective ledger v1.2

Canonical ledger rule:

> first valid event-key payload is immutable; later conflicting recomputations are audit-only and never rewrite causal history.

State:

- schema `ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2`
- first-seen payload immutable `true`
- deduplicated events `393`
- eligible observations/setups `61`
- unique eligible primary families `47`
- raw duplicate occurrences `5991`
- conflicting duplicate occurrences `5991`
- conflicting event keys `391`
- ledger event-set SHA256 `de631c72a5cd932b3d7e3df66671d702296dfbbf30514bacc50df9dee2f9edc6`
- ledger summary SHA256 `03eebcd4b09e37e9b42a2ed6d9b3dd4840bcfe7c948c726550f23f2cf3234dce`
- ledger events SHA256 `2644a7781735aa9b5f2e48e858afbcbe6e54f139d2e682f6270bb4c61eeda210`

The previous v1.1 canonical ledger was preserved under:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/ledger_snapshots/20260916T190000Z_pre_v1_2/`

Resolver v1.3 guard thresholds were not changed.

## Resolver v1.3 — accepted 19:00Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T190000Z`

Summary SHA256:

`fc028d68af827487691aa5acb348fe986b324ba53abd6805ee117e4a1ac3d2c2`

State:

- eligible observations `61`
- unique primary families `47`
- resolved primary families `47`
- unresolved primary families `0`
- wins/losses `13/34`
- win rate `27.65957446808511%`
- expectancy `-0.5989123384630131R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`
- prior terminal reuse `61`
- current-path revalidated `51`
- aged-out/source-window-expired accepted terminals `10`
- max prior entry delta `0.0`
- max prior stop delta `3.809370596741246e-10`
- network false
- holdout false
- production false

Canonical resolver recovery rule remains unchanged: do not use obsolete standalone `/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`; use repository pipeline v2 / canonical staged runtime under `/tmp/ktrader-runtime-v2/`.

## Material sample state

The four primary families that were unresolved before `18:15Z` remain resolved by STOP:

- TRUMPUSDT SHORT `12:30Z` -> `STOP`, `-1.0660070957569756R` — discovery
- ADAUSDT SHORT `13:15Z` -> `STOP`, `-1.0833591484214327R` — confirmation
- DOGEUSDT SHORT `13:15Z` -> `STOP`, `-1.075440314509089R` — confirmation
- ADAUSDT SHORT `15:00Z` -> `STOP`, `-1.1028235346941972R` — confirmation

No new sample outcome was introduced by the ledger v1.2 migration.

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

19:00Z evidence tracker SHA256:

`2feada24deeb6909c327c06acee2f814d7298868594e29e3bd845aa26b4da5af`

Counts:

- discovery primary families `44`
- confirmation primary families `3`
- confirmation resolved `3`
- confirmation unresolved `0`
- all confirmation families are `SHORT / REST`
- chronology/governance invariants PASS

The confirmation cohort is fully resolved but remains too small to authorize strategy changes.

## Portfolio risk

19:00Z risk-report SHA256:

`6403fb04638444d28d0e194624bc756f3ce04ea4418d1356e19315cb41d44f05`

Observed:

- current open families `0`
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`

Portfolio caps remain risk controls, not an alpha repair. No production cap selected.

## Pipeline v2 / recovery provenance

Canonical orchestration entry point:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

Original 19:00Z execute attempt failed at resolver and is preserved.

Accepted recovery manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T190000Z_recovery_ledger_v1_2.json`

SHA256:

`f796ecdd2d3456ae6ca727179c12b15e25dbf78bebc21fd3e5a2a29a934a57a4`

Ledger v1.2 regression: PASS.

Pipeline v2 plan/preflight after staging: PASS.

Repository-exact runtime ledger SHA256:

- compatibility entrypoint `165f630b8fec0f55fc71ef24bdbe920e3cd4d464d50cf49f5268174c39bf3df7`
- versioned v1.2 `b9043ae20a7298eb13c40297d101e74494182dc01a1253c1c5c68cd05cbfed27`

## Phase 11G closure state

Audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1900Z.md`

Path A:

- resolved primary families `47/100`
- shortfall `53`
- confirmation sample `3/3 resolved`, still underpowered

Path B has not been selected by the user.

Therefore Phase 11G remains ACTIVE.

## Storage / provenance

Machine state:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T190000Z.json`

SHA256:

`18d9ea1956f9035951c008c06cae0ca363c39fdc89599e1fa37a4c020cc4a077`

All five referenced source hashes independently recomputed with `0` mismatches.

## OpenAI product migration — Phase 10P

The Custom GPT remains the supported legacy compatibility wrapper until replacement acceptance.

Account-surface precheck:

`docs/plugin_migration/ACCOUNT_SURFACE_PRECHECK_2026-09-16.md`

Current session can discover/manage Plugin/App/connector integrations, but no supported repository-to-custom-K-Trader-Plugin creation operation is currently exposed. No third-party plugin was installed or connected during the precheck.

Target architecture remains:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only K-Trader backend`

Do not cut over until Plugin product-side integration/auth/permissions/regression/sharing acceptance passes.

## Next work order

1. Continue causal prospective collection with pipeline v2, resolver v1.3 and ledger v1.2 at fully closed M15 cutoffs.
2. Use `/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T190000Z` as the next prior accepted outcomes state.
3. Preserve prereg boundary `2026-09-16T13:00:00Z` and confirmation/discovery separation.
4. Refresh diagnostics/checkpoint only on material sample or infrastructure-governance change.
5. Keep frozen v2.2, resolver guard thresholds, holdout, production read-only state and Phase 12 unchanged.
6. Continue Phase 10P preparation without disabling the existing Custom GPT before replacement acceptance.
7. Do not reopen broad `K_Investigation_Forecast` strategy discovery until the user explicitly returns positive results.
