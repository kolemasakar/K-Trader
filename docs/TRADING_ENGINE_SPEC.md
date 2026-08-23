# Trading Engine Specification v1.2

## Mandatory evaluation sequence

Every complete setup evaluation covers:

1. Market regime
2. Liquidity
3. Session
4. Trap
5. MTF levels
6. Strength
7. Setup Score
8. ATR
9. Setup type
10. Stop
11. Entry + luft
12. Position size
13. Risk
14. Rating

The engine is read-only and never places orders.

## 1. Market regime

Consume Phase 5 MTF regime.

Directional setup requires canonical HTF regime equal to setup direction.

MA50/200 remain supporting confirmation, never standalone signals.

Mismatch -> hard reject.

## 2. Liquidity

Consume ranked `UniverseCandidate` context.

Liquidity must be positive and rank/universe size valid.

Rank percentile contributes to Setup Score; invalid liquidity context is a hard reject.

## 3. Session

Consume DST-aware Tokyo/London/New York context.

Crypto is 24/7. Session contributes context points only and can neither independently approve nor reject a trade.

## 4. Trap

Consume confirmed Phase 6 TrapEvent.

If trap evidence is declared by the setup it must match provider, symbol, direction and primary level.

## 5. MTF levels

Tradable primary level must be:

- active `CONFIRMED` or `MIRROR`;
- `STRONG`;
- provider/symbol consistent.

HTF priority remains `1d > 4h > 1h > 15m > 5m` for level-map organization.

## 6. Strength

Use the weaker evidence count of the HTF pair that establishes direction:

- agreeing directional 1d + 4h; or
- when D1 is non-directional, agreeing directional 4h + 1h.

3 -> STRONG, 2 -> MODERATE, otherwise WEAK.

Strength affects score but does not replace HTF regime hard validation.

## 7. Setup Score

Use `SCORING_SPEC.md` v1.1.

Canonical weights sum to 100.

A+ >=90, A >=80, B >=70, C <70.

Score is not probability.

Any hard reject forces grade C and public score <=69 while retaining raw_score for audit.

## 8. ATR

Use ATR14, ATR5D and canonical Phase 7 ATR-used origin from `ATR_SPEC.md` v1.2.

Daily excursion is measured from current UTC-day directional extreme to proposed Entry using confirmed closed 5m bars from 00:00 UTC.

ATR used >80% -> hard reject.

## 9. Setup type

Canonical Phase 7 setup types:

- TRAP_VSA_CONFIRMATION
- VSA_LEVEL_CONFIRMATION
- TRAP_LEVEL_CONFIRMATION

Evidence identity and declared setup type must be consistent.

## 10. Stop

Stop is structural.

For LONG use primary support lower boundary or lower confirmed trap sweep extreme, then subtract luft.

For SHORT use primary resistance upper boundary or higher confirmed trap sweep extreme, then add luft.

Round outward to tick.

## 11. Entry + luft

Canonical luft:

`max(1 price tick, 0.02 * ATR14)`.

LONG Entry = confirmation-bar high + luft, rounded upward.

SHORT Entry = confirmation-bar low - luft, rounded downward.

Target is nearest active confirmed/mirror opposing structural level beyond Entry, with luft applied before the zone.

No structural target -> hard reject.

Synthetic 3R target is prohibited in v1.

## 12. Position size

Calculate only from explicit confirmed RiskContext:

- balance;
- risk-per-trade percent;
- quantity value per one price unit;
- quantity step.

Without those fields -> N/A.

## 13. Risk

RR uses structural Entry/SL/TP.

RR <3 -> hard reject.

If explicit risk context exists, quantity is rounded down to quantity step so planned risk is not exceeded.

## 14. Rating

Only A+/A with no hard rejects emit LONG/SHORT.

B/C or any hard reject emit NO_TRADE.

## Final decision contract

Phase 7 emits `TradingDecision` with:

- source/instrument identity;
- 14-stage context;
- score/grade;
- setup type;
- structural geometry;
- ATR diagnostics;
- optional position/risk;
- reason codes;
- freshness/source timestamps.

Use `SIGNAL_SPEC.md` v1.1 for public field contract.

## Fail-closed rule

Missing confirmed inputs, stale data, mismatched evidence, insufficient UTC-day context, invalid geometry, missing structural target, failed RR/ATR gate or invalid risk context cannot be repaired by narrative inference.
