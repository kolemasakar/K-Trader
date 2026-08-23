# Phase 4 Checkpoint

Date: 2026-08-23

Status: IMPLEMENTATION COMPLETE.

## Implemented

- standard True Range;
- Wilder ATR14;
- D1 ATR5D with same-bar ATR14 abnormal-range reference;
- high abnormal rejection `>= 2 * ATR14`;
- low abnormal rejection `<= 1/3 * ATR14`;
- collection of five valid D1 ranges without replacement/duplication;
- SMA and EMA implementations;
- MA50/200 snapshot with canonical v1 baseline `sma`;
- 20-bar previous-only volume baseline;
- relative base volume;
- optional relative quote volume only when complete;
- VSA candle spread and relative spread;
- generic ATR-used calculation;
- exact ATR-used classification boundaries;
- provider-independent indicator snapshot.

## Important boundary

Phase 4 does not define what market/setup point is the origin of `move_distance` for ATR-used.

That semantic rule belongs to Phase 7. This prevents an arbitrary indicator-layer assumption from becoming a trading rule.

## Deterministic verification

Phase 4 isolated harness:

- 12 tests passed;
- Python compileall PASS.

Covered cases include:

- gap-aware True Range;
- Wilder ATR14;
- abnormal high/low ATR5D rejection;
- no rejected-bar replacement;
- SMA50 and MA50/200;
- EMA seed/update;
- current-bar exclusion from volume baseline;
- missing quote-volume behavior;
- ATR-used 40/80% exact boundary behavior;
- combined indicator snapshot.

Repository-wide CI remains a later Phase 9 acceptance gate.

## Acceptance

Phase 4 implementation exit is satisfied.

Indicators consume only validated closed contiguous candles and are independent of Binance/Bybit-specific payloads.
