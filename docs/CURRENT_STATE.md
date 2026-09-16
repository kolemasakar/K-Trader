# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T19:30:00Z`.

Current checkpoint:

`docs/checkpoints/2026-09-16_1930Z_PROJECT_SYNC.md`

Current Phase 11G audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`

Current new-chat handoff:

`docs/operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`

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
- Plugin typed tool surface: `docs/plugin_migration/MCP_TOOL_SURFACE_V1.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime after the 19:30Z cycle:

- host `k-trader-prod-vnic`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage
- no production deploy, restart, privilege expansion or trading action performed
- public API remains GET-only

The 2026-09-16 SentinelX hub reconnect incident is closed as recovered. Remote connectivity is operational.

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
- `19:00Z` — capture/funding PASS, original resolver attempt failed closed on prior-stop identity drift; ledger v1.2 infrastructure/causality correction accepted; downstream recovery PASS
- `19:15Z` PASS under ledger v1.2
- `19:30Z` PASS under ledger v1.2

No eligible-family or outcome change occurred at 19:15Z or 19:30Z.

## Latest accepted prospective state — 19:30Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T193000Z`

Pipeline v2 execute manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T193000Z_execute.json`

SHA256:

`1ad3819eed6770c802a972b5c590cf7b3d2eff9426200c767738b89d027933ce`

State manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T193000Z.json`

SHA256:

`e3b97d383d8b23d9f1fdd5e6677c36325a6d414db1148f1d4eeb158a4ebeb801`

State:

- status `PASS`
- panel `19/19`
- eligible observations `61`
- unique primary families `47`
- resolved primary families `47`
- unresolved primary families `0`
- current open families `0`
- wins/losses `13/34`
- win rate `27.65957446808511%`
- expectancy `-0.5989123384630131R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`
- confirmation families `3`
- confirmation resolved `3`
- confirmation unresolved `0`
- holdout false
- production action false

Capture:

- status `VALID_SHADOW_CAPTURE`
- current-capture eligible setups `49`
- event count `299`
- signal bars evaluated `6574`
- bundle export summary SHA256 `eeb78e0fdf151f2f8e83a3e488731b4840e10a0dd860f8564da3e28dad490f17`
- event file SHA256 `c3a0000331fe18ce2e9c57d5381594db7382b3affd53091ccc9051b7cc2f0b81`
- shadow summary SHA256 `9b647eb6b89be5595bd64eedb7cb891e5c48f8524f1b0edaf5fd77f16b37e6e8`

Funding:

- symbols `19`
- records `1878`
- summary SHA256 `b7341bd6bf8006bf62d73bc6a0ace2e4aabe7c647f48b2144ea2b1d647ab7aeb`

## Prospective ledger v1.2

Canonical rule:

> first valid event-key payload is immutable; later conflicting recomputations are audit-only and never rewrite causal history.

19:30Z current state:

- schema `ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2`
- first-seen payload immutable `true`
- raw duplicate occurrences `6587`
- conflicting duplicate occurrences `6587`
- conflicting event keys `393`
- deduplicated events `394`
- eligible setups/observations `61`
- unique eligible primary families `47`
- ledger event-set SHA256 `8d0801da0f03ca7d8f716782f57775c4cfa7993f2164efd94027734dda84e747`
- ledger summary SHA256 referenced by the 19:30 state manifest: `55cbfb6053f6c77dcad22031d6a1ee7779866ddf75c2261dce9746e610152675`

The extra deduplicated event added by 19:30Z is rejected and does not change the eligible prospective family sample.

The pre-v1.2 ledger snapshot remains preserved under:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/ledger_snapshots/20260916T190000Z_pre_v1_2/`

Resolver v1.3 guard thresholds were not changed.

## Resolver v1.3 — accepted 19:30Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T193000Z`

Summary SHA256:

`25bd1ee7af4095ce84a24d57222fede1d806528f75a77a1510480f830948e3ae`

