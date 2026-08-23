# Trading Engine Specification v1.1

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

## 1. Market regime

Consume Phase 5 `MarketStructureSnapshot`.

Canonical per-timeframe regime:

- HH + HL structure plus `close > MA50 > MA200` -> BULLISH;
- LH + LL structure plus `close < MA50 < MA200` -> BEARISH;
- range/transition structure plus neutral MA -> RANGE;
- otherwise MIXED.

Canonical HTF precedence:

1. agreeing directional `1d + 4h` wins;
2. if D1 is non-directional, agreeing directional `4h + 1h` may define direction;
3. all RANGE -> RANGE;
4. otherwise MIXED.

MA50/MA200 confirm structure; they are not independent signals.

## 2. Liquidity

Consume normalized liquidity rank/score and hard spread/liquidity filters from `LIQUIDITY_SPEC.md`.

## 3. Session

Consume DST-aware session context from `MARKET_STRUCTURE_SPEC.md`.

Crypto is 24/7: session is context, not a market-open permission. Phase 5 provides active session labels/overlap only. Any future scoring weight must be explicitly versioned in Phase 7.

## 4. Trap

Consume deterministic trap state from `TRAP_SPEC.md`.

## 5. MTF levels

Consume active confirmed levels/zones from `LEVELS_SPEC.md`.

FLOATING, BROKEN and INVALIDATED levels cannot independently validate a trade. MIRROR becomes active only after the defined retest/confirmation transition.

Canonical HTF level priority:

`1d > 4h > 1h > 15m > 5m`

## 6. Strength

Phase 5 directional strength is evidence count, not probability and not Setup Score:

- structure agreement;
- MA agreement;
- relative-volume participation >= configured threshold.

3 -> STRONG, 2 -> MODERATE, <=1 -> WEAK. RANGE -> NEUTRAL.

Phase 7 will define how strength affects Setup Score; no implicit weight is allowed before then.

## 7. Setup Score

Use `SCORING_SPEC.md`. Score is not probability.

## 8. ATR

Use ATR14/ATR5D/ATR-used from `ATR_SPEC.md`. ATR used > 80% is a hard reject.

The setup-specific origin for ATR-used `move_distance` must be defined in Phase 7 before tradable output.

## 9. Setup type

Setup type must be explicit and rule-backed, not free-form narrative.

## 10. Stop

Stop must be structurally justified by the validated setup and instrument tick rules. No arbitrary stop may be fabricated.

## 11. Entry + luft

Entry and optional luft/buffer are engine outputs tied to setup structure. Exact luft algorithm is deferred until setup rules are specified and tested.

## 12. Position size

Calculate only with confirmed account balance, risk-per-trade and instrument specifications. Otherwise N/A.

## 13. Risk

Expose RR and, when prerequisites exist, monetary/percent risk. RR < 3 is a hard reject.

## 14. Rating

A+/A/B/C. Only A+/A may produce LONG/SHORT signal; B/C returns NO TRADE.

## Fail-closed rule

Missing confirmed inputs, stale data, unresolved provider integrity, insufficient structural history, conflicting HTF context or failed hard filter results in NO TRADE/REJECT with reason codes.
