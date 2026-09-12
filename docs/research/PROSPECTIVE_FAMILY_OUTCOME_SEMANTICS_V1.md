# Prospective Family Outcome Semantics v1

Status: **PREREGISTERED / RESEARCH ONLY**  
Applies to: frozen `candidate_rule_set_v2_2` prospective evidence after boundary `2026-09-11T20:00:00Z`.

## Purpose

Prevent correlated entries from inflating evidence counts or allowing post-outcome cherry-picking.

## Immutable evidence unit

Primary evidence unit = **unique `setup_family_id`**.

A family may contain one or more eligible shadow observations. Multiple observations from one family are not independent evidence.

## Family representative

For each `setup_family_id`, the **primary representative** is the earliest eligible observation by:

1. `entry_time` ascending;
2. if tied, `signal_bar_open_time` ascending;
3. if still tied, deterministic lexical order of `(symbol, side)`.

The representative is fixed once first observed and is never replaced because of later performance.

All later eligible observations in the same family are `CORRELATED_DIAGNOSTIC_ONLY`.

## Family resolution

Family outcome = outcome of the primary representative only.

Until the primary representative reaches a terminal state, the family is `UNRESOLVED`, even if a secondary observation reaches a terminal state earlier.

Terminal states follow the exact frozen v2.2 execution path:

- `GAP_STOP`;
- `GAP_TARGET`;
- `STOP`;
- `TARGET`;
- `TIME_EXIT` after `32 x M15` bars / 8h.

Same-bar ambiguity preserves frozen semantics: **STOP is evaluated before TARGET**.

No discretionary early exit, break-even move, trailing stop, profit protection or parameter change is allowed for family-resolution evidence.

## Execution and economics

Use frozen v2.2 base execution assumptions:

- target = `3R`;
- entry/exit adverse slippage = base `2 bps` each execution side through the frozen harness convention;
- fee = `5 bps` per side through the frozen harness convention;
- provider-recorded funding applicable between entry and exit;
- `realized_R = net_return_pct / initial_risk_pct`.

Record both raw path outcome and net economics.

## Required observation fields

For every eligible observation store at minimum:

- `setup_family_id`;
- representative/secondary role;
- symbol/side;
- signal and entry timestamps;
- entry/SL/3R target;
- initial risk %;
- terminal state/time/price when resolved;
- gross/net return and `realized_R`;
- fee/slippage/funding components;
- MFE/MAE;
- time-to-0.5R/1R/2R/3R when reached;
- hold bars;
- exact frozen harness/protocol hashes;
- source bundle provenance.

## Evidence gates

Count only resolved primary representatives:

- `<30` unique resolved families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

## Prohibited post-hoc actions

Do not:

- choose the best entry inside a family after outcome is known;
- count multiple observations from one family as independent wins/losses;
- replace a losing primary representative with a later winning observation;
- change family IDs using outcome information;
- change v2.2 thresholds, RR, 8h max hold, SL or execution rules while accumulating this evidence;
- use holdout for tuning.

## Current governance

This document changes **research accounting only**. It does not change production, trading eligibility, the frozen v2.2 signal generator or the holdout authorization state.
