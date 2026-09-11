# Phase 11G Prospective Control Specification v1.0

## Purpose

The Phase 11G prospective-control utility deterministically replays already-recorded production universe context and provider-recorded MTF candles across a logical UTC cutoff window. It is a research/control tool only. It does not change live Trading Engine semantics, create orders, relax hard gates, fabricate targets/outcomes, or estimate probability.

The canonical implementation is `ktrader.replay.prospective`; the operator CLI is `scripts/run_prospective_control.py`.

## Inputs and provenance

One control identity is defined by:

- one verified `ktrader.universe_archive.v1` archive;
- one provider;
- explicit inclusive UTC `start` and `end` aligned to the selected setup interval;
- canonical `RuntimeScannerConfig` and its SHA-256;
- explicit `analysis_limit`;
- maximum recorded-context age, canonical Phase 11G value `300s`;
- provider-recorded MTF bundles for symbols encountered in the selected recorded universes.

Bundle provenance is recorded only for symbols selected by a valid recorded snapshot during the logical window. Missing selected-symbol bundles are not substituted with lower-ranked symbols; their slots fail closed as `HISTORY_FAIL`.

## Logical cutoffs

Cutoffs are the inclusive sequence:

`start, start + setup_interval, ..., end`

The bounds must align exactly to the selected setup interval. FAST production research uses canonical `5m` setup/evidence timing and `12` setup-age bars (`60m`). This utility does not redefine the lifecycle contract.

## Recorded universe selection

At logical cutoff `T`:

1. select the newest universe snapshot with `captured_at <= T`;
2. reject future snapshots;
3. calculate `context_age = T - captured_at`;
4. `context_age <= 300s` remains valid;
5. `context_age > 300s` is stale and the cutoff is fail-closed;
6. use the first `analysis_limit` members exactly in the recorded liquidity ranking.

No current exchange state may backfill or alter an older logical cutoff.

## Causal candle selection

For each selected symbol, the utility uses the canonical MTF bundle and `slice_datasets_asof()`.

Only candles with `close_time <= cutoff` may enter analysis. Canonical minimum history requirements remain controlled by `RuntimeScannerConfig.history`. Missing minimum history is counted as `HISTORY_FAIL` and does not produce a decision.

No future candle, provider substitution, history interpolation, lower-ranked-symbol replacement, or cross-provider splice is permitted.

## Canonical analyzer

A history-ready slot calls the same `analyze_candle_snapshot()` function used by live/runtime and historical replay.

The prospective utility must not contain a second implementation of:

- ATR / ATR-used;
- market structure;
- Trap/VSA detection;
- setup discovery;
- Entry/Luft/SL/structural target geometry;
- RR;
- Setup Score / Grade;
- setup TTL;
- final LONG/SHORT eligibility.

## UTC-midnight rule

Canonical ATR-used daily range requires canonical closed `5m` candles beginning at exactly `00:00 UTC` for the current UTC day.

At a cutoff where the causal snapshot contains no closed `5m` candle opened on the current UTC day, the prospective utility records:

`ANALYSIS_ERROR: ValueError: 5m day sequence is empty`

Rules:

- the canonical analyzer is not called for that slot;
- no previous-day range is carried forward;
- no synthetic `00:00` candle or daily range is fabricated;
- no `NO_TRADE` decision is synthesized;
- the slot remains explicit in analysis-error accounting.

This makes the known midnight boundary deterministic and fail-closed without changing live analyzer semantics.

## Slot states

Each selected symbol/cutoff slot has exactly one state:

- `ANALYZED` — canonical analyzer returned its decision set;
- `HISTORY_FAIL` — required causal history/bundle is unavailable;
- `ANALYSIS_ERROR` — history is ready but analysis cannot be executed/finished safely.

Missing or stale recorded context is cutoff-level state and produces no symbol slots.

An analysis exception is recorded by exception type and message. It is never silently converted into a decision.

## Deterministic sharding

