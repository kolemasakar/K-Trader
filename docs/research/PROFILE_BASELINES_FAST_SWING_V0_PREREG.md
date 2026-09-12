# FAST + SWING Baselines v0 — Preregistration

Status: **PREREGISTERED / RESEARCH ONLY / HOLDOUT UNTOUCHED**

Purpose: establish simple executable profile baselines on the independent deep profile dataset without copying tuned v2.2 thresholds.

Dataset root:

`/data/research/phase11g/profile_research_dataset_v0_20260911T204500Z_adaptive`

Provider: `binance_usdm`.

Costs for both baselines:

- fee: `5 bps` per side using the existing research accounting convention;
- base adverse slippage: `2 bps` per execution side;
- stress adverse slippage: `5 bps` per execution side;
- actual provider-recorded funding between entry and exit;
- target: nominal `3R`;
- same-bar ambiguity: STOP before TARGET;
- signal only on closed trigger bar;
- entry no earlier than next trigger-bar open;
- no pyramiding; one open position per symbol/profile;
- no holdout outcomes may be read.

Time split per symbol on the trigger timeframe:

- development: first 60%;
- validation: next 20%;
- untouched profile holdout: final 20%.

Only development, validation and their combined non-holdout may be evaluated in this baseline run.

## FAST v0

Research horizon: up to approximately 4h.

Timeframes:

- H1 direction;
- M15 setup/pullback context;
- M5 trigger/execution.

Direction:

- LONG: H1 EMA20 > EMA50 and EMA20 > EMA20 three H1 bars earlier;
- SHORT: H1 EMA20 < EMA50 and EMA20 < EMA20 three H1 bars earlier.

M15 alignment:

- EMA20/EMA50 must point in the same direction as H1.

Pullback episode, last 3 closed M15 bars:

- LONG: at least one bar touches/breaches M15 EMA20 or RSI14 <45;
- SHORT: at least one bar touches/breaches M15 EMA20 or RSI14 >55.

M5 trigger:

- LONG: close > EMA20, RSI14 >=50, close > previous M5 high, bullish body;
- SHORT: close < EMA20, RSI14 <=50, close < previous M5 low, bearish body.

Structural stop:

- LONG: minimum low of current + previous 5 M5 bars minus `0.15 * ATR14_M5`;
- SHORT: maximum high of current + previous 5 M5 bars plus `0.15 * ATR14_M5`.

No v2.2 min-risk, H1-separation, body-fraction or structural-space thresholds are imported.

Max hold:

`48 x M5 = 4h`, followed by TIME_EXIT at the next M5 open if neither STOP nor TARGET resolved the trade.

## SWING v0

Research horizon: approximately 2–4 days.

Timeframes:

- D1 direction;
- H4 alignment + pullback context;
- H1 trigger/execution.

Direction:

- LONG: D1 EMA20 > EMA50 and EMA20 > EMA20 three D1 bars earlier;
- SHORT: D1 EMA20 < EMA50 and EMA20 < EMA20 three D1 bars earlier.

H4 alignment:

- EMA20/EMA50 must point in the same direction as D1.

Pullback episode, last 4 closed H4 bars:

- LONG: at least one bar touches/breaches H4 EMA20 or RSI14 <45;
- SHORT: at least one bar touches/breaches H4 EMA20 or RSI14 >55.

H1 trigger:

- LONG: close > EMA20, RSI14 >=50, close > previous H1 high, bullish body;
- SHORT: close < EMA20, RSI14 <=50, close < previous H1 low, bearish body.

Structural stop:

- LONG: minimum low of current + previous 4 H1 bars minus `0.15 * ATR14_H1`;
- SHORT: maximum high of current + previous 4 H1 bars plus `0.15 * ATR14_H1`.

No v2.2 min-risk, H1-separation, body-fraction or structural-space thresholds are imported.

Max hold:

`96 x H1 = 4 days`, followed by TIME_EXIT at the next H1 open if unresolved.

## Interpretation

These are deliberately simple baselines, not candidate production strategies. Results are used to measure whether each profile has any reproducible signal/economic foundation before feature engineering.

No threshold may be changed after seeing validation and still be called the same v0 baseline. Any change requires a new preregistered version and fresh evidence.
