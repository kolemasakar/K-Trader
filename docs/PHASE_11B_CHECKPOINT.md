# Phase 11B Checkpoint - Provider History / Signal Outcomes

Date: 2026-08-23

Status: IMPLEMENTED / PR CI VERIFICATION PENDING.

## Implemented

- versioned provider-history JSONL dataset contract;
- exact candle-content SHA-256 digest;
- closed/contiguous/single-provider validation;
- latest provider-native closed-history page collector;
- public-data history export utility;
- conservative no-lookahead signal-outcome evaluator;
- explicit OHLC intrabar ambiguity handling;
- deterministic TradingDecision fingerprint;
- SQLite outcome persistence/upsert;
- binary-resolved WIN/LOSS sample extraction without probability calculation.

## Guardrails

- Setup Score remains rule-based, not probability.
- `estimated_probability` remains null/N/A.
- `NO_TRADE` cannot become a calibration sample.
- Cross-provider future candles are rejected.
- Gapped outcome histories are rejected.
- Same-candle entry/exit ordering is never guessed.
- `outcome_r` is planned geometry touch outcome, not realized PnL.
- Deep provider history pagination is deferred; current exports are bounded to one provider-native page.

## Verification

Repository-wide PR CI pending.
