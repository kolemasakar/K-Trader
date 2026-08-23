# Phase 6 Checkpoint

Date: 2026-08-23

Status: IMPLEMENTATION COMPLETE.

## Implemented

- provider-independent `TrapEvent` evidence contract;
- confirmed/mirror level eligibility for trap detection;
- LONG failed-break sequence at support;
- SHORT failed-break sequence at resistance;
- ATR-scaled minimum break distance;
- RETURNED / CONFIRMED / EXPIRED trap states;
- provider-independent `VSAEvent` evidence contract;
- deterministic raw detection for ND, NS, T, UT, BC, SC and SV;
- previous-20-bar volume/spread baselines excluding the current bar;
- relative volume, relative candle spread and close-location metrics;
- strict HTF directional context;
- confirmed/mirror level location requirement;
- ATR-scaled level-distance qualification;
- next-bar confirmation window;
- same-level confirmed trap confluence attachment;
- RAW / IGNORED / VALID_CONTEXT / CONFIRMED VSA states.

## Canonical trap baseline

- minimum break distance: `0.05 * ATR14`;
- return window: 3 closed bars;
- confirmation window: 2 closed bars;
- LONG confirmation: close above return-bar high;
- SHORT confirmation: close below return-bar low.

## Canonical VSA baseline

- baseline window: previous 20 closed bars;
- narrow spread <= 0.8 relative spread;
- wide spread >= 1.5;
- low volume <= 0.8 relative volume;
- high/climactic volume >= 1.8;
- stopping volume >= 1.5;
- valid level distance <= `0.25 * ATR14` unless bar overlaps the level zone;
- VSA confirmation window: next 2 closed bars.

Exact event geometry is documented in `VSA_SPEC.md`.

## Hard rules

- a raw VSA label never creates LONG/SHORT by itself;
- wrong HTF direction -> IGNORED;
- no confirmed level location -> IGNORED;
- no next-bar confirmation -> VALID_CONTEXT only, not CONFIRMED;
- a break without return/confirmation is not a confirmed trap;
- Phase 6 assigns no Setup Score points and no A/A+/B/C rating.

## Deterministic verification

Local isolated Phase 6 harness:

- 14 tests passed;
- compile validation PASS.

Additional compatibility harness using the Phase 5 `PriceLevel` / `MTFRegimeSnapshot` constructor contracts passed.

Covered cases include:

- confirmed LONG trap;
- confirmed SHORT trap;
- trap expiration without return;
- raw detection of all seven VSA event types;
- bullish VSA confirmation near support;
- HTF mismatch rejection;
- missing confirmed-level rejection;
- valid context waiting for confirmation.

Repository-wide CI remains a Phase 9 acceptance gate.

## Phase boundary

Phase 7 will decide setup types, ATR-used origin, entry/stop/target construction, RR, scoring weights and final A+/A/B/C rating. Phase 6 evidence cannot bypass those rules.
