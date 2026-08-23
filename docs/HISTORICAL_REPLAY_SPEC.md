# Historical Replay / Signal Outcome Spec v1.3

## Purpose

Phases 11B-11E provide reproducible provider-recorded historical candles, deterministic MTF replay snapshots, conservative signal-outcome tracking, full-engine chronological study orchestration and timestamped historical universe/liquidity context captured prospectively.

They do not convert Setup Score into statistical probability. `estimated_probability` remains null/N/A.

## Provider history contract

Schema: `ktrader.history.v1`.

A history dataset is a coherent series from exactly one provider, canonical symbol and timeframe.

Rules:

- confirmed closed candles only;
- chronological, contiguous and UTC aligned;
- no provider mixing/fallback inside a dataset;
- Decimal market values serialized as strings;
- source kind `provider`;
- SHA-256 digest over canonical candle content;
- requested bar count and actual range recorded separately.

## Historical collection

`collect_provider_history()` is the one-page compatibility path. `collect_deep_provider_history()` pages backward through the same provider with an explicit UTC end cursor.

Current implementations:

- Binance USD-M `/fapi/v1/klines` with `endTime`;
- Bybit Linear `/v5/market/kline` with `end`.

Deep collection requires exact requested closed-bar depth, strict backward cursor progress, page deduplication, provider/symbol/timeframe identity and final contiguity. Insufficient depth, unsupported pagination or gaps fail closed. Another provider may never fill a missing page.

## MTF replay bundle

Schema: `ktrader.mtf_bundle.v1`.

A canonical bundle contains exactly `1d/4h/1h/15m/5m`, all under one provider, canonical symbol, provider-native symbol and UTC `as_of` cutoff. Any included candle closing after `as_of` invalidates the bundle.

The manifest stores per-timeframe counts/digests plus a bundle SHA-256. `slice_datasets_asof()` removes all bars not closed by the selected replay cutoff and can require the live minimum history per timeframe.

Default live-compatible history depths:

```text
1d   250
4h   250
1h   250
15m  250
5m   300
```

Research captures may be deeper without changing the schema.

## Shared live/replay analysis path

Phase 11D uses the same pure `analyze_candle_snapshot()` path for live runtime and historical replay.

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

Historical replay may not change scoring weights, RR requirements, ATR-used limits or setup eligibility rules.

## Why OHLCV alone is insufficient

The live Setup Score also consumes market-universe context:

- liquidity score;
- liquidity rank;
- universe size.

Therefore an MTF OHLCV bundle alone cannot faithfully reproduce the live decision context. Missing historical liquidity information may not be replaced by assumed values such as `rank=1`.

## Replay context

Schema: `ktrader.replay_context.v1`.

A context contains confirmed instrument identity and strictly chronological liquidity observations with:

- UTC timestamp;
- liquidity score;
- liquidity rank;
- universe size;
- maximum allowed context age.

At replay cutoff `T`, only the newest point with `timestamp <= T` may be used. If no point exists or it is stale, that cutoff is skipped fail-closed.

Forbidden:

- guessed rank/universe size;
- future context points;
- indefinite stale carry-forward;
- provider substitution.

## Historical universe snapshot contract - Phase 11E

Schema: `ktrader.universe_snapshot.v1`.

A snapshot records one provider-native market universe at a specific UTC capture time using an explicit `UniverseConfig`.

It preserves the inputs required to audit/reproduce live-compatible liquidity ranking, including where available:

- instrument identity and provider-native symbol;
- price tick / quantity step;
- last price;
- 24h quote volume and base volume;
- 24h trade count;
- bid / ask;
- open interest field when present;
- calculated liquidity score;
- rank;
- resulting universe size.

The snapshot uses the same `build_universe()` / `liquidity_score()` logic as live scanning. Ranks must be contiguous from one and reproducible from stored ticker inputs.

Snapshot validation rejects:

- cross-provider instruments/tickers;
- duplicate symbols;
- ticker timestamps after `captured_at`;
- rank/score inconsistencies;
- digest mismatch.

Each snapshot has a content SHA-256.

## Prospective-only historical rank rule

Public exchange ticker endpoints used by K-Trader expose current market state. They do not provide a trustworthy historical reconstruction of the full ranked universe for arbitrary past timestamps.

Therefore Phase 11E follows a strict rule:

> Historical liquidity rank/universe size exists only if K-Trader actually captured a timestamped provider-native universe snapshot at that time.

Current ticker data must never be used to backfill an old replay cutoff. Real historical universe context must be accumulated prospectively by a continuously running capture process.

## Universe archive

Schema: `ktrader.universe_archive.v1`.

An archive is an append-only ordered set of universe snapshots and must use:

- exactly one provider;
- exactly one `UniverseConfig`;
- strictly increasing capture timestamps.

It stores each snapshot digest and one archive SHA-256. Provider/config mixing, non-chronological append and tampering fail closed.

A provider switch starts a separate coherent archive; exchanges are never spliced into one historical universe series.

## Study cohort

