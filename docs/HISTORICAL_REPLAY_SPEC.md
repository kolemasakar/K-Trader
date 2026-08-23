# Historical Replay / Signal Outcome Spec v1.2

## Purpose

Phases 11B-11D provide reproducible provider-recorded historical data, deterministic MTF replay snapshots, conservative signal-outcome tracking and full-engine chronological study orchestration. They do not convert Setup Score into probability.

## Provider history contract

A history dataset is a coherent series from exactly one provider, canonical symbol and timeframe.

Rules:

- only confirmed closed candles;
- chronological and contiguous;
- UTC timestamps;
- no provider mixing or provider fallback inside a dataset;
- Decimal market values serialized as strings;
- source kind `provider`;
- SHA-256 digest over canonical candle content;
- requested bar count and actual time range recorded separately.

Schema version: `ktrader.history.v1`.

The JSONL file starts with one manifest record followed by candle records.

## Historical collection

`collect_provider_history()` remains the single-page compatibility path.

`collect_deep_provider_history()` pages backward through the same provider with an explicit UTC end cursor.

Current provider implementations:

- Binance USD-M: `/fapi/v1/klines` with `endTime`;
- Bybit Linear: `/v5/market/kline` with `end`.

Deep collection rules:

- exact requested closed-bar depth is mandatory;
- pages are deduplicated by candle open time;
- paging cursor must strictly move backward;
- every page preserves provider/symbol/timeframe identity;
- merged history remains contiguous and closed;
- insufficient depth or unsupported pagination fails closed;
- another provider may never fill a missing page.

## MTF replay bundle

Schema version: `ktrader.mtf_bundle.v1`.

A canonical bundle contains exactly `1d/4h/1h/15m/5m`. All datasets share provider ID, canonical symbol, provider-native symbol and one UTC `as_of` cutoff. Any candle closing after `as_of` invalidates the bundle.

The manifest stores per-timeframe candle counts/digests plus one bundle SHA-256. `slice_datasets_asof()` is the canonical no-future-lookahead boundary: it removes all bars not closed by the selected cutoff and can require minimum history per timeframe.

Default operational depths remain:

```text
1d   250
4h   250
1h   250
15m  250
5m   300
```

Deeper research captures may request larger depths.

## Full-engine historical replay

Phase 11D uses one shared pure analysis path:

`analyze_candle_snapshot()`

The live `EngineSymbolAnalyzer` loads its validated SQLite snapshot and calls this function. Historical replay slices the MTF bundle at a historical cutoff and calls the same function. This prevents a separate replay-only implementation of ATR, market structure, Trap/VSA, setup geometry or scoring.

At each accepted cutoff the shared analyzer applies the configured live history windows and runs:

```text
validated MTF snapshot
-> freshness
-> ATR14 / ATR5D
-> structure / levels / sessions
-> Trap / VSA
-> setup discovery
-> Entry / Luft / SL / structural TP
-> RR / ATR-used hard gates
-> Setup Score / Grade
-> TradingDecision
```

Historical replay may not alter scoring weights, RR requirements, ATR-used limits or setup eligibility rules.

## Replay liquidity/universe context

OHLCV history alone cannot reproduce the complete live Setup Score because live scoring also consumes liquidity rank, universe size and liquidity score.

Schema version: `ktrader.replay_context.v1`.

A replay context contains:

- confirmed instrument identity including provider-native symbol and positive price tick;
- strictly chronological liquidity observations;
- observation timestamp;
- liquidity score;
- liquidity rank;
- universe size;
- maximum allowed context age.

For a cutoff `T`, replay may use only the latest context point whose timestamp is `<= T`. If none exists or it is older than the configured maximum age, the cutoff is skipped fail-closed.

Forbidden behavior:

- assuming `rank=1`;
- inventing universe size;
- using a future context point;
- carrying a stale observation indefinitely;
- filling a missing provider context with another exchange.

## Replay study contract

Schema version: `ktrader.replay_study.v1`.

`run_replay_study()` walks the setup timeframe chronologically. For each cutoff it:

- slices the full MTF archive to bars closed at that cutoff;
- verifies minimum live-analysis history;
- resolves a valid timestamped liquidity context point;
- calls the canonical shared snapshot analyzer;
- selects the best `TradingDecision` using normal engine ordering;
- preserves the exact time-specific decision fingerprint for audit;
- optionally evaluates the first occurrence of a unique tradable setup on confirmed future bars;
- optionally persists the outcome through `OutcomeRepository`.

