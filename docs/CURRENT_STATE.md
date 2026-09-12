# K-Trader Current State

Updated: 2026-09-12  
Research checkpoint: `docs/checkpoints/2026-09-12_V2_2_FAMILY_SEMANTICS_PROFILE_BASELINES_W1.md`

## Production

Production remains unchanged by strategy research.

Accepted application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Runtime contract:

- health `ok`;
- mode `read_only`;
- provider `binance_usdm`;
- `data_ready=true`;
- Action authentication enabled;
- `scanner_status=DEGRADED` is the known fail-closed/history-readiness condition and does not by itself mean runtime failure.

No production code/config/deployment/risk/execution/trading semantics were changed by this research batch.

## Research isolation

Branch:

`research-strategy-benchmark-v1`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

The research branch does not imply production activation.

## Frozen INTRADAY candidate v2.2

Strategy:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Path:

`H1 context -> M15 pullback/reclaim -> structural SL -> frozen H1 structural-space gate -> nominal 3R`

Frozen gates include:

- H1 EMA20/50 separation / ATR14 >=0.20;
- M15 signal body/range <=0.60;
- executed structural risk distance >=1.25%;
- frozen H1 pivot-cluster structural-space >=3R or open-space;
- max hold `32 x M15 = 8h`.

Historical pre-holdout result:

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 23 | 47.83% | +0.1003R | 1.1818 |
| Validation | 10 | 30.00% | +0.2507R | 1.3941 |
| Non-holdout | 37 | 45.95% | +0.2888R | 1.5592 |
| Stress | 37 | 43.24% | +0.2741R | 1.5235 |

Promotion gate remains **FAIL** because sample and WR gates are not met. Positive expectancy/PF does not override preregistered gates.

## Prospective evidence

Frozen boundary:

`2026-09-11T20:00:00Z`

The shadow runner is provider-recorded, immutable and fail-closed. One old infrastructure-invalid `20:45Z` attempt remains explicitly excluded from evidence.

Latest valid snapshot:

`2026-09-12T02:00:00Z`

Current ledger:

- valid snapshots: 6;
- panel: 19/19;
- latest snapshot: 437 causally evaluable symbol-bars;
- deduplicated frozen events: 17;
- eligible observations: 4;
- unique eligible families: 3;
- resolved primary families: 0.

Evidence state:

`OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`

Latest artifact hashes:

- outcome summary: `cc78668947393c84cc0533d103f45935236b725f0c8203d01676a21bf8957581`;
- 02:00Z cycle: `b36de45b4e28daf4e53e9ed43e6ef33f497d3e3625f4c3047cbc63cc0e23b040`;
- 02:00Z shadow summary: `ab0a5bbaf1016c625e851c46e536bb8ec7ca73547f0617dbf7af22df8c677206`;
- prospective ledger: `b81652f3be5a2438a219017095a5da9c0313b4eff4a3ac70d24ae859e5593c59`.

## Family accounting

Preregistered before any terminal family outcome:

`docs/research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`

Primary evidence unit = unique `setup_family_id`.

Earliest eligible observation is the immutable family representative. Later observations from the same family are correlated diagnostics only and do not increase evidence count.

