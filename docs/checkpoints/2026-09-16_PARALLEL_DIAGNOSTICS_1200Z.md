# Parallel Diagnostics Checkpoint — 2026-09-16 12:00Z

Status: **ACCEPTED DIAGNOSTIC CHECKPOINT**

Scope: diagnostic-only research under the `30–49` resolved-family governance tier. Frozen `candidate_rule_set_v2_2` remains unchanged. Holdout remained closed. No production action was taken.

## Authoritative prospective state

Cutoff: `2026-09-16T12:00:00Z`

- eligible observations: `56`;
- unique families: `43`;
- resolved primary families: `39`;
- unresolved primary families: `4`;
- wins / losses: `9 / 30`;
- win rate: `23.0769230769%`;
- expectancy: `-0.6482720085510278R`;
- evidence tier: `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`.

Frozen harness SHA256 remains:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256 remains:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

## A+B — post-30 and portfolio diagnostics

Canonical 12:00Z descriptive diagnostics:

- overall expectancy `-0.648272R`;
- LONG: `13` resolved, expectancy `-0.585215R`;
- SHORT: `26` resolved, expectancy `-0.679800R`;
- max concurrent exposure: `6`;
- largest correlated cohort: `4`;
- same-side 60m correlated cohorts: `36`;
- top-symbol share: `0.16279`;
- symbol HHI: `0.102217`.

Obstacle context remains the strongest earlier hypothesis-generating feature, but the original post-30 multiple-comparison analysis still does not authorize a filter.

Hashes:

- descriptive report: `81c90dbedf726366f26bdb0703f6dd9ea5ddc0b39237c0ebf2a882771ea0cc17`;
- statistical report: `38063ca5d80b9cb8da02d17f3b92cc02b3b151cfb658f1b9dcbba1c4476b8fc2`.

### Extended interaction diagnostics

Exploratory, data-derived terciles of `H1 EMA20/50 separation / ATR14` were evaluated. Tercile cutpoints in the 39-family resolved sample were:

- low/mid: `0.9033277894201235`;
- mid/high: `1.1318041660979272`.

A notable post-hoc contrast appeared for SHORT:

- SHORT / LOW trend tercile: `n=10`, expectancy `-0.137355R`;
- SHORT / MID+HIGH: `n=16`, expectancy `-1.018829R`;
- difference: `+0.881473R`;
- permutation `p≈0.00061`;
- BH-adjusted `q≈0.00366` across six exploratory contrasts.

This remains **hypothesis-only** because the threshold was derived from the same prospective sample and the sample is small.

Prospective leave-one-symbol-out robustness:

- positive LOW-vs-rest difference after excluding each symbol: `8/8`;
- low group is concentrated mainly on `2026-09-15`, so time/regime confounding remains possible.

Hashes:

- extended descriptive report: `22ef770b4f9be8dee4c5f9121df9a28afda6ea319d6a86ba6dcc4d2fa1eb80e2`;
- interaction statistical report: `4a9160e718b5f59e88aa6ae47ecc695ab021030bdd551b0c1460331b17eb64ed`;
- SHORT low-trend robustness report: `ee7028f64f87a2c995651f19fed6dbc6a46843a27507c87f31d119112f0210ba`.

## D+E — provenance audit and resolver-v1.2 hardening

Provenance audit result: **PASS**.

- eligible observations: `56`;
- families: `43`;
- primary outcomes: `43`;
- family-set match: true;
- primary identity mismatches: `0`;
- symbol/side family inconsistencies: `0`;
- exact identity duplicates after ledger dedup: `0`;
- multi-observation families: `13` (expected family semantics);
- observations hash: match;
- families hash: match;
- network used: false;
- holdout opened: false;
- production action: false.

Provenance report SHA256:

`5c4341421d1e702f3256e50639c9e909c1880053346bc26a1d98142e6d8d4e0e`

Resolver v1.2 hardening result: **PASS**.

- observed `2.1062864786e-9` price drift accepted;
- stable inside-tolerance test accepted;
- outside-tolerance `3.5e-9` test rejected;
- missing funding snapshot fails closed with `FUNDING_SUMMARY_MISSING`;
- `50/50` previously resolved observations found in current output;
- economic / terminal mismatches: `0`;
- aged-out immutable prior outcomes preserved: `6`.

Hardening report SHA256:

`6b780390daabad1b74824bcc2a01fdbc40457b639aa253dc425c4334155fa369`

## G — historical versus prospective context

Current prospective expectancy / win rate are below every accepted causal historical window:

| Window | Historical trades | Historical expectancy | Prospective expectancy | Historical WR | Prospective WR |
|---|---:|---:|---:|---:|---:|
| P25 | 214 | `+0.259415R` | `-0.648272R` | `44.86%` | `23.08%` |
| R90 | 531 | `+0.031637R` | `-0.648272R` | `39.36%` | `23.08%` |
| R180 | 1073 | `-0.013131R` | `-0.648272R` | `39.14%` | `23.08%` |
| R365 | 2099 | `-0.051000R` | `-0.648272R` | `37.54%` | `23.08%` |

Historical-vs-prospective report SHA256:

`dbb09c81ee29e5da43e825b9b9a7d9e72f213c6eb1b2b01f4318fb43d2e35315`

### Historical context for SHORT low-trend hypothesis

Using the prospective-derived cutpoint `H1 EMA-sep/ATR < 0.9033277894`, the LOW subgroup had better SHORT expectancy than the other SHORT trades in all four causal historical windows:

| Window | LOW n / expectancy | Rest n / expectancy | Difference | Permutation p |
|---|---:|---:|---:|---:|
| P25 | 21 / `-0.1045R` | 28 / `-0.6366R` | `+0.5321R` | `0.0343` |
| R90 | 56 / `-0.0053R` | 167 / `-0.2831R` | `+0.2778R` | `0.1149` |
| R180 | 135 / `-0.0007R` | 397 / `-0.1500R` | `+0.1493R` | `0.2094` |
| R365 | 300 / `+0.1610R` | 1006 / `-0.1451R` | `+0.3061R` | `0.00026` |

This is **historical hypothesis context only**, not fresh OOS validation. Historical data have already been used in strategy research and cannot promote this threshold into frozen v2.2.

Historical-context hypothesis report SHA256:

`7be8b49cf07ed0798646b6cc6b54277e28d3dcf379c257e251637dae4d0c23ac`

## Governance decision

No rule change is authorized.

Specifically, this checkpoint does **not** authorize:

- a SHORT exclusion;
- an EMA-separation filter;
- a `0.9033277894` production threshold;
- RR / max-hold / risk-gate changes;
- holdout access;
- production mutation;
- Phase 12 activation.

The SHORT-low-trend result is registered only as a candidate hypothesis for a future version. Any promotion would require preregistration and fresh independent prospective/OOS evidence under the existing governance thresholds.

Phase 11G remains **ACTIVE**. Phase 12 remains **FUTURE / NOT ACTIVE**.
