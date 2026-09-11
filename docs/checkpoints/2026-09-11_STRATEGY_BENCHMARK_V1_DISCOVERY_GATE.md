# K-Trader Strategy Benchmark v1 — discovery gate

Date: 2026-09-11
Branch: `research-strategy-benchmark-v1`
Canonical base main: `f3ddbfddb37847f63234960855afa287ec9eb9ce`
Accepted production image: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`

## Production boundary

No production code, configuration, deployment, or trading semantics were changed. Production remains read-only. Benchmark outputs live only under `/data/research/phase11g/strategy_benchmark_v1/` and on this research branch.

## Frozen pre-backtest artifacts

- `/data/research/phase11g/strategy_benchmark_v1/inventory.json`
  - semantic SHA-256: `4daa203f0ac6291fcf0e030627f137a8c5fd648f2a9506e938cfd51ac753e4a0`
  - initial raw SHA-256: `90d79eb763246677d1aaeffd5ecddfe240ab0308ede0b7d57097e89f779f4119`
- `/data/research/phase11g/strategy_benchmark_v1/strategy_catalogue.json`
  - SHA-256: `45d5994dd6485802dce1d71df2aa1cc6a2bb6e45abb881c4f3cfebba6eea2a57`
- `/data/research/phase11g/strategy_benchmark_v1/protocol.json`
  - SHA-256: `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

The catalogue froze nine simple strategy families/variants across `5m`, `15m`, and `1h`, giving 27 strategy-timeframe combinations. The protocol froze closed-bar causality, next-open execution, conservative same-bar stop/target ordering, all-taker fees, slippage sensitivity, actual historical funding, 60/20/20 chronological segmentation, walk-forward evidence, and a locked final holdout.

## Data materialization

All pre-existing provider-recorded overlapping candle bundles for the frozen 19-symbol panel were unioned by `open_time`. Overlapping OHLCV, quote-volume, and trade-count records had zero conflicts.

- source builder: `/data/research/phase11g/strategy_benchmark_v1/harness/build_sources.py`
  - SHA-256: `5e5b3efcd687f6f0a2532475429b6112ec5b4758e04ad43356ffe772a3295eb9`
- sources manifest: `/data/research/phase11g/strategy_benchmark_v1/sources/sources_manifest.json`
  - SHA-256: `a14c8031ff82cb5cc8c08b59d5d64de86921f171976c8f93372bdd5d0bc50dcb`
- discovery harness: `/data/research/phase11g/strategy_benchmark_v1/harness/benchmark.py`
  - SHA-256: `ed8ccda2269667d44bfebc303c8b2967ee936dd2b759e5b8184c08c2afe4e673`
  - research branch implementation commit: `5b6331e86f369713555385b1a2518c2a4f1cce27`

Historical funding was fetched from the official Binance USD-M funding history endpoint and persisted per contract before result calculation.

## Discovery and validation result

- discovery/validation report:
  `/data/research/phase11g/strategy_benchmark_v1/runs/discovery_validation/report.json`
  SHA-256 `c438f11646761b45fc4790f1d697d1998dda04ff33efd244fa2085abb2a9b21f`
- leaderboard:
  `/data/research/phase11g/strategy_benchmark_v1/summary/leaderboard.json`
  SHA-256 `2cca0f2f4f927ecf172f6b248e632a74259308bb3b6331170997db36b59bf381`
- strict survivors:
  `/data/research/phase11g/strategy_benchmark_v1/summary/survivors_gt60.json`
  SHA-256 `22f593ddc2d709b0dd47066986e403d95d38f8a4dc882609b0886df68e003279`

Result: **0 / 27 combinations passed the frozen survivor gate**.

Screen counts:

- non-holdout observed win rate >60%: `1 / 27`
- non-holdout positive expectancy and PF>1: `6 / 27`
- non-holdout WR>60% + positive expectancy + PF>1: `0 / 27`
- validation WR>60% + positive expectancy + PF>1: `0 / 27`
- full survivor gate: `0 / 27`

The only non-holdout WR>60% combination was `bb20_2_reentry_v1` on 15m: 360 completed trades, WR 61.94%, PF 0.8804, net expectancy -0.1306% per trade. Its validation segment degraded to 95 trades, WR 55.79%, PF 0.4232, net expectancy -1.1029% per trade.

A separate H1 trend/momentum/breakout cluster produced some positive non-holdout expectancy/PF>1 configurations, but with roughly 20–36% win rates and material validation instability. It therefore did not satisfy the user-required >60% hit-rate criterion or the frozen robustness gate.

## Component analysis and candidate gate

- component analysis:
  `/data/research/phase11g/strategy_benchmark_v1/summary/component_analysis.json`
  SHA-256 `d821a29998be6798cca30cf8a6f574e95756d69c04a31121aa191fa4077e24ad`
- candidate artifact:
  `/data/research/phase11g/strategy_benchmark_v1/combined_rules/candidate_rule_set_v1.json`
  SHA-256 `ee36316b04acd59c896de78067509d4c2c643e03d6acef502fdcaf3e995a67d6`

`candidate_rule_set_v1` status is `BLOCKED_NO_QUALIFIED_CANDIDATE`, `executable=false`, `holdout_authorized=false`.

Reason: after observing the non-holdout evidence, inventing or tuning a combined rule solely to force the requested >60% result would violate the preregistered anti-overfit protocol. No robust parent strategy/component set exists from which a qualified v1 candidate can be constructed.

## Holdout status

**UNTOUCHED / LOCKED.**

The 20% final holdout has not been evaluated. Walk-forward evaluation was limited to the first 80% as preregistered. Since no executable candidate passed the discovery gate, the holdout was deliberately not consumed.

## Decision

The benchmark does **not** currently justify replacing or rebuilding K-Trader architecture around any of the tested simple strategies. The correct v1 outcome is a negative research result, not a tuned winner.

The next eligible research step is to accumulate more genuinely new history and preregister a new strategy/candidate research round while preserving the untouched v1 holdout or reserving new future data as a fresh final holdout.
