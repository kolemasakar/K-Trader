# Frozen v2.2 Causal Rolling-Context Replay v1 — Preregistered Correction Protocol

Date: 2026-09-13
Status: PREREGISTERED CORRECTION / PRE-OUTCOME / RESEARCH ONLY / HOLDOUT UNTOUCHED / PRODUCTION UNCHANGED

## Purpose

Correct the Historical Expansion / long-window robustness methodology after identifying that the frozen v2.2 structural-space gate scans the full H1 array supplied to the harness. Supplying 2,000–9,060 H1 bars therefore changes the effective structural context relative to the bounded prospective pipeline.

This protocol is committed before any corrected replay outcome is inspected. It does not change `candidate_rule_set_v2_2`; it changes only the historical replay orchestration so each decision receives the same bounded causal information budget intended by the prospective pipeline.

## Frozen candidate identity

- strategy: `candidate_rule_set_v2_2`
- frozen harness SHA256: `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- target: `3R`
- max hold: `32 x M15 = 8h`
- H1 EMA20/EMA50 separation / ATR14 >= `0.20`
- M15 signal body/range <= `0.60`
- executed structural risk distance >= `1.25%`
- H1 structural-space gate: open space OR next confirmed obstacle >= `3R`
- same-bar ambiguity: STOP first
- fee/funding/slippage: unchanged frozen economics

No trading parameter may be modified by this correction.

## Methodology defect being corrected

Frozen `level_features()` calls `_confirmed_pivots(h1, decision_idx)` and the pivot detector scans from the beginning of the supplied H1 array through the causal decision index.

Therefore historical evaluators that supplied thousands of H1 bars changed the set of remembered structural levels and are not semantically comparable with the bounded prospective pipeline.

The same principle applies to indicator initialization on M15: the prospective capture provides a bounded M15 bundle rather than an arbitrarily long history.

Accordingly, prior Historical Expansion v1 and Historical Robustness Windows v1 outcomes are superseded for inference until corrected replay results exist.

## Causal rolling information budget

For every historical M15 decision bar `t`, construct a decision-local snapshot using only data available by the close of `t`:

- M15 context: at most the latest `400` closed M15 bars ending at `t`, inclusive;
- H1 context: at most the latest `300` closed H1 bars whose `close_time <= close_time(t)`;
- no future M15 or H1 candle may enter signal, indicator, trend, level or structural-space calculations;
- M15 indicators are recomputed on that local M15 snapshot;
- H1 indicators are recomputed on that local H1 snapshot;
- the original frozen `v.signal_at()` function is called on the local snapshot;
- the original frozen `level_features()` function is called on the same decision-local H1 snapshot at next-bar entry;
- pending entry remains next M15 open, exactly as in the frozen harness;
- position management, target, stop, STOP-first semantics, max hold, fee, funding and slippage remain the frozen implementation.

This is an orchestration correction, not a strategy rule change.

## Episode identity normalization

The frozen signal function emits `episode_key` and `pullback_episode_index` relative to the supplied M15 array. Because the rolling snapshot start moves over time, the replay engine must remap this local episode identity to the corresponding absolute historical M15 index before applying one-position-per-episode suppression.

This normalization preserves the original semantic episode while preventing artificial duplicate/re-entry behavior caused only by moving array offsets.

## Historical cutoff and isolation

Hard external cutoff remains:

`2026-09-05T14:45:00Z`

No scored candle may close at or after this cutoff.

The existing benchmark holdout remains `UNTOUCHED / NOT AUTHORIZED` and may not be opened or queried for outcomes.

Production remains unchanged and read-only.

## Data roots and frozen provenance

Use the already collected provider-recorded Binance USDM historical dataset:

`/data/research/phase11g/historical_robustness_v1_20260905T144500Z`

Pre-outcome dataset summary SHA256:

`9b1a724247d351068f120f52ef91fc78e1c481e6d66a6efd4ce7925df9bae80b`

Funding summary SHA256:

`a60e712dc2bba23707fe89af94e092df796823fabfbe521e8947e582e22eba70`

No symbol is selected or removed by observed trading performance.

## Fixed evaluation windows

All windows end at the same hard cutoff:

- `P25`: final `2400` M15 bars = 25 days — corrected replacement for Historical Expansion v1;
- `R90`: final `8640` M15 bars = 90 days;
- `R180`: final `17280` M15 bars = 180 days;
- `R365`: final `35040` M15 bars = 365 days.

Readiness remains outcome-free:

- P25/R90/R180 use all 19 frozen-panel symbols if causal context and funding are available;
- R365 uses the pre-outcome readiness cohort already established by data age; `AKEUSDT` and `METUSDT` are age-limited and excluded from R365 only;
- no substitution is allowed.

## Parity / acceptance gates before interpreting outcomes

The corrected evaluator must fail closed unless all of the following pass:

1. Frozen harness SHA exactly matches the accepted SHA.
2. Local signal generation delegates to the frozen `v.signal_at()` implementation.
3. Structural-space evaluation delegates to frozen `level_features()`.
4. Every scored signal records context counts `M15 <= 400` and `H1 <= 300`.
5. Latest-bar parity check against a canonical prospective 400-M15 / 300-H1 snapshot passes for every available frozen-panel symbol: same signal/no-signal decision and, when present, identical side, stop and frozen signal features modulo explicitly normalized local indices.
6. Hard historical cutoff isolation passes.
7. Official funding coverage passes.
8. Existing holdout remains unopened.

If parity fails, no corrected historical P&L is accepted.

## Metrics

For each accepted window report:

- cohort and coverage;
- completed trades / censored positions;
- wins/losses, win rate;
- expectancy_R after frozen costs;
- profit_factor_R;
- chronological trade-stream drawdown;
- STOP/TARGET/TIME_EXIT composition;
- LONG/SHORT counts and expectancy;
- per-symbol trade count and expectancy;
- time-block stability;
- base versus stress slippage;
- context-bound audit maxima/minima;
- hashes of reports and trade files.

## Interpretation guardrails

Corrected historical replay is historical evidence only. It is not added to prospective family counts.

No corrected result authorizes in-place retuning of frozen v2.2. Any future rule change requires a new version, preregistration and fresh OOS/prospective validation.

The previous unbounded-context 25d/90d/180d/365d outcomes remain preserved for audit but are marked `SUPERSEDED / METHODOLOGY INVALID FOR INFERENCE`.

## Next state transition

Only after parity passes and corrected P25/R90/R180/R365 reports are generated may Track B return to an accepted evidence state. Track A prospective accumulation remains independent and unchanged throughout.