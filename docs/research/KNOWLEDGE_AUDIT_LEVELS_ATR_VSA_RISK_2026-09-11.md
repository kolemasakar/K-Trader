# Knowledge Audit — Levels, ATR, VSA, Risk and Position Sizing

Date: 2026-09-11
Status: RESEARCH INPUT / NO PRODUCTION CHANGE

## Sources reviewed

1. `01_levels_rules.pdf`
2. `02_ATR_and_range.pdf`
3. `03_money_management.pdf`
4. `04_position_sizing.pdf`
5. `K_Trader_KB_VSA_ATR_SysInstrAddition1.md`

## Executive conclusion

The uploaded material contains useful structural concepts but mixes three different classes of content:

- market-structure ideas that are broadly compatible with current K-Trader research;
- numerical heuristics originally written for other markets and periods that must not be copied directly into crypto production;
- unverified VSA / ATR rules that are suitable as research features and hypotheses, not yet as universal hard gates.

The current `candidate_rule_set_v2_1` must therefore NOT be silently overwritten. The material should be incorporated into a new versioned research specification and tested causally.

## 1. Levels — accepted concepts

Useful concepts from `01_levels_rules.pdf`:

- distinguish forming/floating zones from confirmed/fixed levels;
- avoid entries while the market is still forming an ambiguous floating level / congestion zone;
- prefer levels that have clear structural confirmation;
- level classes worth recording include:
  - trend-break / first technical pullback levels;
  - historical repeated-price levels;
  - mirror support/resistance levels;
  - repeated-touch limit levels;
  - abnormal-bar boundary levels;
  - consolidation/trading-range levels;
  - gap-boundary levels where relevant;
- confirming features include repeated touches, failed breakouts, long rejection tails, level origin from a major structural turn, and higher-timeframe origin.

These concepts are strongly compatible with the present strategy direction: `trend context -> pullback -> reclaim/continuation`.

### Proposed integration

Do not initially require one exact named level type as a hard gate. Instead add a deterministic `level_context` feature block to every setup:

- `level_detected`
- `level_type`
- `level_age_bars`
- `touch_count`
- `false_break_count`
- `mirror_role_change`
- `rejection_tail_score`
- `distance_to_level_at_entry_R`
- `higher_tf_level`
- `floating_zone_flag`

Initial hard rule candidate for future testing:

- `floating_zone_flag == true` -> reject or downgrade.

This is not promoted to production until validated.

## 2. ATR and available range — accepted concept, numerical thresholds require revalidation

Useful concepts from `02_ATR_and_range.pdf`:

- separate statistical/expected range from technical available range;
- use ATR as a measure of remaining movement potential, not as a directional signal;
- late entries after a large fraction of expected movement has already been consumed are less attractive unless the market is breaking into open space;
- the next structural obstacle matters at least as much as nominal ATR;
- a planned 3R target must physically fit inside the remaining technical range;
- abnormal bars should not blindly dominate a short ATR estimate.

The source contains historical heuristic thresholds such as 75-80% of daily ATR already used, and a preference for ATR large enough to contain five stop distances. These are research hypotheses, not portable production constants for crypto futures.

### Proposed integration

Add causal features:

- `atr5d_clean`
- `atr14_d1`
- `daily_range_used_pct`
- `directional_atr_used_pct`
- `remaining_statistical_range_pct`
- `distance_to_next_structural_level_R`
- `technical_range_R`
- `target_fits_before_level`

Potential hard safety rule for testing:

- reject if `technical_range_R < 3.0 + cost_buffer_R`.

Potential ranking features:

- prefer lower `directional_atr_used_pct`;
- downgrade >60-80% only if empirical K-Trader data supports that threshold;
- allow exception for verified breakout into open space.

## 3. Stop placement — strongly compatible principle, old fixed percentages rejected

Useful concepts from `04_position_sizing.pdf`:

- stop belongs behind the market structure whose failure invalidates the trade thesis;
- risk is measured from actual executed entry, not from the nominal level;
- slippage and entry offset must be included in effective risk;
- reward:risk should be evaluated from the executable entry and actual stop;
- technical stop is preferred when it reflects thesis invalidation.

Not directly portable:

- fixed stop percentages such as 0.1-0.2% of price;
- market-specific fixed cent/pip stop examples;
- rule that technical stop may exceed calculated stop by no more than 20%.

Those numbers are market-specific legacy heuristics and conflict with current crypto evidence, where v2.1 already found very narrow R-units economically fragile.

### Current K-Trader rule direction

Keep structural stop placement and account-risk-normalized sizing. Continue to test minimum/maximum stop-distance quality empirically by horizon/profile.

## 4. Money management — concept accepted, percentages need project policy reconciliation

Useful concepts from `03_money_management.pdf`:

- account-level risk limits are separate from setup quality;
- risk should be normalized across instruments through position size;
- position size should decrease when technical stop distance increases;
- do not concentrate the entire daily risk allowance into one trade;
- repeated losses should trigger a risk/session control rather than revenge trading.

Legacy numerical guidance such as 1-3% daily risk and splitting into 3-5 positions must not override the canonical K-Trader Risk Manager. Production risk limits remain governed only by canonical project configuration.

### Research features to retain

- `risk_per_trade_pct`
- `portfolio_open_risk_pct`
- `daily_realized_R`
- `daily_loss_streak`
- `correlated_family_exposure`
- `symbol_cluster_exposure`

The existing family-first dependence control is more important than simply counting nominal positions.

## 5. VSA knowledge base — useful as context scorer, not yet a standalone signal engine

The VSA knowledge document defines:

- bullish contextual signals: NS, Test, Selling Climax, Stopping Volume;
- bearish contextual signals: ND, Upthrust, Buying Climax;
- stronger quality when signals occur at a key level, have confirmation, and are not mid-range;
- trend alignment as positive context;
- ATR-used buckets as a quality factor;
- A+ as a cluster of level + VSA + trend + confirmation + ATR + liquidity.

This architecture is conceptually compatible with current K-Trader research, but the precise VSA pattern definitions are not yet deterministic enough for unbiased backtesting.

### Proposed integration

First implement VSA as recorded feature scores, not hard gates:

- `vsa_no_demand_score`
- `vsa_no_supply_score`
- `vsa_test_score`
- `vsa_upthrust_score`
- `vsa_buying_climax_score`
- `vsa_selling_climax_score`
- `vsa_stopping_volume_score`
- `vsa_confirmation_bars`
- `vsa_at_level`
- `vsa_cluster_score`

Before any of these can become a hard rule, define each pattern quantitatively using spread, close location, relative volume, level interaction and confirmation bars, freeze the definitions, and test OOS.

## 6. Main conflicts with current evidence

### Conflict A — short stop is always better

Legacy material emphasizes shorter stops because they make 3R easier to reach. Current v2/v2.1 evidence shows that too-narrow stop-distance units can be harmed disproportionately by noise and costs. Therefore K-Trader should optimize stop placement for structural invalidation plus cost/noise robustness, not simply minimize stop size.

### Conflict B — ATR as a universal hard filter

Previous K-Trader replay did not prove ATR-rejected setups were inferior. The uploaded knowledge argues for ATR-used limits. Resolution: ATR and remaining-range logic should be reintroduced as explicit measurable features, then tested before becoming a hard gate.

### Conflict C — volume/VSA as mandatory

Current benchmark did not show a simple relative-volume threshold to be robust enough as a hard gate. VSA may add value only when combined with structure/levels. Therefore VSA is initially contextual/scoring evidence.

### Conflict D — one horizon for all trades

The uploaded material is largely intraday-oriented. K-Trader requires profile-specific horizons.

## 7. Proposed multi-horizon architecture

These are research defaults, not production-approved constants.

### FAST

- context: H1 / M15
- trigger: M5
- intended hold: minutes to a few hours
- provisional maximum hold: 4h
- setup TTL and stop scale derived from M5/M15 volatility and structure

### INTRADAY

- context: H4 / H1
- trigger: M15
- intended hold: same trading day
- provisional maximum hold: 8-12h
- current v2.1 research profile belongs here

### SWING

- context: D1 / H4
- trigger: H1
- intended hold: multiple sessions
- provisional maximum hold: 2-4 days
- funding and overnight regime risk become materially more important

### POSITION

- context: W1 / D1
- trigger: H4
- intended hold: multi-day / multi-week
- provisional maximum hold: 7-21 days
- funding, regime change and higher-timeframe structural invalidation dominate

The final maximum hold for every profile should be learned from trade-duration/MFE/MAE distributions, not fixed forever by these starting values.

## 8. Recommended next research version

Do NOT modify `candidate_rule_set_v2_1` in place.

Create a new version that preserves the current core:

`trend -> pullback -> reclaim/continuation -> structural stop -> 3R`

and adds a structured evidence layer:

1. fixed-vs-floating level context;
2. distance to next structural obstacle in R;
3. clean ATR5D / range-used features;
4. VSA feature scores around the level;
5. horizon-specific profile;
6. current cost-aware and family-first risk controls.

Only the simplest objectively measurable constraints should be candidate hard gates. All other legacy rules start as recorded features and must earn promotion through OOS evidence.

## 9. Knowledge-source status

Recommendation for the custom GPT Knowledge store after this audit:

- do not treat the five uploaded files as canonical operational instructions;
- retain them only as historical/research reference if desired;
- canonical active truth should live in the K-Trader repository;
- any future GPT knowledge file should point to current canonical strategy/risk documents and clearly label historical sources as non-authoritative.