Automatic resolver:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_v1.py`

It preserves frozen STOP-first same-bar handling, 3R target, base execution costs/funding and 32 completed M15 bars before TIME_EXIT at the next open.

Synthetic resolver self-test: `PASS`.

Current primary family state:

| Family | Obs | MFE | MAE | Resolved |
|---|---:|---:|---:|---|
| `15fc0a...` | 2 | 2.530R | 0.027R | no |
| `6aabd4...` | 1 | 0.400R | 0.798R | no |
| `293d11...` | 1 | 0.655R | 0.297R | no |

No unresolved family is counted as win/loss.

## Fresh Level Context observation

Prospective report SHA256:

`22d547f847bd212572052c372aa55562e995b362f9536f8d6594d015e2ae648a`

Among 3 primary families:

- all 3 currently have `clean_break_no_revisit=true`;
- frozen v2.2 detector sees open-space for all 3;
- richer Level Context v2 disagrees for 2/3;
- those richer obstacles are approximately `0.028R` and `0.214R` ahead.

This is fresh observation but not a gate because outcomes remain unresolved and sample size is tiny.

## Deep multi-profile dataset

Research-only dataset cutoff:

`2026-09-11T20:45:00Z`

Panel: 19/19 Binance USDM symbols.

Depth per symbol:

- M5: 3000;
- M15: 3000;
- H1: 2000;
- H4: 1000;
- D1: 335–500, listing-age aware.

Funding captured from official Binance Futures `/fapi/v1/fundingRate` for 19/19 symbols.

Funding completeness:

`PASS_WITH_LISTING_BOUNDARY_HEAD_GAPS`

Internal gap <=8.01h; only expected listing-boundary head gaps on AKEUSDT, METUSDT and USELESSUSDT.

Dataset SHA256:

`4f49f57dcd3d36939bfa56167b13a9af2ea08884fb11be66dd0f957389b3f077`

Funding summary SHA256:

`c987475c7417bb8c34722e0da67ebe71909eb57a99af3be0191d02209122911f`

## FAST baseline v0

Preregistered:

`docs/research/PROFILE_BASELINES_FAST_SWING_V0_PREREG.md`

Path:

`H1 direction -> M15 pullback -> M5 trigger -> structural M5 SL -> 3R -> max 4h`

No tuned v2.2 threshold was imported.

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 486 | 32.30% | -0.163R | 0.773 |
| Validation | 152 | 30.92% | -0.189R | 0.734 |
| Non-holdout | 641 | 31.98% | -0.167R | 0.766 |
| Stress | 637 | 31.08% | -0.222R | 0.699 |

Conclusion: FAST v0 is a negative baseline. Do not tune it in place using seen validation.

## SWING baseline v0

Path:

`D1 direction -> H4 alignment/pullback -> H1 trigger -> structural H1 SL -> 3R -> max 4d`

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 238 | 31.51% | -0.0035R | 0.995 |
| Validation | 76 | 28.95% | -0.0273R | 0.963 |
| Non-holdout | 318 | 30.82% | -0.0100R | 0.986 |
| Stress | 318 | 29.56% | -0.0516R | 0.929 |

Conclusion: SWING v0 is near breakeven under base assumptions but negative in validation/stress. It is not promotable.

Post-hoc LONG-vs-SHORT differences are diagnostics only and must not become a rule without a new version and fresh evidence.

Baseline report SHA256:

`11e4dd9c0fa9c6ed82df63e798a03121920bc8693568686c897ce23f215e9c09`

Diagnostics SHA256:

`7e0c20399ee6183a374e726b98af46a51ff1438f0eff750971d75dac4d1d7495`

## POSITION W1 research contract

Preregistered:

`docs/research/POSITION_W1_DATA_CONTRACT_V0.md`

W1 is derived only from exactly seven fully closed provider-recorded D1 bars in an ISO UTC week.

Audit:

- 19/19 symbols;
- 47–70 W1 bars;
- temporal integrity `PASS`;
- invalid weekly sequences: 0;
- 17/19 symbols have >=53 W1 bars;
- AKEUSDT=49 and METUSDT=47 remain too young for meaningful EMA50+3-week-slope context.

W1 summary SHA256:

`c4108fc548741bac7f28a3709c3133f1830c2349601e935d3b245a6d0a473449`

POSITION remains prototype/data-architecture only.

## Historical diagnostics retained

Previous findings remain valid as diagnostics only:

- v2.2 STOP trades mostly fail early;
- TARGET trades usually show strength quickly;
- `clean break -> no revisit` remains the strongest structural hypothesis;
- historical v2.2 economics are materially supported by IOSTUSDT;
- execution costs are material;
- raw canonical VSA does not support mandatory directional matching;
- canonical static level clustering is much less discriminating than Level Context v2.

See:

- `docs/research/PARALLEL_RESEARCH_RESULTS_2026-09-11.md`;
- `docs/research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`.

## Evidence governance

Primary evidence unit = unique resolved setup family.

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Every strategy change requires a new version, preregistration, causal full-path testing and fresh evidence. Holdout must not be used for repeated tuning.

## Safe continuation

Continue:

- exact frozen-v2.2 shadow captures;
- automatic family outcome resolution;
- observation-only Level Context/VSA/execution logging;
- provenance/ledger checks;
- separate new-version research when preregistered.

Do not change frozen v2.2 from currently seen data:

- no Level Context/clean-break hard gate;
- no early-progress or profit-protection rule;
- no new min-risk threshold;
- no volume/VSA hard gate;
- no symbol/direction inclusion rule;
- no RR/8h retuning;
- no holdout opening.

## Next hard milestone

`>=30 unique resolved prospective frozen-v2.2 setup families`

Until then prospective evidence remains observation-only.
