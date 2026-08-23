# Phase 11D Checkpoint - Full-engine Historical Replay / Outcome Studies

Date: 2026-08-23

Status: VERIFIED.

## Implemented

- one shared `analyze_candle_snapshot()` path used by live `EngineSymbolAnalyzer` and historical replay;
- chronological replay across `ktrader.mtf_bundle.v1` snapshots with explicit `as_of` cutoffs;
- timestamped replay-liquidity context schema `ktrader.replay_context.v1`;
- fail-closed handling when historical liquidity rank/universe size/score is missing or stale;
- deterministic replay-study schema `ktrader.replay_study.v1` and study digest;
- deterministic `TradingDecision` audit IDs through Phase 11B fingerprints;
- separate stable setup-geometry key to deduplicate unchanged tradable setups across consecutive cutoffs;
- Phase 11B conservative future-candle outcome evaluation and optional SQLite persistence;
- explicit optional outcome horizon in setup-timeframe bars;
- JSONL study artifact containing all selected best decisions plus first outcome per unique tradable setup;
- operator utility `scripts/run_replay_study.py`.

## Methodological guardrails

A five-timeframe OHLCV bundle alone is not sufficient to reproduce the live Setup Score because live scoring also uses liquidity rank, universe size and liquidity score.

Phase 11D therefore does not fabricate historical market-universe context. Each replay cutoff requires a confirmed timestamped liquidity context point no later than that cutoff and within the configured maximum context age. Missing or stale context causes that cutoff to be skipped fail-closed.

The replay engine uses the same analysis function as live runtime for:

- history-window trimming/validation;
- freshness;
- ATR14 and ATR5D;
- market structure/levels/sessions;
- Trap/VSA;
- setup discovery;
- Entry/Luft/SL/structural TP geometry;
- RR/ATR-used hard gates;
- Setup Score/grade/TradingDecision.

No historical replay-only trading rules are introduced.

## Signal/outcome identity

`decision_fingerprint()` remains the exact audit identity of one emitted decision and includes its decision time.

`stable_signal_key()` is a separate study identity based on provider, symbol, side, setup type, primary level and Entry/SL/TP geometry. It prevents the same unchanged setup from being counted as a new independent signal on every subsequent 5m cutoff.

Only the first occurrence of a unique tradable setup is passed to Phase 11B outcome evaluation. `NO_TRADE` does not produce a calibration outcome.

## Outcome rules

- outcome bars begin strictly after the decision's last closed bar;
- future bars must remain same provider/symbol and contiguous;
- same-candle Entry + exit ambiguity remains `AMBIGUOUS`;
- same-candle Stop + Target after entry remains `AMBIGUOUS`;
- optional study horizon is explicit; no universal holding period is invented;
- outcome R remains planned geometry touch outcome, not realized broker PnL.

## Probability guardrail

Phase 11D does not calculate or expose win probability.

`Setup Score` remains a deterministic rule score and `estimated_probability` remains null/N/A in decisions and replay-study artifacts.

## Verification evidence

PR #7 (`Phase 11D full-engine historical replay orchestration`) final GitHub Actions CI run:

`32653087172`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **140 passed, 1 dependency deprecation warning**;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

The initial PR gate `32653028353` produced 135 passed / 5 failed. All five failures were caused by one invalid new synthetic OHLC fixture (`low > open`) and were corrected by fixing the test fixture only. Production validation rules were not weakened.

PR #7 was squash-merged to `main` as:

`cb2869bc9d5f56496368920e8b7e43faf9ba3bbd`

## Current limitations / next data work

- historical liquidity/universe context is an explicit study input; automated historical multi-symbol universe capture is not yet implemented;
- real long provider-recorded MTF bundles remain operator-generated artifacts;
- study summaries report outcome counts and binary-resolved sample count but deliberately do not report calibrated probability;
- transaction costs, funding, slippage and execution quality remain outside the current OHLC outcome model.

## Remaining hardening

- historical multi-symbol universe/liquidity context capture and reproducible study cohorts;
- capture/catalogue real-provider MTF bundles plus corresponding liquidity contexts;
- operations hardening: SQLite backup/recovery, disk/log guards, metrics and restart/recovery validation;
- later approved statistical calibration methodology with time-separated out-of-sample validation.
