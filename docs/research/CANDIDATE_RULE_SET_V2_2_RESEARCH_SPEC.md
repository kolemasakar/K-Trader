# Candidate Rule Set v2.2 — Research Specification

Date: 2026-09-11
Status: RESEARCH SPEC / NOT YET AN EXECUTABLE FROZEN CANDIDATE / HOLDOUT UNTOUCHED

## Objective

Extend the current v2.1 trend-pullback-continuation foundation with the useful parts of the uploaded legacy Knowledge Base without importing unvalidated legacy constants as production rules.

Core remains:

`trend context -> pullback -> reclaim/continuation -> structural invalidation stop -> target >= 3R`

## 1. Multi-horizon profiles

Time limits are profile-specific. The current 8h rule is not universal.

### FAST
- context: H1/M15
- trigger: M5
- provisional max hold: 4h
- intended trade duration: minutes to several hours

### INTRADAY
- context: H4/H1
- trigger: M15
- provisional max hold: 8-12h
- v2.1 belongs to this profile

### SWING
- context: D1/H4
- trigger: H1
- provisional max hold: 2-4 days

### POSITION
- context: W1/D1
- trigger: H4
- provisional max hold: 7-21 days

These are starting envelopes only. Final time-stop parameters must be learned from MFE/MAE and duration distributions on unique resolved setup families.

## 2. Structural level layer

Legacy knowledge distinguishes floating/forming zones from confirmed fixed levels and describes trend-break, historical, mirror, limit/repeated-touch, abnormal-bar, consolidation and gap levels.

v2.2 should implement deterministic level features before deciding whether any are hard gates:

- level_detected
- level_type
- higher_tf_level
- touch_count
- false_break_count
- rejection_tail_score
- level_age_bars
- mirror_role_change
- distance_to_level_R
- floating_zone_flag

Primary hypothesis:

- continuation entries anchored to confirmed structural levels outperform entries inside ambiguous/floating congestion.

No production gate until causal OOS evidence exists.

## 3. Available-range layer

Implement:

- clean ATR5D based only on closed D1 bars;
- D1 ATR14;
- directional ATR used from UTC-day open;
- remaining statistical range;
- next structural obstacle distance in R;
- technical range in R;
- whether 3R target fits before the next structural obstacle.

### Legacy ATR threshold audit already performed

On 80 usable v2.1 development+validation trades:

- base: WR 42.5%, expectancy +0.0666R, PF_R 1.117;
- `<60% directional ATR used`: 56 trades, WR 42.9%, expectancy +0.0536R, PF_R 1.092;
- `<80%`: 61 trades, WR 41.0%, expectancy +0.0124R, PF_R 1.021.

Validation alone improved under `<60%`:

- 18 trades, WR 44.4%, expectancy +0.104R, PF_R 1.177.

But development did not show a comparable robust gain, and >100% ATR-used behaved positively in development but negatively in validation.

Decision: do NOT make 60% or 80% a universal hard gate. Keep ATR-used as a feature/regime variable. Test an exception for breakout into open space separately.

## 4. Technical-range safety hypothesis

A stronger candidate than raw ATR-used is whether the intended 3R target has room before a known structural obstacle.

Research hypothesis:

`technical_range_R >= target_R + cost_buffer_R`

may be a defensible eligibility constraint after deterministic level detection exists.

The legacy recommendation that ATR should contain five stop distances remains a research feature, not a frozen rule.

## 5. VSA layer

Implement quantitative, causal feature definitions for:

- No Demand
- No Supply
- Test
- Upthrust
- Buying Climax
- Selling Climax
- Stopping Volume

Each definition must explicitly use only closed bars and measurable quantities:

- spread/range relative to recent distribution;
- volume relative to recent distribution;
- close location within bar;
- interaction with deterministic level;
- 1-2 bar confirmation.

Initial policy:

- VSA is a score/context feature;
- no VSA signal is a mandatory hard gate;
- VSA may only be promoted after ablation and OOS validation show incremental expectancy beyond structure/trend alone.

## 6. Stop and sizing policy

Preserve the useful legacy principle:

- stop belongs beyond the structure whose failure invalidates the thesis;
- actual execution/slippage is included in risk distance;
- position size normalizes account risk to that structural stop.

Reject direct reuse of old market-specific fixed stop percentages/pips/cents.

The current v2.1 observation that very narrow risk units are fragile remains relevant and should be re-estimated separately by FAST/INTRADAY/SWING/POSITION profile.

## 7. Risk-management policy

Legacy daily-risk and loss-streak ideas are informative but cannot override canonical K-Trader Risk Manager settings.

Research should track:

- risk_per_trade_pct
- total_open_risk_pct
- correlated setup-family exposure
- symbol/sector/market-beta cluster exposure
- daily realized R
- daily loss streak

The dependence unit is unique setup family, not raw signal count.

## 8. Learning loop from real trades

Every accepted, rejected-near-miss and executed setup stores:

- strategy/profile version;
- complete causal features;
- level features;
- ATR/range features;
- VSA features;
- trend/pullback/confirmation features;
- planned and realized entry/SL/TP;
- fees/slippage/funding;
- MFE/MAE;
- realized R;
- hold duration;
- unique setup-family id;
- exact data/config hashes.

Evidence gates remain:

- <30 resolved unique families: observation only;
- 30-49: diagnostics only;
- 50-99: ablation/component proposals allowed;
- >=100 diverse resolved families: versioned recalibration proposal allowed;
- every rule change creates a new preregistered version and requires fresh walk-forward/OOS evidence.

No automatic live-rule mutation.

## 9. Promotion objective

For nominal target RR 1:3:

- OOS WR target >=50%;
- expectancy_R >0 after all costs;
- PF_R >1 mandatory, target >=1.5;
- stress-slippage survival;
- no single-symbol/single-regime domination;
- drawdown compatible with expected return;
- sufficient unique-family sample.

A strategy below 50% WR can still be profitable mathematically, but it does not satisfy the user's preferred operating target and should not be represented as having met that target.

## 10. Next implementation order

1. deterministic level detector and floating-zone detector;
2. technical-range-to-next-level metric;
3. clean ATR5D / directional ATR-used feature capture;
4. deterministic VSA feature definitions;
5. profile-aware time/TTL framework;
6. causal ablation on development data;
7. freeze executable v2.2 candidate only after definitions are complete;
8. validation/walk-forward;
9. holdout only after preregistered promotion gate passes.
