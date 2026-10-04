# K-Trader research strategy catalogue — hypotheses, not approved trading rules

> **RESTORATION WARNING (2026-10-04):** This draft's S2–S5 ID mapping differs from the dated history-first plan. Server-local approval confirms the six IDs and S3 SL beyond level but does not establish this draft's executable mapping. Do not treat the following hypotheses as restored exact approved definitions. See [restoration matrix](GERCHIK_S1_S6_RESTORATION_MATRIX_2026-10-04.md) and [backtest preparation protocol](GERCHIK_BACKTEST_PROTOCOL_V0_1_2026-10-04.md). Historical S6's ATR-based level builder is superseded. No six-strategy run is approved by a documentation label.

Status: **DRAFT FOR RESEARCH**. K-Trader's Gerchik research model does **not** execute live orders. All hypothetical trades are evaluated only in historical simulation after validated causal level prerequisites; missing ATR is recorded as a data-quality condition, not a new blanket trade prohibition. No strategy is selected as optimal before out-of-sample comparison.

## Shared causal pipeline

1. Build D1/W1 levels from validated source events; preserve exactly one primary type and all provenance. Distinguish independently verified formation from mere test pivots or exploratory clusters. Never treat a level as known before the right-side confirmation or independent review actually completes. D1/W1 overlap is allowed as corroborating evidence within approved symmetric luft; no automatic strength score.
2. Compute approved filtered ATR5 only from D1 bars **closed before** the decision timestamp. Insufficient normal-bar history => explicit missing-ATR diagnostics; strategy-specific treatment must be frozen before simulation, without reinstating the cancelled blanket transition no-trade rule. ATR is not used to construct levels.
3. Observe approach/reaction around a known D1/W1 level on H4/H1; use M5/M15 for the owner's current intraday entry-model precision layer. M30 and other horizon variants require separately restored/frozen specifications. These lower timeframes never create independent levels.
4. Evaluate each candidate strategy's independently defined prerequisites as of each bar close. Multiple simultaneous eligible strategies are allowed during research; log all rather than selecting a winner using future outcomes.
5. Compute entry, technical stop, target, fees, spread, slippage and exposure using **as-of** information. Run simulation with explicit conservative handling of same-candle stop/target ambiguity; log censored/ambiguous cases separately.
6. Chronological early-development/late-validation split; freeze parameters before late data. Reserved external archive remains untouched until formal freeze.

## Candidate strategies and falsifiable prerequisites

| ID | Research hypothesis | Prerequisites to test (not yet thresholds) | Possible invalidation |
|---|---|---|---|
| S1 | First approach and rejection of known D1/W1 level | Level existed before approach; price approaches from one side; H1/H4 rejection evidence; M15/M30 timing event after rejection | Decisive close through level, adverse excursion or stale level |
| S2 | Breakout and confirmed retest | Level known before breakout; bar closes beyond level; subsequent retest occurs after breakout; confirmation on lower TF only after retest | Return through level before confirmation, false break |
| S3 | False breakout and return; technical SL beyond the level | Known level; price crosses level then returns to original side on completed bars; explicit reversal confirmation | Continued breakout, insufficient reversal confirmation |
| S4 | Range boundary reaction | Two separately established D1/W1 boundaries exist **as of** decision; price is near one boundary; enough space to opposite boundary | Range breakdown, poor reward/risk, insufficient independent boundary evidence |
| S5 | Trend continuation after pullback | Known level aligns with independently established higher-TF trend; pullback completes; subsequent lower-TF confirmation | Trend invalidation or missing independently defined trend state |
| S6 | Historical H1 20-bar breakout + EMA50 + proximity to D1/weekly level | Restoration reference from docs/knowledge/part1/06_strategies.md; exact causal breakout, EMA, proximity, entry and exit definitions must be restored before a new run | Unresolved executable specifications; prior holdout already inspected |

S1–S5 above are draft hypotheses, not proof that their mapping reproduces every approved historical strategy. The approved program covers S1–S6; restore authoritative executable definitions before running them. The restored development sequence is 1R then 3R, S3 SL beyond level, analysis, Level Strength v2 and independent reserved holdout. No mandatory 2R stage.

Do not infer intrabar event order from D1/W1 OHLC. Distinguish mutually incompatible prerequisites and concurrent hypotheses; only after calibrated out-of-sample analysis may the selection policy be proposed. A candidate's empirical win rate alone is insufficient: compare net expectancy, adverse excursion, trade count, stability across symbols/regimes and costs, with uncertainty intervals. Avoid post-hoc parameter tuning on the validation window.

## Explicit unresolved specifications before strategy implementation

- Operational definition and independent evidence for Gerchik structural extrema, trend and level expiry.
- Numeric thresholds for rejection, breakout, retest, false breakout, and entry timing; decide using development data only.
- Instrument-specific realistic historical spread/fees/slippage and exchange session calendars.
- Bar-resolution event ordering: when stop and target are both reachable inside the same candle, conservative loss-first or mark ambiguous; report sensitivity.
- Binding ATR5 v2 is the iterative current-five mean with full recheck after each replacement, inclusive >=2x and <=1/3 thresholds and newest-abnormal-first engineering tie-break. The 2026-10-01 canonical owner decision supersedes old rolling-reference wording. Adaptive v3 remains experimental; no silent substitution. See ATR5_GERCHIK_OWNER_DECISION_2026-10-01.md and ATR5_TRADE_EVALUATION_V0_1.md.
- Contextual D1/W1 tolerance and M5/M15 entry precision are separate. Freeze percentage anchor, Forex point convention and tick rounding explicitly before implementing numeric tolerance.

## Verification status

At source SHA `1c10c8c597eec8e4722b7efba48f8ca55cebb8a7`, a fresh isolated GitHub clone on `kgm-e4-owner-pilot` passed **106/106** selected tests: `tests/test_gerchik_*.py`, `tests/test_atr_free_level_validation_v1.py`, `tests/test_native_internal_d1_w1_v1.py`, `tests/test_historical_level_builder.py`, `tests/test_structural_level_clusters_v1.py`. This is a code regression gate, **not** empirical proof of level reliability. Previously documented internal data audit covers 8,981 D1 candles and 1,257 complete derived W1 candles across 19 symbols, but this session has **not** rerun actual level formation or real-data ATR on that archive. Do not claim historical level-quality validation complete. Next: immutable dataset manifests and independent as-of D1/W1 event replay, duplicate/false-positive checks, level revisit statistics versus predeclared baselines, filtered ATR per cutoff, then frozen strategy prereq implementation.
