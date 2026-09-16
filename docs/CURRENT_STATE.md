# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T20:15:00Z`.

Current checkpoint:
`docs/checkpoints/2026-09-16_2015Z_PROSPECTIVE_MATERIAL_UPDATE.md`

Authoritative new-chat handoff remains:
`docs/operations/K_TRADER_NEW_CHAT_HANDOFF_2026-09-16_1930Z.md`

## Production invariant

- accepted/deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- host `k-trader-prod-vnic`
- health last verified `ok`
- mode `read_only`
- provider `binance_usdm`
- scanner `DEGRADED` remains known fail-closed/history-readiness condition
- no production deploy, restart, privilege expansion or trading action performed
- public API remains GET-only

## Research boundary

- branch `research-strategy-benchmark-v1`
- canonical main baseline `4919fea4397d34898ddc7d4215ea898e6caea815`
- frozen candidate `candidate_rule_set_v2_2`
- frozen harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`
- resolver v1.3
- ledger v1.2: first valid event-key payload immutable; later conflicting recomputations audit-only
- prereg boundary `2026-09-16T13:00:00Z`
- holdout `UNTOUCHED / NOT AUTHORIZED`
- Phase 11G **ACTIVE**
- Phase 12 **FUTURE / NOT ACTIVE**

No frozen rule, RR, 32-M15 max hold, risk gate, side filter or production authorization changed.

## Causal continuation since 19:30Z project sync

- `19:45Z` PASS — new confirmation family `ADAUSDT SHORT` at entry `19:30Z`, unresolved
- `20:00Z` PASS — no sample/outcome change
- `20:15Z` PASS — material outcome change: the `ADAUSDT SHORT` family resolved `STOP`, `-1.076370735924895R`

## Latest accepted prospective state — 20:15Z

Run root:
`/data/research/phase11g/v2_2_shadow_20260916T201500Z`

Pipeline manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T201500Z_execute.json`

SHA256: `fb1d02c4d148991f54f85571565b6cd312416e98d0dc3c9da16b866d4a0ab8a0`

State manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T201500Z.json`

SHA256: `b0925fcd433ef5c45065a50000b7fc08a15b032f4cf6e7c2a6d3be5eb633a738`

State:

- status `PASS`
- panel `19/19`
- eligible observations `62`
- unique primary families `48`
- resolved primary families `48`
- unresolved primary families `0`
- current open families `0`
- wins/losses `13/35`
- win rate `27.08333333333333%`
- expectancy `-0.6088593884101355R`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`
- confirmation families `4`
- confirmation resolved `4`
- confirmation unresolved `0`
- holdout false
- production action false

Resolver summary SHA256: `d70ab95cefc36683495cebeea73debec4c79f1c6a4d21be137bb478f3ac99163`
Evidence tracker SHA256: `af16276eb4559c0731d3c54500ed303861b0762c0e441e30b60205eb72c3cef5`
Portfolio-risk report SHA256: `178391eae9fb612d214df85c0b76cddac515608f6608753f8444c1ae8c1b5466`

## Confirmation sample

- discovery primary families `44`
- confirmation primary families `4`
- confirmation resolved `4`
- all confirmation families are `SHORT / REST`
- latest confirmation family: `ADAUSDT SHORT`, entry `19:30Z`, `STOP`, `-1.076370735924895R`
- chronology/governance invariants PASS

The confirmation cohort remains too small to authorize strategy changes.

## Portfolio risk

- current open families `0`
- observed max concurrent all `8`
- observed max concurrent SHORT `8`
- largest correlated cohort `4`
- diagnostic only; no production cap selected or enforced

## Phase 11G closure state

Path A:

- resolved primary families `48/100`
- shortfall `52`
- confirmation sample `4/4 resolved`, still underpowered

Path B has not been selected. Phase 11G remains **ACTIVE**.

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

## Next work order

1. Continue causal pipeline v2 at next fully closed M15 cutoff `2026-09-16T20:30:00Z` using prior outcomes `.../20260916T201500Z`.
2. Preserve ledger v1.2 immutability, resolver v1.3 guards and prereg boundary.
3. Refresh checkpoint only on material sample/governance change or explicit synchronization.
4. Do not retune frozen v2.2, open holdout, activate Phase 12 or mutate production without separate authorization.
5. Continue Phase 10P preparation without disabling the existing Custom GPT before replacement acceptance.
