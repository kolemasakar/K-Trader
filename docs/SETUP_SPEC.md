# Setup Specification v1.0

## Scope

Phase 7 converts confirmed market context/evidence into deterministic setup candidates and final read-only trade decisions.

It does not place orders.

## Canonical setup types

- `TRAP_VSA_CONFIRMATION`
- `VSA_LEVEL_CONFIRMATION`
- `TRAP_LEVEL_CONFIRMATION`

A setup candidate is keyed by:

- provider;
- symbol;
- direction;
- primary confirmed level.

Trap/VSA evidence may be combined only when it references the same provider, symbol, direction and primary level.

## Primary level rule

Tradable setup requires:

- level status `CONFIRMED` or `MIRROR`;
- level strength `STRONG`;
- HTF regime aligned with setup direction.

FLOATING, BROKEN, INVALIDATED, MODERATE or WEAK primary levels cannot validate a tradable setup.

## Confirmation trigger

The setup trigger is the latest confirmed evidence bar among the selected trap/VSA evidence.

VSA confirmation retains the Phase 6 rule:

- LONG: a following closed bar closes above the VSA source-bar high;
- SHORT: a following closed bar closes below the VSA source-bar low.

Trap confirmation uses the Phase 6 `confirmation_time`.

If no confirmed trigger bar exists, setup is rejected.

## Luft

Canonical v1 baseline:

`luft = max(1 price tick, 0.02 * ATR14)`

Luft is rounded outward to the instrument tick.

## Entry

LONG:

`Entry = confirmation_bar.high + luft`, rounded upward to tick.

SHORT:

`Entry = confirmation_bar.low - luft`, rounded downward to tick.

This makes Entry a confirmation trigger rather than an assumed fill at a historical close.

## Stop

Stop is structural.

LONG:

- base anchor = lower boundary of primary support;
- when confirmed trap exists, use the lower of level boundary and sweep extreme;
- `SL = anchor - luft`, rounded downward.

SHORT:

- base anchor = upper boundary of primary resistance;
- when confirmed trap exists, use the higher of level boundary and sweep extreme;
- `SL = anchor + luft`, rounded upward.

No arbitrary percent stop is allowed.

## Structural target

Target is the nearest active confirmed/mirror opposing level beyond Entry.

LONG:

- nearest resistance with lower boundary above Entry;
- `TP = resistance.lower - luft`, rounded downward.

SHORT:

- nearest support with upper boundary below Entry;
- `TP = support.upper + luft`, rounded upward.

If no structural target exists, result is `NO_TRADE`.

K-Trader v1 does not fabricate a synthetic 3R target merely to satisfy RR.

## RR

LONG:

`RR = (TP - Entry) / (Entry - SL)`

SHORT:

`RR = (Entry - TP) / (SL - Entry)`

`RR < 3` is a hard reject.

## ATR-used origin

ATR-used measures how much of normal daily movement would already be consumed when the proposed Entry is triggered.

Daily range context is built from confirmed closed 5m candles beginning exactly at `00:00 UTC` for the current UTC day.

LONG:

`move_distance = Entry - observed_UTC_day_low`

SHORT:

`move_distance = observed_UTC_day_high - Entry`

Then:

`ATR_used_pct = move_distance / ATR5D * 100`

- <40% -> STRONG
- 40..80% -> ACCEPTABLE
- >80% -> hard reject

Partial-day context that does not start at 00:00 UTC is rejected rather than extrapolated.

## Position size and risk

Position size remains optional.

It is calculated only if caller supplies confirmed:

- balance;
- risk-per-trade percent;
- quantity value per one price unit;
- quantity step.

Formula:

`risk_amount = balance * risk_pct / 100`

`risk_per_quantity = abs(Entry-SL) * quantity_value_per_price_unit`

`quantity = floor(risk_amount / risk_per_quantity to quantity_step)`

If risk context is absent:

- Position size = N/A
- Risk amount = N/A

No account balance is inferred.

## Final eligibility

A candidate emits LONG/SHORT only when:

- no hard reject exists;
- grade is A or A+.

Otherwise it emits `NO_TRADE` with reason codes.
