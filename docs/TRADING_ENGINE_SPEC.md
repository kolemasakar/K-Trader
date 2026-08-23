# Trading Engine Specification v1.0

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

Determine directional/range context from confirmed MTF structure and configured HTF trend filters. MA50/MA200 are supporting trend inputs, not independent signals.

Exact HTF precedence and MA rules SHALL be versioned before Phase 5 production use.

## 2. Liquidity

Consume normalized liquidity rank/score and hard spread/liquidity filters from `LIQUIDITY_SPEC.md`.

## 3. Session

Classify current market time using UTC internally and Europe/Kyiv for presentation. Session weighting must be configurable and tested; crypto is 24/7, so session is context rather than market-open permission.

## 4. Trap

Consume deterministic trap state from `TRAP_SPEC.md`.

## 5. MTF levels

Consume confirmed active levels/zones from `LEVELS_SPEC.md`. Floating/unconfirmed primary levels cannot validate a trade.

## 6. Strength

Strength is a deterministic composite of structure/momentum/participation inputs. Exact formula is deferred to a versioned spec update before implementation.

## 7. Setup Score

Use `SCORING_SPEC.md`. Score is not probability.

## 8. ATR

Use ATR14/ATR5D/ATR-used from `ATR_SPEC.md`. ATR used > 80% is a hard reject.

## 9. Setup type

Setup type must be explicit and rule-backed (for example sweep/test/confirmation), not free-form narrative.

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

Missing confirmed inputs, stale data, unresolved provider integrity or failed hard filter results in NO TRADE/REJECT with reason codes.