Continuity:

- prior terminal reuse `61`
- current-path revalidated `51`
- aged-out/source-window-expired accepted terminals `10`
- max prior entry delta `0.0`
- max prior stop delta `3.809370596741246e-10`
- network false
- holdout false
- production false

Do not use obsolete standalone `/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`; use repository pipeline v2 / canonical staged runtime under `/tmp/ktrader-runtime-v2/`.

## Material sample state

The four primary families resolved at 18:15Z remain terminal:

- TRUMPUSDT SHORT `12:30Z` -> `STOP`, `-1.0660070957569756R` — discovery
- ADAUSDT SHORT `13:15Z` -> `STOP`, `-1.0833591484214327R` — confirmation
- DOGEUSDT SHORT `13:15Z` -> `STOP`, `-1.075440314509089R` — confirmation
- ADAUSDT SHORT `15:00Z` -> `STOP`, `-1.1028235346941972R` — confirmation

No subsequent eligible family or terminal outcome has been added through 19:30Z.

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

19:30Z evidence tracker SHA256:

`1a561d280720c8dbb9d6167ed4786be456c714bb1ef2c65bc339a1d10e8f7800`

Counts:

- discovery primary families `44`
- confirmation primary families `3`
- confirmation resolved `3`
- confirmation unresolved `0`
- all confirmation families are `SHORT / REST`
- chronology/governance invariants PASS

The confirmation cohort remains too small to authorize strategy changes.

## Portfolio risk

19:30Z report SHA256:

`270e90ad220d5b09ba32dad9c83e69ed22374f6692bc778756a8e629d96a83aa`

Observed:

- current open families `0`
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`

Portfolio caps remain risk controls, not an alpha repair. No production cap selected.

## Provenance

All five source hashes referenced by the 19:30Z state manifest were independently recomputed: `5/5 PASS`, `0` mismatches.

## Phase 11G closure state

Audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1930Z.md`

Path A:

- resolved primary families `47/100`
- shortfall `53`
- confirmation sample `3/3 resolved`, still underpowered

Path B has not been selected by the user.

Therefore Phase 11G remains ACTIVE.

## OpenAI product migration — Phase 10P

The Custom GPT remains the legacy compatibility wrapper until replacement acceptance.

Prepared migration package includes:

- `docs/plugin_migration/K_TRADER_SKILL_DRAFT.md`
- `docs/plugin_migration/INTEGRATION_CONTRACT_V1.md`
- `docs/plugin_migration/REGRESSION_SUITE.md`
- `docs/plugin_migration/PLUGIN_IMPLEMENTATION_BLUEPRINT_V1.md`
- `docs/plugin_migration/ACCOUNT_SURFACE_PRECHECK_2026-09-16.md`
- `docs/plugin_migration/MCP_TOOL_SURFACE_V1.md`

The typed surface defines all eight canonical read-only capabilities and explicit auth/error/fail-closed semantics. No write/order/account/generic-proxy capability is authorized.

Target architecture remains:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only K-Trader backend`

Do not cut over until product-side integration/auth/permissions/regression/sharing acceptance passes.

## Next work order

1. Verify production health/read-only invariant and research branch/head.
2. Continue causal prospective collection with pipeline v2, resolver v1.3 and ledger v1.2 at the latest fully closed M15 cutoff.
3. Immediate resume point is `2026-09-16T19:45:00Z` with prior outcomes `/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T193000Z`.
4. Preserve prereg boundary `2026-09-16T13:00:00Z` and confirmation/discovery separation.
5. Refresh diagnostics/checkpoint on material sample/governance change or explicit project synchronization.
6. Keep frozen v2.2, resolver guard thresholds, holdout, production read-only state and Phase 12 unchanged.
7. Continue Phase 10P preparation without disabling the existing Custom GPT before replacement acceptance.
8. Do not reopen broad `K_Investigation_Forecast` strategy discovery until the user explicitly returns positive results.
