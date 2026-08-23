# Historical Bootstrap Specification v1.0

## Purpose

Build a validated historical MTF state from one provider before any engine analysis.

Default target bars:

- `1d`: 250
- `4h`: 250
- `1h`: 250
- `15m`: 250
- `5m`: 300

## Per-timeframe algorithm

1. Verify provider supports the canonical interval.
2. Request `target + 1` bars where provider page limits allow, so the current open bar does not reduce closed-history depth.
3. Validate every normalized returned candle.
4. Remove open candles.
5. Require at least the target number of closed bars.
6. Select the latest target closed bars.
7. Require strict chronological and contiguous sequence.
8. Require freshness according to configured policy.
9. Stage the validated interval in memory.

## Atomic MTF rule

No candle is persisted until all requested timeframes pass.

After all timeframes pass, the complete staged snapshot is written with one repository transaction.

If any interval has insufficient bars, invalid OHLCV, wrong UTC boundary, a gap, stale data, provider mismatch or unsupported interval:

- bootstrap status = FAILED;
- no partial MTF candle snapshot is persisted;
- error is recorded in `bootstrap_runs` where possible.

## Provider integrity

One bootstrap uses one `MarketDataProvider` and one matching `NormalizedInstrument`.

Cross-provider history stitching remains forbidden.
