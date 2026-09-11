# Candidate v2.2 — Prospective Shadow Protocol

Date: 2026-09-11
Status: FROZEN PROSPECTIVE RESEARCH PROTOCOL / NO PRODUCTION CHANGE

## Freeze point

Executable candidate commit:
- `9abb05d88912293cee3c254dd427a7127ce5bcc7`
- commit time: `2026-09-11T19:52:22Z`

To avoid partial-bar contamination, the first fully prospective M15 bar is the bar opening at:
- `2026-09-11T20:00:00Z`

No bar that began before the frozen executable commit may be used as a new prospective signal bar.

## Candidate

Use `candidate_rule_set_v2_2` exactly as frozen.

No parameter changes are allowed during this prospective accumulation period.

## Mode

Research/shadow only.

- no live order submission;
- no production strategy change;
- no Risk Manager change;
- no execution/deployment mutation;
- no holdout opening.

## Universe

Use the same frozen primary 19-symbol benchmark panel unless a symbol lacks sufficient causal history or is no longer available from the same provider/market type.

Do not replace failed/missing symbols with performance-selected substitutes during the same prospective study.

## Data rules

- provider: `binance_usdm` for the frozen study unless a new version explicitly changes provider;
- market type must remain consistent;
- closed bars only;
- causal MTF alignment only;
- no look-ahead;
- record exact `as_of`, data hashes and config/strategy hashes;
- incomplete history => `DATA_INSUFFICIENT`, not inferred values.

## Logging scope

Log three classes:

1. `ELIGIBLE_V2_2`
   - passes complete v2.2 rules;

2. `NEAR_MISS_STRUCTURAL_SPACE`
   - passes inherited v2.1 rules but fails the v2.2 structural-space gate;

3. `BASE_NEAR_MISS`
   - reaches a defined pre-entry stage but fails another explicit inherited v2.1 gate.

The rejected groups are retained for causal comparison; they are not simulated as live trades unless the protocol explicitly defines a shadow outcome calculation.

## Required feature record

For each candidate/near-miss, store at least:

- symbol;
- side;
- strategy version;
- profile;
- signal time and prospective `as_of`;
- setup-family id;
- H1 trend/separation features;
- M15 pullback/reclaim features;
- executed/simulated entry;
- structural SL and initial risk;
- next confirmed H1 level distance in R;
- `OPEN_SPACE` flag;
- level touch count/mirror flag;
- floating-zone diagnostic;
- ATR-used / clean ATR5D when available;
- H4/D1 alignment as features only;
- VSA features as features only when deterministically available;
- relative volume;
- fees/slippage/funding assumptions and realized values;
- MFE/MAE;
- exit reason;
- realized R;
- hold duration and time-to-target/time-to-stop/time-exit;
- exact data/config/code hashes.

## Outcome rules

For `ELIGIBLE_V2_2` shadow trades, use the frozen executable rules:

- next executable M15 open;
- adverse base slippage;
- structural stop;
- 3R target;
- stop-first same-bar ambiguity;
- maximum hold 8h;
- actual funding where available;
- current fee assumptions unchanged.

Do not change max hold during this protocol.

## Evidence gates

Primary unit = unique resolved setup family.

- `<30`: observation only;
- `30–49`: diagnostics only;
- `50–99`: component/ablation proposals allowed, no production promotion;
- `>=100` diverse resolved families: versioned recalibration proposal may be considered.

The 50% WR target is not evaluated in isolation. Always report:
- WR;
- expectancy_R;
- PF_R;
- avg win/loss R;
- drawdown R;
- MFE/MAE;
- costs;
- side/symbol/regime concentration.

## Anti-overfit rule

Do not alter v2.2 based on early prospective outcomes and continue calling the modified system v2.2.

Any rule change creates a new candidate version with a new freeze point. Data observed before that new freeze can be used for research/diagnostics but not as fresh prospective validation of the changed version.

## Holdout boundary

The existing benchmark holdout remains untouched.

Prospective shadow evidence does not automatically authorize holdout opening. Holdout may be opened only when the preregistered promotion gate explicitly passes.
