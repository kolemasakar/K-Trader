# K-Trader Current State

Updated: 2026-09-11  
Research checkpoint: `docs/checkpoints/2026-09-11_V2_2_PARALLEL_RESEARCH_CHECKPOINT.md`

## Production state

Production remains unchanged by strategy research.

Verified 2026-09-11 after the parallel-research batch:

- deployed SHA: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- `/health`: `status=ok`;
- mode: `read_only`;
- `data_ready=true`;
- `scanner_status=DEGRADED`;
- provider: `binance_usdm`;
- Action authentication enabled.

`DEGRADED` remains a known fail-closed/history-readiness condition and does not by itself mean the entire runtime is unavailable.

No production code, deployment, risk, execution or trading semantics were changed by the independent strategy research.

## Canonical/research separation

Production remains GitHub/deployment controlled. Independent strategy work is isolated on:

`research-strategy-benchmark-v1`

The research branch does not imply production activation.

Canonical production FAST behavior remains governed by the deployed system and `docs/TRADING_HORIZON_PROFILES.md`.

New INTRADAY/FAST/SWING/POSITION strategy architecture is research-only unless separately approved.

## Frozen INTRADAY candidate

Current strongest frozen research candidate:

`candidate_rule_set_v2_2`

Frozen executable harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Frozen path:

`H1 direction/context -> M15 pullback -> M15 reclaim/continuation -> structural SL -> H1 structural-space gate -> nominal 3R`

Inherited quality gates:

- `abs(EMA20_H1 - EMA50_H1) / ATR14_H1 >= 0.20`;
- M15 signal body/range <= `0.60`;
- executed structural risk distance >= `1.25%` of entry.

Frozen structural-space layer:

- causal H1 swing radius `2`;
- clustering tolerance `0.20 * ATR14_H1`;
- confirmed cluster requires >=2 pivots;
- no obstacle ahead or nearest confirmed obstacle >=`3R`.

Frozen max hold:

`32 x M15 = 8h`

This 8h rule belongs only to this exact INTRADAY candidate and is not a universal profile limit.

## v2.2 pre-holdout result

| Segment | Trades | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 23 | 47.83% | +0.1003R | 1.1818 |
| Validation | 10 | 30.00% | +0.2507R | 1.3941 |
| Non-holdout | 37 | 45.95% | +0.2888R | 1.5592 |
| Stress non-holdout | 37 | 43.24% | +0.2741R | 1.5235 |

Promotion gate: **FAIL**.

Reasons:

- non-holdout sample <100;
- validation sample <30;
- non-holdout WR <50%;
- validation WR <50%.

Therefore:

- `production_approved=false`;
- `holdout_authorized=false`;
- holdout remains untouched.

Positive expectancy/PF does not override the preregistered gates.

## Post-v2.2 diagnostics

Detailed results:

`docs/research/PARALLEL_RESEARCH_RESULTS_2026-09-11.md`

### Level Context + MFE/MAE

Completed:

- Level Context v2;
- Level Context v2.1 strict-break diagnostics;
- broken-level traversal lifecycle;
- MFE/MAE stages 1–3;
- canonical static-level parity.

Main observations:

- most STOP trades fail early rather than first producing large favorable excursion;
- TARGET trades usually show strength quickly;
- TIME_EXIT trades are often positive but may give back meaningful MFE;
- `clean break -> no revisit before entry` is the strongest current post-hoc structural hypothesis;
- it is not a v2.2 hard gate.

Canonical static clustering does not reproduce Level Context v2 discrimination: canonical static clustering saw open-space on 35/37 non-holdout trades while Level Context v2 saw H1 open-space on 22/37.

### Portfolio/correlation

- 37 historical trades -> 36 diagnostic correlation families under the current definition;
- only one multi-trade diagnostic family;
- maximum simultaneous positions = 5;
- top-symbol trade share ~16.2%;
- main high-correlation traded-symbol cluster: `1000PEPEUSDT / DOGEUSDT / TRUMPUSDT`.

This grouping is diagnostic and is not yet canonical setup-family semantics.

### Execution economics

- median explicit fee+funding cost ~`0.041R`;
- median zero-to-base full-path execution drag ~`0.009R`;
- median combined explicit+base execution burden ~`0.051R`;
- base-to-stress adds ~`0.015R` median full-path drag.

Execution changes can alter path identity/eligibility; they must be tested by full replay rather than subtracting a constant cost.

No new min-stop threshold is authorized from these diagnostics.

### VSA / volume

Heuristic VSA/volume features were studied as diagnostics only.

