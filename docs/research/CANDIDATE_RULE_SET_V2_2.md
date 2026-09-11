# Candidate Rule Set v2.2 — Structural Space Gate

Date: 2026-09-11
Status: PREREGISTERED EXECUTABLE RESEARCH CANDIDATE / HOLDOUT UNTOUCHED / NO PRODUCTION CHANGE

## Scope

v2.2 is a deliberately narrow refinement of `candidate_rule_set_v2_1`.

It preserves the complete v2.1 entry, stop, target, cost, episode-control and 8h time-exit logic, and adds exactly one new eligibility gate:

`the intended 3R target must fit before the nearest causally confirmed H1 structural obstacle, or no such obstacle may exist.`

The purpose is to test the strongest preregistered legacy-knowledge hypothesis without simultaneously changing VSA, ATR thresholds, side selection, volume, H4 alignment or time-exit logic.

## Active research profile

This executable candidate remains the current v2.1-compatible intraday research implementation:

`H1 directional context -> M15 pullback/reclaim -> next M15 open execution`

Maximum hold remains `32 x M15 = 8h` for comparability.

The broader `FAST / INTRADAY / SWING / POSITION` architecture is not activated inside this candidate. Profile-specific TTL/max-hold work continues separately. This avoids changing multiple causal dimensions at once.

## Inherited v2.1 rules

All v2.1 rules remain unchanged:

- H1 EMA20/EMA50 directional trend and EMA20 slope;
- M15 pullback window = 5 closed bars;
- M15 reclaim/continuation trigger;
- next executable M15 open with adverse slippage;
- structural stop beyond the 5-bar pullback extreme plus `0.15 * ATR14_M15`;
- minimum H1 EMA separation `>= 0.20 ATR14_H1`;
- signal candle body fraction `<= 0.60`;
- minimum structural risk distance `>= 1.25%` of executed entry;
- nominal TP = `3R`;
- stop-first same-bar ambiguity;
- maximum hold = 8h;
- fee, slippage and actual funding model unchanged;
- duplicate episode/family control unchanged.

## New deterministic H1 level detector

All level calculations are causal and use only H1 bars already closed at the M15 decision time.

### 1. Confirmed swing points

A H1 bar `k` is a swing high if:

- `high[k] > high[k-1]`
- `high[k] > high[k-2]`
- `high[k] >= high[k+1]`
- `high[k] >= high[k+2]`

A swing low is symmetric.

A pivot at `k` becomes usable only after bar `k+2` has closed.

### 2. Level clustering

All causally confirmed swing highs/lows are sorted by price and clustered.

Cluster tolerance:

`0.20 * ATR14_H1` measured at the decision bar.

A cluster price is the arithmetic mean of its member pivot prices.

### 3. Confirmed structural level

A cluster becomes a confirmed structural level when:

`touch_count >= 2`

High and low pivots may belong to the same cluster. If both occur, `mirror_role_change=true` is recorded as a feature only.

### 4. Structural obstacle in trade direction

At executed entry:

- LONG: nearest confirmed level strictly above entry;
- SHORT: nearest confirmed level strictly below entry.

Distance is normalized by initial structural risk:

`next_confirmed_level_R = directional_distance_to_level / abs(entry - SL)`

If no confirmed level exists in the trade direction, the path is tagged `OPEN_SPACE`.

## New v2.2 hard gate

Trade is eligible only when:

`next_confirmed_level_R is None (OPEN_SPACE) OR next_confirmed_level_R >= 3.0`

This tests whether the nominal 3R target fits before the nearest confirmed H1 obstacle.

The threshold is frozen at `3.0R` because it directly matches the nominal target. Development-only exploration showed the same selected sample at 3.0R, 3.25R and 4.0R, so no stricter post-hoc threshold is promoted.

## Development-only evidence used to choose the gate

Before opening validation for v2.2, the deterministic level layer was applied to the 55 already-resolved v2.1 development trades.

Base v2.1 development:
- n = 55
- WR = 45.45%
- expectancy = +0.1033R
- PF_R = 1.1916

`OPEN_SPACE or next confirmed level >=3R`:
- n = 20
- WR = 55.0%
- expectancy = +0.3175R
- PF_R = 1.6632

This is discovery evidence only. It does not validate v2.2.

## Explicitly NOT promoted

The following remain recorded/research-only and are not hard gates in v2.2:

- floating/congestion-zone detector;
- support/resistance anchor distance;
- mirror-level presence;
- raw ATR-used 40/60/80% thresholds;
- D1/H4 alignment;
- VSA signals;
- relative volume;
- side asymmetry;
- tighter structural-space thresholds above 3R.

Development results for several of these were weak or internally inconsistent. Mirror-anchor behavior was interesting but post-hoc and sample-small, so it is not promoted.

## Validation protocol

After this document and the executable harness are committed:

1. run development to verify exact reproducibility;
2. run untouched v2.2 validation once under the frozen rules;
3. report non-holdout and stress only after the frozen validation run;
4. do not change v2.2 rules based on validation and rerun under the same version;
5. holdout remains locked unless the preregistered promotion gate passes.

## Promotion objective

Same as v2.1:

- non-holdout completed trades >=100;
- validation completed trades >=30;
- OOS/validation WR >=50%;
- expectancy_R >0 after costs;
- PF_R >1 mandatory, target >=1.5;
- stress expectancy_R >0;
- no material single-symbol/regime concentration;
- adequate unique setup-family evidence.

Failure creates a new version; it does not authorize tuning v2.2 against the same validation set.

## Knowledge-base treatment

The uploaded historical level/ATR/VSA materials are hypothesis sources only. v2.2 promotes only the deterministic structural-space hypothesis described above. No legacy constant becomes canonical merely because it appears in historical Knowledge.

## Production boundary

Research only.

- no production strategy changes;
- no Risk Manager changes;
- no execution/deployment changes;
- no automatic rule mutation;
- holdout untouched until the promotion gate explicitly authorizes it.
