# K-Trader Checkpoint — 2026-09-16 20:15Z

Status: **ACCEPTED / MATERIAL SAMPLE UPDATE**

## Scope

Accepted causal continuation through fully closed M15 cutoff `2026-09-16T20:15:00Z` after sequential PASS cycles at 19:45Z, 20:00Z and 20:15Z.

## Invariants

- production deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- production mode `read_only`; no trading action authorized
- frozen candidate `candidate_rule_set_v2_2`
- frozen harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`
- resolver v1.3; ledger v1.2 first-seen immutable
- prereg boundary `2026-09-16T13:00:00Z`
- holdout false / not authorized
- Phase 11G ACTIVE; Phase 12 NOT ACTIVE

## Accepted 20:15Z state

Pipeline manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_pipeline_manifests/pipeline_v2_20260916T201500Z_execute.json`

SHA256: `fb1d02c4d148991f54f85571565b6cd312416e98d0dc3c9da16b866d4a0ab8a0`

State manifest:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T201500Z.json`

SHA256: `b0925fcd433ef5c45065a50000b7fc08a15b032f4cf6e7c2a6d3be5eb633a738`

- status `PASS`
- eligible observations `62`
- unique primary families `48`
- resolved `48`; unresolved `0`
- wins/losses `13/35`
- win rate `27.08333333333333%`
- expectancy `-0.6088593884101355R`
- confirmation families `4/4 resolved`
- current open families `0`
- holdout false
- production action false

Material change: `ADAUSDT SHORT`, entry `2026-09-16T19:30:00Z`, confirmation cohort, resolved at the 20:15Z causal cycle as `STOP`, realized `-1.076370735924895R`.

Resolver summary SHA256: `d70ab95cefc36683495cebeea73debec4c79f1c6a4d21be137bb478f3ac99163`
Evidence report SHA256: `af16276eb4559c0731d3c54500ed303861b0762c0e441e30b60205eb72c3cef5`
Portfolio-risk report SHA256: `178391eae9fb612d214df85c0b76cddac515608f6608753f8444c1ae8c1b5466`

## Phase 11G closure

Path A: `48/100` resolved prospective primary families; shortfall `52`. Confirmation sample is `4/4 resolved` and remains underpowered. Path B not selected. Phase 11G therefore remains **ACTIVE**.

## Resume point

Next causal cutoff: `2026-09-16T20:30:00Z` when fully closed, using prior outcomes:
`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T201500Z`.

Do not retune frozen v2.2, open holdout, activate Phase 12 or mutate production without separate authorization.