Study output records every selected best decision, while outcome counts are based on unique tradable setups rather than every repeated 5m observation of the same geometry.

## Decision identity vs stable signal identity

`decision_fingerprint()` is the exact audit identity of one emitted decision and includes decision timing fields.

`stable_signal_key()` is a separate study identity based on:

- provider;
- canonical symbol;
- side;
- setup type;
- primary level ID;
- Entry;
- Stop;
- Target.

This prevents unchanged setup geometry from being counted as a new independent signal at every consecutive cutoff while retaining complete time-specific decision audit records.

## Signal outcome contract

Outcome evaluation consumes a previously emitted tradable `TradingDecision` and later confirmed candles from the same provider/symbol.

Eligible decisions require side `LONG`/`SHORT` and confirmed Entry, Stop and Target geometry. `NO_TRADE` and missing geometry never enter calibration samples.

Canonical states:

- `PENDING_ENTRY`;
- `OPEN`;
- `WIN`;
- `LOSS`;
- `AMBIGUOUS`;
- `EXPIRED_NO_ENTRY`;
- `EXPIRED_OPEN`;
- `NOT_ELIGIBLE`.

Future outcome candles must begin strictly after the decision's last closed bar.

## Intrabar ambiguity

OHLC bars do not prove intrabar ordering. Therefore:

- Entry plus Stop/Target in one candle -> `AMBIGUOUS`;
- Stop and Target both touched in one post-entry candle -> `AMBIGUOUS`;
- ambiguous outcomes are excluded from binary WIN/LOSS samples.

No optimistic or pessimistic ordering assumption is allowed.

## Outcome horizon and R

The study does not invent a universal holding period. The horizon is explicit and optional; Phase 11D can express it as a number of setup-timeframe bars.

`outcome_r` remains planned geometry touch outcome, not realized broker PnL:

- target touch -> planned reward/risk multiple;
- stop touch -> `-1R`;
- ambiguous/open/expired/not-eligible -> N/A.

Fees, funding, slippage and execution quality are not modeled by the current OHLC outcome layer.

## Persistence

`OutcomeRepository` stores outcomes separately in SQLite under deterministic decision IDs. Unresolved states may be upserted later to resolved states. `list_binary_resolved()` exposes only WIN/LOSS records and intentionally does not calculate a probability.

## Operator workflow

Capture provider-recorded MTF history:

```sh
python scripts/export_mtf_history.py \
  --provider bybit_linear \
  --symbol SUIUSDT \
  --bars-1d 500 \
  --bars-4h 1000 \
  --bars-1h 1500 \
  --bars-15m 3000 \
  --bars-5m 5000 \
  --output data/replay/bybit_linear/SUIUSDT/sample
```

Then run a study only after a matching timestamped replay-context file has been captured/prepared:

```sh
python scripts/run_replay_study.py \
  --bundle data/replay/bybit_linear/SUIUSDT/sample \
  --context data/replay/bybit_linear/SUIUSDT/context.json \
  --outcome-db data/replay/outcomes.sqlite3 \
  --output data/replay/studies/sui-study.jsonl \
  --horizon-bars 24
```

For 5m setup bars, `24` bars represents an explicit two-hour study horizon. This changes only study observation length, not Trading Engine entry rules.

## Provider-recorded regression artifacts

Real exchange captures are operator-generated from public APIs and are never silently substituted with synthetic candles. PR CI uses deterministic mocked provider pages and synthetic replay contexts marked as test data so repository verification does not depend on exchange availability.

A real historical study requires both:

- provider-recorded MTF candle bundle;
- corresponding timestamped historical liquidity/universe context.

## Calibration guardrail

Phase 11D reports deterministic decisions, outcome states/counts and the number of binary-resolved observations. It still does not report win probability.

Before any `Estimated Probability` is introduced, a later approved phase must define at minimum:

- sufficient sample size;
- time-separated train/validation/test sets;
- provider/symbol/regime stratification;
- survivorship/listing bias handling;
- ambiguous/unresolved outcome policy;
- transaction-cost assumptions;
- confidence intervals and calibration metrics;
- true out-of-sample validation.

Until that work is complete, `estimated_probability` remains N/A/null.
