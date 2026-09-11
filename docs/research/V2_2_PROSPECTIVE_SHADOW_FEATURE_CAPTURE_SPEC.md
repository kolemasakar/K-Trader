# v2.2 Prospective Shadow Feature Capture

Date: 2026-09-11
Status: RESEARCH INFRASTRUCTURE / FROZEN v2.2 / NO LIVE TRADING CHANGE

## Purpose

Capture fresh post-freeze observations for the already frozen `candidate_rule_set_v2_2` while attaching the new diagnostic feature layers. This is shadow research only.

First fully prospective signal-bar open boundary:

`2026-09-11T20:00:00Z`

## Frozen execution logic

The runner must import and use the exact frozen v2.2 harness already present in the research artifact tree. It must not duplicate or alter the candidate thresholds.

Frozen gates remain:
- H1 EMA20/EMA50 trend + slope logic inherited from v2;
- H1 EMA separation / ATR >= 0.20;
- M15 signal body/range <= 0.60;
- next-open adverse slippage;
- executed structural risk distance >= 1.25%;
- v2.2 structural-space gate using the frozen H1 pivot-cluster detector and >=3R open space rule;
- target 3R;
- 8h max hold for the frozen INTRADAY candidate.

## Shadow feature capture

For every post-boundary frozen-v2.2 signal that reaches the entry-evaluation stage, record:

- exact symbol and signal/entry timestamps;
- frozen v2.2 causal features;
- risk distance and structural-space result;
- Level Context v2 H1 features;
- strict confirmed-level-break diagnostics;
- broken-level traversal/revisit features;
- exact bundle/source provenance.

Status is one of:
- `ELIGIBLE_SHADOW_SETUP`;
- `REJECT_MIN_RISK_DISTANCE`;
- `REJECT_LEVEL_CONTEXT_UNAVAILABLE`;
- `REJECT_STRUCTURAL_SPACE`.

The runner does not change production and does not send orders.

## Data policy

- fixed 19-symbol primary research panel from the benchmark protocol;
- provider `binance_usdm`;
- only closed candles;
- no look-ahead;
- next-open entry evaluation requires the next M15 bar to exist in the captured bundle;
- new bundles must record an explicit `as_of`/bundle manifest;
- no panel substitution for symbols that fail history export.

## Outcome policy

Initial capture may contain unresolved eligible setups. Outcome resolution is a separate causal pass after sufficient future bars exist.

Future MFE/MAE outcome capture will add:
- MFE/MAE;
- 1/2/4/8-bar early progress checkpoints;
- time-to-0.5R/1R/2R/3R;
- MFE peak age and giveback;
- fees/slippage/funding;
- realized R;
- unique setup-family id.

No unresolved setup may be treated as a WIN/LOSS.

## Evidence boundary

Existing development/validation results are diagnostic history. New post-`2026-09-11T20:00:00Z` resolved setup families are the required fresh evidence stream for any future version based on `clean_break_no_revisit` or early-progress behavior.

Holdout remains unopened.
