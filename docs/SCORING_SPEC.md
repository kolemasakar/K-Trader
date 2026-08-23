# Scoring Specification v1.0

## Principle

v1 exposes a deterministic `Setup Score` from 0 to 100. It is not a statistical win probability.

## Inputs

Scoring SHALL consume only confirmed outputs from:
- market regime
- liquidity
- session
- trap
- MTF levels
- strength
- ATR state
- setup type
- entry/stop/target/RR validation
- VSA/context confirmation
- data freshness

## Hard rejects

At minimum:
- stale/insufficient data
- RR < 3
- ATR used > 80%
- required confirmation missing
- floating/unconfirmed level used as primary validation
- invalid HTF context

Hard reject overrides numeric score.

## Rating

Allowed grades:
- A+
- A
- B
- C

Only A+ and A may produce a tradable signal. B/C result in NO TRADE.

Exact numeric thresholds and weights SHALL be introduced as versioned configuration with tests before production use. They are intentionally not fabricated in Phase 0.

## Future probability

`Estimated Probability` remains N/A until a calibrated model is built from confirmed historical signals and outcomes.
