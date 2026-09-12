# K-Trader Research Update — 2026-09-12

Status: **RESEARCH ONLY / PRODUCTION UNCHANGED / HOLDOUT UNTOUCHED**

## 1. Prospective family accounting

Preregistered:

`docs/research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`

Rule: earliest eligible observation of each `setup_family_id` is the immutable primary representative. Later observations in that family are correlated diagnostics and never increase independent evidence count.

Automatic resolver:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_v1.py`

Synthetic semantics self-test:

`PASS` for STOP-first same-bar ambiguity and TIME_EXIT at the next open after 32 completed M15 bars.

At `2026-09-12T02:00:00Z`:

- eligible observations: 4;
- unique families: 3;
- resolved primary families: 0;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

Primary-family state:

| Family | Observations | MFE | MAE | Resolved |
|---|---:|---:|---:|---|
| `15fc0a...` | 2 | 2.530R | 0.027R | no |
| `6aabd4...` | 1 | 0.400R | 0.798R | no |
| `293d11...` | 1 | 0.655R | 0.297R | no |

No unresolved family is counted as win/loss.

Outcome summary SHA256:

`cc78668947393c84cc0533d103f45935236b725f0c8203d01676a21bf8957581`

## 2. Frozen v2.2 shadow status

Additional valid snapshot:

`2026-09-12T02:00:00Z`

- panel: 19/19;
- causally evaluable symbol-bars in snapshot: 437;
- deduplicated frozen events: 17;
- eligible observations: 4;
- unique eligible families: 3;
- no new family versus 01:45Z;
- holdout untouched;
- exact frozen harness preserved.

Cycle summary SHA256:

`b36de45b4e28daf4e53e9ed43e6ef33f497d3e3625f4c3047cbc63cc0e23b040`

Shadow summary SHA256:

`ab0a5bbaf1016c625e851c46e536bb8ec7ca73547f0617dbf7af22df8c677206`

Current ledger SHA256:

`b81652f3be5a2438a219017095a5da9c0313b4eff4a3ac70d24ae859e5593c59`

## 3. Prospective Level Context v2 observation

Report SHA256:

`22d547f847bd212572052c372aa55562e995b362f9536f8d6594d015e2ae648a`

All 3 primary families currently have `clean_break_no_revisit=true`.

Important fresh observation:

- frozen v2.2 level detector reports open-space for all three families;
- richer Level Context v2 disagrees on 2/3 primary families;
- those two richer-detector obstacles are approximately `0.028R` and `0.214R` ahead of entry.

This is observation only. Outcomes are unresolved, therefore no Level Context v2 feature is promoted to a gate.

## 4. FAST baseline v0

Preregistered rules:

`docs/research/PROFILE_BASELINES_FAST_SWING_V0_PREREG.md`

Profile:

`H1 direction -> M15 pullback -> M5 trigger -> structural M5 SL -> 3R -> max 4h`

No v2.2 separation/body/min-risk/structural-space thresholds were imported.

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 486 | 32.30% | -0.163R | 0.773 |
| Validation | 152 | 30.92% | -0.189R | 0.734 |
| Non-holdout | 641 | 31.98% | -0.167R | 0.766 |
| Stress non-holdout | 637 | 31.08% | -0.222R | 0.699 |

Conclusion: simple FAST v0 has no positive economic baseline. Do not tune it in-place from this validation.

Diagnostics, non-holdout:

- STOP: 384;
- TARGET: 92;
- TIME_EXIT: 165;
- only 42.7% of STOP trades first reached +0.5R;
- 68.5% of TIME_EXIT trades were net-positive;
- LONG subgroup is less negative than SHORT, but this is post-hoc and not a rule.

## 5. SWING baseline v0

Profile:

`D1 direction -> H4 alignment/pullback -> H1 trigger -> structural H1 SL -> 3R -> max 4d`

| Segment | n | WR | expectancy_R | PF_R |
|---|---:|---:|---:|---:|
| Development | 238 | 31.51% | -0.0035R | 0.995 |
| Validation | 76 | 28.95% | -0.0273R | 0.963 |
| Non-holdout | 318 | 30.82% | -0.0100R | 0.986 |
| Stress non-holdout | 318 | 29.56% | -0.0516R | 0.929 |

Conclusion: SWING v0 is near breakeven at base assumptions, but validation and stress are negative. It is not a candidate for promotion.

Diagnostics, non-holdout:

- STOP: 209;
- TARGET: 65;
- TIME_EXIT: 44;
- 48.3% of STOP trades first reached +0.5R;
- 75% of TIME_EXIT trades were net-positive;
- LONG subgroup `n=77` is positive while SHORT is negative, but this is post-hoc and must not become a direction gate without a new preregistered version and fresh evidence;
- leave-one-symbol-out expectancy crosses around zero, confirming weak robustness of the near-breakeven aggregate.

Baseline report SHA256:

`11e4dd9c0fa9c6ed82df63e798a03121920bc8693568686c897ce23f215e9c09`

Diagnostics SHA256:

`7e0c20399ee6183a374e726b98af46a51ff1438f0eff750971d75dac4d1d7495`

## 6. POSITION W1 derived contract

Preregistered:

`docs/research/POSITION_W1_DATA_CONTRACT_V0.md`

Research-only W1 built from exactly seven closed Binance USDM D1 bars per UTC ISO week.

Temporal integrity audit:

`PASS`

- symbols: 19/19;
- W1 bars per symbol: 47–70;
- invalid week alignment/gaps: 0;
- current incomplete and listing-partial weeks excluded;
- 17/19 symbols have at least 53 W1 bars;
- `AKEUSDT=49`, `METUSDT=47`, insufficient for an EMA50 + 3-week slope context without effectively no warm history.

W1 summary SHA256:

`c4108fc548741bac7f28a3709c3133f1830c2349601e935d3b245a6d0a473449`

POSITION remains prototype/data-architecture only; no statistical baseline is promoted.

## 7. Governance conclusion

No result in this batch changes:

- production;
- frozen v2.2 rules;
- v2.2 RR=3;
- v2.2 8h max hold;
- holdout authorization;
- Risk Manager/execution/deployment.

Safe continuation during evidence accumulation:

- frozen prospective captures;
- deterministic outcome resolution;
- observation-only Level Context/VSA/execution features;
- documentation/provenance checks;
- separate new-version design only after explicit preregistration.

Do not tune FAST v0 or SWING v0 using the validation results above and continue to call the result the same v0 version.
