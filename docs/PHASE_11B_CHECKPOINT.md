# Phase 11B Checkpoint - Provider History / Signal Outcomes

Date: 2026-08-23

Status: VERIFIED.

## Implemented

- versioned provider-history JSONL dataset contract `ktrader.history.v1`;
- exact canonical candle-content SHA-256 digest;
- closed/contiguous/single-provider validation;
- latest provider-native closed-history page collector through the existing `MarketDataProvider` contract;
- public-data history export utility for Binance USD-M and Bybit Linear;
- conservative no-lookahead signal-outcome evaluator;
- explicit OHLC intrabar ambiguity handling;
- deterministic `TradingDecision` fingerprint;
- separate SQLite outcome persistence/upsert;
- binary-resolved WIN/LOSS sample extraction without probability calculation.

## Outcome states

- `PENDING_ENTRY`;
- `OPEN`;
- `WIN`;
- `LOSS`;
- `AMBIGUOUS`;
- `EXPIRED_NO_ENTRY`;
- `EXPIRED_OPEN`;
- `NOT_ELIGIBLE`.

## Guardrails

- Setup Score remains rule-based, not probability.
- `estimated_probability` remains null/N/A.
- `NO_TRADE` cannot become a calibration sample.
- Cross-provider future candles are rejected.
- Gapped outcome histories are rejected.
- Same-candle entry/exit ordering is never guessed.
- Entry plus Stop/Target in one OHLC candle is `AMBIGUOUS`.
- Stop plus Target in one post-entry OHLC candle is `AMBIGUOUS`.
- Ambiguous/unresolved observations are excluded from `list_binary_resolved()`.
- `outcome_r` is planned geometry touch outcome, not realized broker PnL; fees, funding, slippage and execution quality are not modeled in Phase 11B.
- No universal holding horizon is invented; `horizon_end` is explicit and optional.
- Deep provider history pagination is deferred; current exports are bounded to one provider-native page while the versioned dataset contract remains reusable.

## Verification evidence

PR #5 (`Phase 11B provider history and signal outcomes`) passed GitHub Actions CI run:

`32650220382`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **121 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #5 was squash-merged to `main` as:

`0b201a5112dca057e3071ef878d8acc6653ab994`

## Calibration status

Phase 11B provides data and outcome plumbing only. It does not introduce win probability.

Before any `Estimated Probability` is enabled, a later approved phase must define sample-size requirements, time-separated train/validation/test sets, provider/symbol/regime stratification, listing/survivorship bias policy, ambiguous/unresolved handling, transaction-cost assumptions, confidence intervals/calibration metrics and out-of-sample validation.

Until that work is complete, `estimated_probability` remains null/N/A.

## Remaining hardening

- deep multi-page provider history collection;
- reproducible multi-timeframe historical replay bundles;
- provider-recorded regression fixtures captured from public APIs;
- signal-outcome studies with approved explicit horizons;
- metrics/backup/recovery/runtime failure hardening.