A full logical cutoff sequence has stable zero-based global indices. For `N` shards, cutoff index `i` belongs to:

`shard_index = i mod N`

This assignment is deterministic and independent of execution order.

Every shard records:

- archive SHA-256;
- scanner-config SHA-256;
- relevant bundle SHA-256 map;
- start/end and cutoff interval;
- analysis/context settings;
- shard index/count;
- expected cutoff count;
- completed cutoff records;
- semantic shard SHA-256.

## Resume contract

Partial shards are valid checkpoints. Resume requires exact provenance/configuration equality with the requested run. Existing cutoff records must belong to the same deterministic shard assignment and must be unique.

Resume never reinterprets or silently rewrites completed cutoff records. New cutoffs are appended by deterministic cutoff identity. Checkpoints are written atomically.

## Merge contract

A full report may be produced only when:

- every shard index `0..N-1` is supplied exactly once;
- every shard is complete;
- all shards have identical non-shard provenance/configuration;
- the merged cutoff sequence exactly equals the full logical window.

The final report deliberately excludes execution topology such as `shard_count` and shard hashes. Therefore an equivalent monolithic run and an equivalent sharded/resumed run produce the same report payload and semantic `report_sha256`.

## Report accounting

The deterministic report includes at minimum:

- logical and selected-context cutoff counts;
- missing/stale context cutoffs and context-age bounds;
- symbol slots;
- analyzed/history-fail/analysis-error slot counts;
- decision-record count;
- best-side counts;
- per-symbol candidate/history-fail counts;
- explicit analysis-error counts;
- reason-code and setup-type counts;
- sequential hard-gate funnel;
- tradable, RR>=3 non-tradable and near-miss audit records;
- every flattened decision audit record identifies its `canonical_symbol`;
- unique stable tradable-signal count;
- archive/config/bundle provenance hashes;
- semantic report SHA-256.

The sequential funnel preserves current hard rules:

`HTF aligned -> STRONG confirmed level -> valid geometry -> ATR <= 80% -> TTL pass -> RR >= 3 -> Grade A/A+ -> LONG/SHORT`

The report is observational. It must not change any threshold to manufacture funnel survivors.

## Operator workflow

Run one bounded/resumable shard:

```sh
python scripts/run_prospective_control.py run \
  --archive /data/research/phase11g/control/universe/archive.jsonl \
  --bundle-root /data/research/phase11g/control/bundles \
  --start 2026-09-10T04:15:00Z \
  --end 2026-09-11T07:20:00Z \
  --shard-index 0 \
  --shard-count 4 \
  --output /data/research/phase11g/control/shard-0.json
```

Resume the same shard after interruption:

```sh
python scripts/run_prospective_control.py run \
  --archive /data/research/phase11g/control/universe/archive.jsonl \
  --bundle-root /data/research/phase11g/control/bundles \
  --start 2026-09-10T04:15:00Z \
  --end 2026-09-11T07:20:00Z \
  --shard-index 0 \
  --shard-count 4 \
  --resume \
  --output /data/research/phase11g/control/shard-0.json
```

Merge the complete shard set:

```sh
python scripts/run_prospective_control.py merge \
  --shard /data/research/phase11g/control/shard-0.json \
  --shard /data/research/phase11g/control/shard-1.json \
  --shard /data/research/phase11g/control/shard-2.json \
  --shard /data/research/phase11g/control/shard-3.json \
  --output /data/research/phase11g/control/report.json
```

## Unchanged Phase 11G boundaries

This utility does not change:

- FAST production profile `M5 / 60m`;
- `RR >= 3`;
- canonical ATR-used rules;
- HTF directional alignment;
- STRONG/confirmed primary-level requirement;
- structural stop / nearest valid structural target;
- Setup Score / Grade semantics;
- D1/MTF history requirements;
- context provenance/freshness rules;
- `estimated_probability = null/N/A`;
- catalogue materialization requirements.

INTRADAY/M15 and MEDIUM/H1 remain research-only. Phase 12 remains inactive unless separately approved.
