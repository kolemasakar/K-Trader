# Prospective v2.2 Offline Incremental Resolver v1

Date: 2026-09-13
Status: RESEARCH TOOL / FAIL-CLOSED / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED

## Purpose

Remove the live Binance HTTP dependency from prospective outcome resolution while preserving the frozen v2.2 outcome semantics.

## Canonical semantics retained

- earliest eligible observation is the immutable primary family representative;
- target = 3R;
- max hold = 32 M15 bars;
- STOP-first same-bar handling;
- fee = 5 bps per side;
- execution slippage = 2 bps per side;
- no holdout access;
- no production action.

## Incremental cache rule

The resolver may reuse an already resolved observation from the previous canonical resolver output only when the immutable identity tuple matches exactly:

`setup_family_id + symbol + side + entry_time + entry_price + stop_price`.

The current candle path is recomputed locally. Reuse is accepted only if terminal state and exit timestamp match the cached canonical result.

This preserves the previously calculated funding/fee/slippage economics for already resolved observations without any new network request.

## Fail-closed rule

If an observation becomes resolved and no matching prior canonical resolved row exists, the offline incremental resolver aborts with:

`NEWLY_RESOLVED_REQUIRES_FUNDING_SNAPSHOT`

It must not assume zero funding.

A separate exporter is provided:

`research/strategy_benchmark_v1/export_prospective_funding_snapshot_v1.py`

Funding source remains Binance official USD-M `/fapi/v1/fundingRate`.

## Artifacts

Resolver:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1.py`

Resolver commit:

`fb876e97538544c1366fb06f332512f6623aef75`

Funding exporter commit:

`cef5402a8edfabd7c3beb7ab7ccb89aeb4ae95c4`

Offline outputs are written under:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1/<ASOF>/`

They do not overwrite the previous canonical online resolver output.

## Current 12:00Z applicability

The 2026-09-13T12:00:00Z read-only price-path audit established that the three currently open VTHOUSDT primary families remain unresolved. Therefore no new realized outcome requires funding at that cutoff, and the offline incremental resolver can resolve the complete 12-family state solely by reusing the nine previously resolved canonical rows plus locally recomputing the three open paths.

The expected family state before execution is:

- unique families: 12;
- resolved primary families: 9;
- unresolved primary families: 3;
- resolved wins/losses: 1 / 8;
- resolved expectancy remains unchanged from the last canonical resolver state.

These values remain a read-only expectation until the offline resolver artifact is actually produced.
