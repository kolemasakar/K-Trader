# Level Context Layer v2 + MFE/MAE Diagnostics — Research Plan

Date: 2026-09-11
Status: APPROVED RESEARCH PLAN / v2.2 FROZEN / HOLDOUT UNTOUCHED / NO PRODUCTION CHANGE

## Purpose

Run two parallel diagnostic tracks without modifying frozen `candidate_rule_set_v2_2`:

A. richer deterministic structural-context research (`Level Context Layer v2`);
B. MFE/MAE and duration diagnostics on frozen v2.2 and comparable historical setup families.

These tracks may generate hypotheses for a future version, but they may not mutate v2.2 in place.

---

# Track A — Level Context Layer v2

## Problem

Current `h1_pivot_cluster_v1` is intentionally minimal. In v2.2 non-holdout, 35/37 completed trades were classified as `open_space`, indicating that the detector is too sparse to represent the full structural environment.

## Design goals

The new layer should be:
- causal;
- deterministic;
- closed-bar only;
- profile-aware;
- independent of outcome labels during feature construction;
- capable of representing both confirmed levels and ambiguous/floating zones;
- auditable from raw OHLCV.

## Candidate feature families

### 1. Trend-break / first-pullback structure
Record:
- break_level_price;
- break_direction;
- break_age_bars;
- post-break_new_extreme;
- first_pullback_level;
- distance_from_entry_R;
- reclaim/retest state.

### 2. Mirror levels
Record:
- prior support/resistance role;
- role-change count;
- last role-change age;
- touches before/after role change;
- distance in ATR and R.

### 3. Repeated-touch / limit levels
Record:
- clustered touch count;
- body-touch count;
- wick-touch count;
- tolerance-normalized dispersion;
- penetration depth;
- exact/non-exact repeat behavior.

No rule such as “3 exact touches” becomes a hard gate unless independently validated.

### 4. Consolidation / trading-zone boundaries
Record:
- local high/low boundary;
- width in ATR;
- duration bars;
- close-density near boundary;
- breakout/re-entry count;
- whether entry is inside, at boundary, or outside the zone.

### 5. False-break features
Record:
- penetration beyond level in ATR;
- close-back-inside flag;
- confirmation within 1-2 closed bars;
- follow-through magnitude;
- false-break age.

### 6. Rejection-tail features
Record:
- upper/lower wick fraction;
- wick/body ratio;
- wick/range percentile;
- close location;
- interaction with a structural level.

### 7. Level age and strength
Record:
- age bars;
- touch count;
- number of clean defenses;
- number of penetrations;
- last interaction age;
- whether level initiated movement to a new extreme.

### 8. Floating/forming-zone detection
Record a deterministic ambiguity score based on:
- repeated closes around a price band;
- overlapping ranges;
- directional inefficiency;
- boundary instability;
- lack of clean post-level acceptance.

Output should include both boolean and continuous features where possible, e.g.:
- `floating_zone_flag`;
- `floating_zone_score`.

### 9. Structural obstacle distance
For both sides record:
- nearest obstacle price;
- obstacle type;
- obstacle confidence/strength features;
- distance in ATR;
- distance in initial R;
- whether planned 1R/2R/3R targets fit before it.

## Multi-timeframe policy

For INTRADAY research:
- H4/H1 context features may describe major structure;
- M15 is the trigger timeframe;
- every HTF feature must use the latest fully closed bar known at the M15 decision time.

Future FAST/SWING/POSITION profiles may use different structural TFs, but must have separately versioned definitions.

## No-look-ahead rule

A pivot requiring future bars may be considered confirmed only after all confirming bars are closed and therefore known at the decision timestamp.

No feature may use future extremes, future role changes or later touch counts.

## Initial evaluation policy

Level Context v2 starts as a feature layer, not a trading gate.

Evaluate:
- feature availability;
- deterministic reproducibility;
- distribution stability;
- correlation/redundancy;
- outcome stratification on development diagnostics;
- later prospective/OOS incremental value.

Do not tune thresholds repeatedly on validation.

