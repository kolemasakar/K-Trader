# Frozen v2.2 Historical Expansion v1 — Methodology Supersession Notice

Date: 2026-09-13
Status: SUPERSEDED FOR INFERENCE / AUDIT RETAINED

## Decision

The following historical result sets are no longer accepted evidence for inference about frozen `candidate_rule_set_v2_2`:

- `/data/research/phase11g/historical_expansion_v1_20260905T144500Z/results_v1`
- `/data/research/phase11g/historical_robustness_v1_20260905T144500Z/results_v1`

The underlying provider data, funding exports, reports, hashes and repository artifacts are retained unchanged for auditability.

## Reason

The frozen H1 structural-space detector scans all H1 bars supplied before the causal decision index. The first Historical Expansion evaluator supplied up to `2000` H1 bars and the long-window evaluator supplied up to `9060` H1 bars, while the prospective pipeline is bounded to `300` H1 bars. This changes the remembered structural-level set and therefore the effective gate.

The historical evaluators also used much longer M15 arrays than the prospective `400`-bar M15 bundle, which can alter indicator initialization. Consequently the old 25d/90d/180d/365d results are not semantically comparable with the intended bounded prospective information budget.

## Superseded documents/results

The following artifacts remain historical records but must be read as `METHODOLOGY REVIEW / SUPERSEDED FOR INFERENCE`:

- `docs/research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_PROTOCOL.md`
- `docs/research/FROZEN_V2_2_HISTORICAL_ROBUSTNESS_WINDOWS_V1_PROTOCOL.md`
- `docs/checkpoints/2026-09-13_FROZEN_V2_2_DUAL_TRACK_HISTORICAL_EXPANSION_V1.md`
- `research/strategy_benchmark_v1/historical_expansion_v2_2_v1.py`
- `research/strategy_benchmark_v1/historical_robustness_v2_2_v1.py`

In particular, the previously reported `+0.1863256189R` 25-day expectancy and the unbounded-context 90/180/365-day results must not be used for promotion, rejection, retuning or historical/prospective comparison.

## Replacement methodology

Canonical correction protocol:

`docs/research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`

Protocol commit:

`065dd43a029bb85c427996da3d26a5c59b322728`

Corrected evaluator:

`research/strategy_benchmark_v1/historical_causal_rolling_replay_v1.py`

Evaluator commit:

`3687df3a9a8f4dbe0cc9cea4183ea4fceb7bbc0e`

The replacement replay uses a causal moving information budget of at most `400` M15 bars and `300` H1 bars at each decision and delegates actual frozen signal/structural calculations to the accepted harness.

## Unchanged governance

- frozen strategy remains `candidate_rule_set_v2_2`;
- frozen harness SHA remains `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- prospective Track A remains independent;
- existing benchmark holdout remains `UNTOUCHED / NOT AUTHORIZED`;
- production remains unchanged and read-only;
- no historical result counts toward prospective family thresholds.