Canonical raw VSA parity used the exact current raw detection rules from `src/ktrader/evidence/vsa.py`.

Result: no evidence supports mandatory raw-VSA direction matching. Raw VSA remains contextual and requires regime/level/confirmation logic before it can be considered validated evidence.

### Robustness warning

Historical non-holdout economics are materially supported by IOSTUSDT:

- removing IOSTUSDT leaves expectancy positive but reduces it from ~`+0.289R` to ~`+0.046R`;
- PF falls to ~`1.079`;
- WR falls to ~`39.4%`.

This weakens current confidence in symbol robustness. It is not a reason to post-hoc remove or require IOSTUSDT.

## Prospective frozen-v2.2 evidence

Frozen boundary:

`2026-09-11T20:00:00Z`

Prospective capture is provider-recorded and immutable. The runner now:

- exports the fixed panel through canonical K-Trader history tooling;
- records bundle, protocol and frozen-harness hashes;
- fails closed on incomplete/mislaid bundles;
- records invalid attempts separately;
- updates a de-duplicated prospective ledger.

### Valid snapshot 1 — 20:30Z

- 19/19 symbols;
- 19 causally entry-evaluable symbol-bars;
- 0 frozen-v2.2 events;
- 0 eligible families.

### 20:45Z attempt 1

Infrastructure-invalid due incorrect bundle directory layout.

Status:

`INVALID_INFRASTRUCTURE`

It is explicitly rejected by the ledger and is not evidence.

### Valid snapshot 2 — 20:45Z retry 2

- 19/19 symbols;
- 38 causally entry-evaluable symbol-bars;
- signal range: M15 opens `20:00` through `20:15` UTC;
- 0 frozen-v2.2 events;
- 0 eligible families;
- exact frozen harness SHA preserved.

Current independent evidence state:

`NO_ELIGIBLE_FAMILIES_YET`

## Cross-provider portability

Second implemented provider: `bybit_linear`.

Fixed-panel availability:

- available: 16/19;
- unavailable: `PUMPUSDT`, `RAYSOLUSDT`, `VTHOUSDT`.

Synchronized 20:45Z comparison on the fixed 16-symbol intersection:

- median M15 return correlation: ~`0.9984`;
- median absolute close basis: ~`4.32 bps`;
- Binance frozen post-boundary events: 0;
- Bybit frozen post-boundary events: 0.

This is data/signal portability evidence only, not profitability validation.

## Profile research architecture

Research spec:

`docs/research/PROFILE_RESEARCH_SPECS_FAST_SWING_V0.md`

Current research envelopes:

| Profile | Context | Setup/trigger | Research envelope |
|---|---|---|---|
| FAST | H1/M15 | M15 -> M5 execution | up to ~4h |
| INTRADAY | H4/H1 conceptual; frozen v2.2 currently H1 | M15 | ~8–12h architecture; frozen v2.2 uses 8h |
| SWING | D1/H4 | H1 | ~2–4 days |
| POSITION | W1/D1 | H4 | ~7–21 days, architecture reserved |

These research envelopes do not modify the existing production FAST TTL contract or earlier lifecycle studies.

TTL before entry and max-hold after entry remain separate concepts.

## Knowledge governance

Legacy Knowledge files remain:

`HISTORICAL / RESEARCH REFERENCE`

Do not automatically promote old:

- ATR-used thresholds;
- fixed SL percentages/pips/cents;
- old risk percentages;
- mandatory VSA/volume filters;
- old TF/holding assumptions.

They may generate hypotheses/features only.

## Evidence governance

Primary evidence unit = unique resolved setup family.

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Every strategy-rule change requires:

- new strategy version;
- preregistration;
- causal full-path backtest/walk-forward;
- fresh OOS/prospective evidence;
- holdout only after predefined gates;
- explicit promotion decision.

Validation/holdout must not be repeatedly mined to tune the same version.

## Current safe work boundary

Continue:

- exact frozen-v2.2 prospective shadow capture;
- provenance/ledger hardening;
- feature observation without changing eligibility;
- separate FAST/SWING data-readiness/specification work;
- portfolio/correlation research.

Do not change frozen v2.2 using the current seen data:

- no clean-break/no-revisit hard gate;
- no early-progress exit rule;
- no new min-risk threshold;
- no volume/VSA hard gate;
- no IOST inclusion/exclusion rule;
- no RR or 8h retuning;
- no holdout opening.

## Next hard evidence milestone

`>=30 unique resolved prospective frozen-v2.2 setup families`

Until then prospective evidence remains observation-only.
