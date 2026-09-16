# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T18:30:00Z`.

Current checkpoint:

`docs/checkpoints/2026-09-16_1830Z_PROSPECTIVE_MATERIAL_UPDATE.md`

Current Phase 11G audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1830Z.md`

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

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime:

- host `k-trader-prod-vnic`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage
- no production deploy, restart or trading action performed by current research continuation
- public API remains GET-only

SentinelX hub reconnect incident was handled by `Sentinel-Remote` and closed as recovered. K-Trader causal research resumed from `17:15Z` with prior outcomes `20260916T170000Z` and continued through `18:30Z`.

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

## Causal continuation after recovery

Canonical pipeline v2 cycles:

- `17:15Z` PASS
- `17:30Z` PASS
- `17:45Z` PASS
- `18:00Z` PASS
- `18:15Z` PASS — material sample change
- `18:30Z` PASS — accepted stable state

All cycles used resolver v1.3, the frozen v2.2 candidate, prereg boundary `2026-09-16T13:00:00Z`, holdout false and production false.

## Latest accepted prospective state — 18:30Z

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T183000Z`

Capture:

- status `VALID_SHADOW_CAPTURE`
- panel `19/19`
- current-capture eligible setups `49`
- event count `296`
- signal bars evaluated `6574`
- bundle export summary SHA256 `1313f96ff9ea9dacb19c9590ad44fea01c250bb650ea2bad70f65179e33f662c`
- event file SHA256 `6466ae36bb637adaf5329709c31e996fce706e3e720c043d7fa4229c8714c322`
- shadow summary SHA256 `e7efecddb39da4cbc578154ef9b770e2aaa89fdc9adf41b1f1fefd4e5a6dbd8a`
- holdout false
- production false

Ledger / outcomes state:

- eligible observations `61`
- unique primary families `47`
- resolved primary families `47`
- unresolved primary families `0`
- current open primary families `0`
- wins/losses `13/34`
- win rate `27.659574%`
- expectancy `-0.5989123384630131R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`

Funding:

- symbols `19`
- summary SHA256 `59b18c8d33c190b6a968f1c9ae767c05bc1097c00197f5371d0ccd2e3cdd50b2`

## Resolver v1.3 — accepted 18:30Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T183000Z`

Summary SHA256:

`672dffd2c05793f194b3b3a7c38a90d52326000073f92c38b3a4e6a7e6591b64`

Continuity:

- prior terminal reuse `61`
- current-path revalidated `51`
- aged-out/source-window-expired accepted terminals `10`
- max prior entry delta `0.0`
- max prior stop delta `5.68053737089267e-09`
- network false
- holdout false
- production false

Canonical resolver recovery rule remains unchanged: do not use obsolete standalone `/tmp/prospective_v2_2_outcome_resolver_offline_v1_3.py`; use repository pipeline v2 / canonical staged runtime under `/tmp/ktrader-runtime-v2/`.

## Material resolutions at 18:15Z

All four previously unresolved primary families resolved by STOP:

- TRUMPUSDT SHORT `12:30Z` -> `STOP`, `-1.0660070957569756R` — discovery context
- ADAUSDT SHORT `13:15Z` -> `STOP`, `-1.0833591484214327R` — confirmation
- DOGEUSDT SHORT `13:15Z` -> `STOP`, `-1.075440314509089R` — confirmation
- ADAUSDT SHORT `15:00Z` -> `STOP`, `-1.1028235346941972R` — confirmation

## Diagnostics — 47 resolved

Descriptive SHA256:

`69ac3ff4142be71f86c9db537206cc6e876cfd034c644391d643641867ad5cc8`

Statistical SHA256:

`a4446e873c89d03d5a8f2cf98d0ee65135d4fdcc4b1d38be0b01fde1f8c7527d`

Key governance interpretation:

- overall expectancy is now `-0.5989123384630131R`
- the four newly resolved families are losses by STOP
- exploratory diagnostics remain non-authorizing
- no current result authorizes a frozen-v2.2 retune
- obstacle/VSA diagnostics remain exploratory

## Preregistered confirmation sample

Boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Evidence tracker SHA256:

`e1f6db64913dbff977dc2f93792fcad815ebf319a6d0f298ee66100f551e9a2b`

Counts:

- discovery primary families `44`
- confirmation primary families `3`
- confirmation resolved `3`
- confirmation unresolved `0`
- all confirmation families are `SHORT / REST`
- chronology/governance invariants PASS

The confirmation cohort is now fully resolved but remains too small to authorize strategy changes.

## Portfolio risk

18:30Z risk-report SHA256:

`5fae672e7bc9301ed4ff2713a66586214938e8fe99b7160c98208e6b624eb98a`

Observed:

- current open families `0`
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`

Portfolio caps remain risk controls, not an alpha repair. No production cap selected.

## Prospective pipeline v2

Canonical orchestration entry point:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v2.py`

Stages:

`capture -> funding -> resolver -> post30 -> statistics -> evidence -> portfolio_risk -> state_manifest`

18:30Z execute manifest SHA256:

`564d2a6118b956b260e73b56972a2b876015df94d4a8b8ef4dc8c2bba4734724`

Pipeline v1 remains history/audit only and is not preferred.

## Phase 11G closure state

Audit:

`docs/research/PHASE_11G_CLOSURE_AUDIT_2026-09-16_1830Z.md`

Path A:

- resolved primary families `47/100`
- shortfall `53`
- confirmation sample `3/3 resolved` but still underpowered

Path B has not been selected by the user.

Therefore Phase 11G remains ACTIVE.

## Storage / provenance

Machine state:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T183000Z.json`

SHA256:

`3eab4fa5d94808176db63bdcb5c2d266d01ffe041847612e2c5e0f6ef53b0341`

All five referenced source hashes independently recomputed with `0` mismatches.

## OpenAI product migration — Phase 10P

The Custom GPT remains the supported legacy compatibility wrapper until replacement acceptance.

Target architecture remains:

`K-Trader Plugin -> Skill + App/Connector/MCP -> existing read-only K-Trader backend`

Do not cut over until Plugin product-side integration/auth/permissions/regression/sharing acceptance passes.

## Next work order

1. Continue causal prospective collection with pipeline v2 and resolver v1.3 at fully closed M15 cutoffs.
2. Use `/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T183000Z` as the next prior accepted outcomes state.
3. Preserve prereg boundary `2026-09-16T13:00:00Z` and confirmation/discovery separation.
4. Refresh diagnostics/checkpoint only on material sample change.
5. Keep frozen v2.2, holdout, production read-only state and Phase 12 unchanged.
6. Continue Phase 10P preparation without disabling the existing Custom GPT before replacement acceptance.
7. Do not reopen broad `K_Investigation_Forecast` strategy discovery until the user explicitly returns positive results.
