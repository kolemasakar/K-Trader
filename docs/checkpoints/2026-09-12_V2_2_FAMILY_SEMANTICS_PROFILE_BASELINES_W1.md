# CHECKPOINT — v2.2 Family Semantics + Profile Baselines + W1 — 2026-09-12

Status: **COMPLETE FOR CURRENT DATA / PROSPECTIVE ACCUMULATION CONTINUES**

Parent research state before this checkpoint document:

`44b1d52fcf4e4ae6ecf27179f2db6ae02370825b`

Branch:

`research-strategy-benchmark-v1`

## Immutable boundaries

Production application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Production remains healthy/read-only and was not changed by this batch.

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

## Family semantics

Preregistered before any family had a terminal outcome:

`docs/research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`

Primary evidence unit = unique `setup_family_id`.

Earliest eligible entry is the immutable family representative; later eligible observations are correlated diagnostics only.

Family outcome is the primary representative outcome only.

Resolver:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_v1.py`

Synthetic semantics test:

- simultaneous STOP+TARGET bar -> STOP;
- 32 completed M15 bars -> TIME_EXIT at next M15 open;
- result: `PASS`.

## Prospective status at 02:00Z

Valid snapshot count: 6.

Latest valid snapshot:

`2026-09-12T02:00:00Z`

- panel 19/19;
- 437 causally evaluable symbol-bars;
- 17 deduplicated events;
- 4 eligible observations;
- 3 unique eligible families;
- 0 resolved primary families.

Evidence state:

`OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`

Latest outcome summary SHA256:

`cc78668947393c84cc0533d103f45935236b725f0c8203d01676a21bf8957581`

Latest cycle summary SHA256:

`b36de45b4e28daf4e53e9ed43e6ef33f497d3e3625f4c3047cbc63cc0e23b040`

Latest shadow summary SHA256:

`ab0a5bbaf1016c625e851c46e536bb8ec7ca73547f0617dbf7af22df8c677206`

Latest ledger SHA256:

`b81652f3be5a2438a219017095a5da9c0313b4eff4a3ac70d24ae859e5593c59`

## Fresh Level Context observation

Report SHA256:

`22d547f847bd212572052c372aa55562e995b362f9536f8d6594d015e2ae648a`

Among 3 primary prospective families:

- all 3 have `clean_break_no_revisit=true`;
- frozen v2.2 level detector sees open-space on all 3;
- Level Context v2 disagrees on 2/3;
- richer-detector obstacles for those two are ~`0.028R` and ~`0.214R`.

No outcome is resolved, so this is observation only and does not modify eligibility.

## FAST baseline v0

Preregistered:

`docs/research/PROFILE_BASELINES_FAST_SWING_V0_PREREG.md`

Results:

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 486 | 32.30% | -0.163R | 0.773 |
| Validation | 152 | 30.92% | -0.189R | 0.734 |
| Non-holdout | 641 | 31.98% | -0.167R | 0.766 |
| Stress | 637 | 31.08% | -0.222R | 0.699 |

Conclusion: negative baseline; do not tune v0 in place.

## SWING baseline v0

Results:

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 238 | 31.51% | -0.0035R | 0.995 |
| Validation | 76 | 28.95% | -0.0273R | 0.963 |
| Non-holdout | 318 | 30.82% | -0.0100R | 0.986 |
| Stress | 318 | 29.56% | -0.0516R | 0.929 |

Conclusion: near breakeven base economics but negative validation/stress; not promotable.

Baseline report SHA256:

`11e4dd9c0fa9c6ed82df63e798a03121920bc8693568686c897ce23f215e9c09`

Diagnostics SHA256:

`7e0c20399ee6183a374e726b98af46a51ff1438f0eff750971d75dac4d1d7495`

## POSITION W1 contract

Preregistered:

`docs/research/POSITION_W1_DATA_CONTRACT_V0.md`

Derived from exactly seven complete closed D1 candles per UTC ISO week.

Audit:

- 19/19 symbols;
- 47–70 W1 bars;
- temporal-integrity status `PASS`;
- 0 invalid weekly sequences;
- 17/19 have >=53 W1 bars;
- AKEUSDT 49 and METUSDT 47 remain too young for meaningful EMA50+3-week-slope prototype context.

W1 summary SHA256:

`c4108fc548741bac7f28a3709c3133f1830c2349601e935d3b245a6d0a473449`

POSITION remains prototype-only.

## Governance

Nothing in this checkpoint changes production, Risk Manager, execution, frozen v2.2 gates, RR=3, 8h max hold or holdout authorization.

Do not promote from current post-hoc subgroup observations:

- SWING LONG-only behavior;
- FAST side asymmetry;
- Level Context v2 obstacle disagreement;
- clean-break/no-revisit;
- time-exit behavior.

Any such change requires a new preregistered version and fresh evidence.

## Next hard milestone

`>=30 unique resolved prospective frozen-v2.2 setup families`

Until then frozen-v2.2 prospective evidence remains observation-only.