Schema: `ktrader.study_cohort.v1`.

A cohort deterministically selects from one verified universe archive:

- explicit UTC start/end window;
- optional explicit symbol subset;
- maximum replay-context age.

For every selected symbol, Phase 11E generates a `ktrader.replay_context.v1` using only snapshot observations in that cohort window. Each point receives the snapshot's captured liquidity score, rank and live-compatible universe size.

Cohort validation rejects:

- symbols never present in the selected captured universe;
- provider mismatch;
- changed analysis-critical instrument metadata within one study identity;
- unsafe context file paths;
- context/cohort digest mismatch.

The cohort manifest records source archive identity, selected snapshot digests, symbols, time range, context digests and a cohort SHA-256.

## Full replay study

Schema: `ktrader.replay_study.v1`.

`run_replay_study()` walks setup-timeframe cutoffs chronologically. At each accepted cutoff it:

- slices the MTF bundle to confirmed bars only;
- verifies minimum history;
- resolves a valid captured replay context point;
- calls the canonical shared analyzer;
- selects the best `TradingDecision` through normal engine ordering;
- retains exact time-specific decision fingerprint for audit;
- evaluates only the first occurrence of a unique tradable setup on future confirmed bars;
- optionally persists outcome through `OutcomeRepository`.

## Decision identity vs stable setup identity

`decision_fingerprint()` identifies one exact emitted decision and includes decision timing.

`stable_signal_key()` identifies unchanged setup geometry by provider, symbol, side, setup type, primary level, Entry, Stop and Target. This prevents an unchanged setup observed across multiple consecutive 5m cutoffs from being counted as multiple independent signals.

## Outcome contract

Eligible outcomes require a tradable LONG/SHORT decision with Entry, Stop and Target. `NO_TRADE` and missing geometry never enter binary samples.

Canonical states:

- `PENDING_ENTRY`;
- `OPEN`;
- `WIN`;
- `LOSS`;
- `AMBIGUOUS`;
- `EXPIRED_NO_ENTRY`;
- `EXPIRED_OPEN`;
- `NOT_ELIGIBLE`.

Future outcome candles must start strictly after the decision's last closed bar and remain contiguous under the same provider/symbol.

## Intrabar ambiguity

OHLC does not prove intrabar ordering.

- Entry and an exit touched in the same candle -> `AMBIGUOUS`.
- Stop and Target both touched in one post-entry candle -> `AMBIGUOUS`.

Ambiguous outcomes are excluded from WIN/LOSS samples. No optimistic or pessimistic ordering is invented.

## Outcome horizon and R

The study horizon is explicit and optional. For 5m setup bars, `24` bars represents a two-hour observation horizon without changing Trading Engine rules.

`outcome_r` is a planned geometry-touch label, not realized broker PnL:

- target -> planned reward/risk multiple;
- stop -> `-1R`;
- ambiguous/open/expired/not-eligible -> N/A.

Fees, funding, slippage and execution quality are not yet modeled.

## Operator workflow

Prospectively capture current universe snapshots repeatedly under one fixed universe configuration:

```sh
python scripts/capture_universe_snapshot.py \
  --provider bybit_linear \
  --max-price 3 \
  --max-candidates 50 \
  --output data/replay/bybit_linear/universe.jsonl
```

Build a reproducible cohort after enough snapshots exist:

```sh
python scripts/build_study_cohort.py \
  --archive data/replay/bybit_linear/universe.jsonl \
  --symbols SUIUSDT DOGEUSDT \
  --output data/replay/bybit_linear/cohort
```

Capture provider-recorded MTF history for a selected symbol:

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

Run the full-engine study with the matching generated replay context:

```sh
python scripts/run_replay_study.py \
  --bundle data/replay/bybit_linear/SUIUSDT/sample \
  --context data/replay/bybit_linear/cohort/contexts/SUIUSDT.json \
  --outcome-db data/replay/outcomes.sqlite3 \
  --output data/replay/studies/sui-study.jsonl \
  --horizon-bars 24
```

## Real vs synthetic artifacts

Real exchange captures are operator-generated from public provider endpoints and are never silently replaced with synthetic data. Normal PR CI uses deterministic synthetic/mocked fixtures explicitly marked as test data.

A real full-engine historical study requires coherent matching inputs:

- provider-recorded MTF candle bundle;
- provider-native universe archive captured prospectively;
- derived study cohort / replay context.

Their SHA-256 identities make the study inputs auditable.

## Calibration guardrail

Phases 11B-11E can report decisions, outcome states/counts and binary-resolved sample size. They do not report a calibrated win probability.

Before any `Estimated Probability` is introduced, a later approved phase must define at minimum:

- sufficient sample size;
- time-separated train/validation/test datasets;
- provider/symbol/regime stratification;
- survivorship/listing bias handling;
- ambiguous/unresolved outcome policy;
- transaction-cost assumptions;
- confidence intervals and calibration metrics;
- true out-of-sample validation.

Until then, `estimated_probability` remains N/A/null.
