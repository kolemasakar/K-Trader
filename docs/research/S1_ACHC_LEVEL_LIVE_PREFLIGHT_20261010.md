# ACHC.us level integration acceptance — 2026-10-10

## Confirmed
- GitHub CI #365 on commit `bf5890450aff4adbfa27c7053b6cfc90cbf09a6a`: **SUCCESS**.
- Production K-Trader container: authoritative D1 corpus exists; new research `scripts/research/gerchik_seven_types_v0_1.py` **not deployed**, so a full real-data seven-type code run is **NOT EXECUTED**.
- Read-only direct D1 diagnostic on `ACHC.us`: 2,175 closed source records, zero malformed OHLC candle geometries, one occurrence of three consecutive equal daily highs or lows. This is only a raw LIMIT-form precheck, **not** an approved Gerchik level: lack of penetration and full classifier confirmation have not been applied. No false review/approval asserted.
- Existing research branch PR #95 contains session-aware D1/W1 conversion, imported PR #94 seven-type detector, runner integration and regression tests. None of these files were applied to production.

## Exact next execution gate
Execute PR #95 research code on an isolated read-only runner with frozen MT4 corpus mounted, preserve metadata, record D1/W1 seven-type result and candidate witnesses, then connect full S1 order generator and A/B execution. Keep `RESEARCH_CANDIDATE` separate from owner-reviewed levels; use broker-wall-clock solely as a chronological coordinate.

This checkpoint is not a trade backtest nor an implementation-complete release gate. No live orders.