---

# Track B — MFE/MAE Diagnostics

## Purpose

Determine whether v2.2 losses and time exits are primarily driven by:
- poor entry selection;
- stop placement;
- insufficient holding time;
- failure to capture favorable excursion;
- structural context;
- execution costs.

This is diagnostic work, not permission to change v2.2.

## Required metrics per completed trade

Using the exact executed entry and initial risk unit:
- `MFE_R`;
- `MAE_R`;
- `time_to_MFE_bars`;
- `time_to_MAE_bars`;
- `time_to_0_5R`;
- `time_to_1R`;
- `time_to_2R`;
- `time_to_3R`;
- maximum favorable excursion before first adverse 0.5R/1R;
- maximum adverse excursion before first favorable 1R/2R;
- whether stop trade previously reached +0.5R/+1R/+2R;
- whether target trade first experienced deep MAE;
- excursion at TIME_EXIT;
- final 4/8 M15-bar slope before TIME_EXIT;
- costs expressed in R.

## Excursion calculation rules

LONG:
- favorable excursion uses subsequent highs relative to executed entry;
- adverse excursion uses subsequent lows.

SHORT:
- favorable excursion uses subsequent lows;
- adverse excursion uses subsequent highs.

Normalize all excursions by the frozen initial risk distance from executed entry to initial structural SL.

Use only the bars actually available during the trade path. Do not inspect bars after the frozen exit when computing in-trade MFE/MAE.

A separate counterfactual post-exit study, if ever performed, must be explicitly labeled and must not be mixed with in-trade metrics.

## Required diagnostic cuts

Report at minimum by:
- development / validation / non-holdout;
- exit reason;
- LONG / SHORT;
- symbol;
- risk-distance bucket;
- H1 trend-strength bucket;
- structural-space/open-space state;
- hold-duration bucket;
- funding-cost bucket if material.

If Level Context v2 features become available, join them causally for diagnostics without altering historical trade execution.

## Key questions

1. How many STOP trades achieved meaningful positive MFE first?
2. Are losses immediate failures or late reversals?
3. Are TIME_EXIT winners still trending favorably at exit?
4. Does 8h truncate trades that commonly reach 3R shortly afterwards? This may be studied only as a clearly labeled counterfactual, not as evidence to retroactively improve v2.2.
5. Is the 1.25% minimum risk-distance gate still justified across regimes?
6. Are target hits concentrated in specific structural contexts?
7. Does large MAE identify weak Level Context states before entry?

## Statistical policy

Primary evidence unit remains unique setup family.

Do not create a new hard rule from small subgroup counts.

Use diagnostics to create a future preregistered hypothesis only when:
- effect direction is interpretable;
- sample is not trivially small;
- no single symbol dominates;
- the feature is causal and implementable at decision time.

---

# Parallel execution order

1. Build deterministic Level Context Layer v2 feature extractor.
2. Build MFE/MAE diagnostic extractor independently.
3. Unit-test causality and reproducibility of both.
4. Run MFE/MAE on frozen v2.2 completed trades.
5. Attach Level Context v2 features to the same frozen trade decisions without changing trade eligibility.
6. Produce diagnostic report.
7. Identify only a small set of candidate hypotheses.
8. If justified, create a new preregistered strategy version; never rewrite v2.2.

## Hard boundaries

- v2.2 remains frozen;
- holdout remains closed;
- validation is not fresh OOS after it has been inspected;
- production remains unchanged;
- no automatic strategy/risk/SL parameter mutation;
- no cherry-picking symbols or regimes to claim promotion.

## Completion criteria for this research stage

Track A complete when:
- feature definitions are deterministic and documented;
- causal tests pass;
- feature extraction is reproducible from stored histories;
- no look-ahead violations are found.

Track B complete when:
- every frozen v2.2 completed trade has MFE/MAE/time-path metrics where history permits;
- aggregate and subgroup diagnostics are generated;
- counterfactual metrics, if any, are separated from actual-path metrics;
- results are documented without changing v2.2.