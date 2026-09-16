# Prospective v2.2 Offline Incremental Resolver v1.1

Date: 2026-09-16  
Status: **ACCEPTED RESEARCH TOOL / FAIL-CLOSED / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED**

## Why v1.1 exists

The v1 offline resolver assumed that every ledger observation could be recomputed from the newest `400`-M15 snapshot. After the extended soak, accepted early observations had aged out of that rolling window. v1 therefore reached `SOURCE_ENTRY_BAR_UNAVAILABLE` and then raised `KeyError: target` before prior terminal outcomes could be reused.

v1.1 does not change frozen-v2.2 trading semantics. It changes only outcome-resolution continuity.

## Semantics preserved

- earliest eligible observation is the immutable primary family representative;
- target `3R`;
- max hold `32` M15 bars / `8h`;
- STOP-first same-bar handling;
- fee `5 bps` per side;
- execution slippage `2 bps` per side;
- official Binance USD-M funding;
- holdout unopened;
- production action false.

## Accepted-prior rule

A previously accepted **resolved** observation is terminal and immutable when stable identity matches:

`setup_family_id + symbol + side + entry_time`

Entry/stop prices must also pass narrow numerical guards:

- absolute tolerance `2e-9`;
- relative tolerance `1e-12`.

The tolerance was chosen only to absorb the observed accepted VTHOUSDT stop representation drift, whose maximum absolute delta was `1.0704848964725178e-9`. A larger mismatch fails closed.

When the source entry bar is still available in the newest bundle, v1.1 recomputes the terminal path and requires terminal state and exit timestamp to match the accepted prior outcome. When the source entry bar has aged out, the accepted terminal row is reused as immutable evidence.

## New-observation rule

An observation without a matching accepted resolved prior row must be recomputed from the current causal bundle.

- if its source entry bar is unavailable, v1.1 fails closed;
- if unresolved, it remains `CENSORED_OPEN`;
- if newly resolved, economics are computed only from a persisted funding snapshot generated from the official Binance USD-M funding endpoint;
- the final resolver performs no network access.

## Required inputs

Runner:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_1.py`

Required arguments:

- `--as-of <UTC>`;
- `--prior-outcomes <accepted outcome directory>`;
- `--funding-snapshot-root <funding_offline_v1 directory>`.

Default output root:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1/`

## Post-soak acceptance fixture

Cutoff: `2026-09-16T09:45:00Z`.

- eligible observations: `56`;
- unique families: `43`;
- previously accepted terminal observations reused: `17`;
- prior terminal paths revalidated from current bundles: `11`;
- prior accepted rows whose source entry bars aged out: `6`;
- new resolved observations: `32`;
- new unresolved observations: `7`;
- resolved primary families: `39`;
- unresolved primary families: `4`;
- wins / losses: `9 / 30`;
- resolved win rate: `23.076923%`;
- resolved expectancy: `-0.6482720083734612R`;
- evidence status: `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- holdout opened: `false`;
- production action: `false`;
- network used by final resolver: `false`.

All `12` primary families accepted at the prior `2026-09-13T13:00:00Z` checkpoint were preserved exactly in terminal state, exit and realized R.

Artifact hashes:

- funding snapshot summary: `d793079cb3fa629b53fb8bff8e198117229e9ac45e923d4dfa836a2bcac322ea`;
- observations: `e39e4d29c4b08fb823c3a41d1ac807c693dd1bc8c10e6fe116059eb7c453e9c0`;
- families: `070ab48b4838b9bdc81041b71a268f01fba2100ad04679e8b3916adfa75eda2f`;
- summary: `cd4bc59764ff15e4f9bc012979fb2d40436ae4d3ccb721686b8daaab423cba25`.

## Governance

Crossing `30` resolved prospective families changes evidence status to **diagnostics only**. It does not authorize in-place retuning, LONG/SHORT filtering, RR/max-hold/risk-gate changes, symbol filtering, holdout access, production deployment, or Phase 12 activation.
