# BOOTSTRAP PACKAGE — K-Trader Post-Pause Resume — 2026-09-13

Use this file to restore the exact project state in a new chat after the 24h technical pause.

## 1. Canonical identities

Repository: `kolemasakar/K-Trader`

Canonical `main`:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Research branch:

`research-strategy-benchmark-v1`

Research branch accepted pre-resume head before this bootstrap/checkpoint sequence:

`90debd3ed5c4284b4590b8e4ebe7f106d475a8d3`

Production deployed SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Production and `main` are intentionally not identical: the current `main` delta is GPT Builder governance/documentation and does not require production deployment.

## 2. Production after pause

At approximately `2026-09-13T06:12:54Z`:

- `/health` = `ok`;
- mode = `read_only`;
- `data_ready=true`;
- provider = `binance_usdm`;
- scanner = `DEGRADED` (known fail-closed/history-readiness condition);
- action authentication enabled;
- deployed SHA unchanged at `81b79...`;
- VM uptime ~`3 days 22:44`, therefore no host reboot occurred during the pause.

The connected SentinelX identity cannot query the Docker socket directly. Do not infer container state from `docker ps`; use health plus an authorized Docker/root channel when direct container inspection is needed.

## 3. Pause integrity

Pause window:

`2026-09-12T06:00:00Z -> 2026-09-13T06:00:00Z`

The pause was **not a strict no-host-change freeze**.

At `2026-09-12T06:04:35Z` unattended-upgrade changed host packages:

- Python 3.12: `3.12.3-1ubuntu0.16 -> 3.12.3-1ubuntu0.17`;
- libc6 family: `2.39-0ubuntu8.8 -> 2.39-0ubuntu8.9`.

No K-Trader repo/deployment SHA changed. Current production health is PASS.

APT timers are active again after the pause. No `2026-09-13` APT transaction was present at the resume audit.

The pause-watch automation did not leave a complete 24h hourly evidence chain. Do not claim complete hourly continuity without reconstructing it from data/runtime artifacts.

## 4. Frozen candidate — immutable

Strategy:

`candidate_rule_set_v2_2`

Harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Prospective boundary:

`2026-09-11T20:00:00Z`

Frozen path:

`H1 context -> M15 pullback/reclaim -> structural SL -> frozen H1 structural-space gate -> nominal 3R`

Frozen key gates:

- H1 EMA20/50 separation / ATR14 >= `0.20`;
- M15 signal body/range <= `0.60`;
- executed structural risk distance >= `1.25%`;
- frozen H1 structural-space = open or >= `3R`;
- max hold = `32 x M15 = 8h`;
- same-bar STOP-first semantics.

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

Do not change frozen v2.2, RR, max hold, risk gate, direction/symbol selection or holdout authorization from the current small prospective sample.

## 5. Latest accepted prospective state before post-pause catch-up

Latest valid immutable snapshot:

`2026-09-12T04:45:00Z`

Ledger:

- valid snapshots: 7;
- panel: 19/19;
- evaluated symbol-bars: 646;
- deduplicated frozen events: 31;
- eligible observations: 6;
- unique eligible families: 4;
- resolved primary families: 2;
- unresolved primary families: 2;
- resolved wins/losses: `0 / 2`;
- resolved expectancy: `-1.0285267114R`;
- evidence status: `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`.

Accepted hashes:

- shadow summary: `4af1233c90464ab1d0e8cdf4b6e1ede062f66731558e6eb1eb947dc9377ca9df`;
- bundle set: `6e41b993477b47b179bc40e9f46a700d0aca9529797111562103920c124f355e`;
- bundle export: `8ce3bb969943ebe8814bd1c67952d8ef1215e56399134dd1430891097711e50d`;
- event file: `83b3f64813a803382048a9193a092e7423a3fef986213905603acdaa8b091073`;
- ledger event set: `cd25594d5e3f46a8894acf0bca050bf7b253c1618fe2f45184ed8a431287d166`;
- outcome summary: `f7e8314337166cdc4657f37b175c9744833a8356d2f0e3bc64702a5d0f4b19cb`;
- Level Context observation: `de61c71e7aef0c01b07eef03c01572f4dd618cd0def99f7bda2b0b1edc113b02`.

Primary families at that boundary:

| Family | Symbol | Side | State | Realized R |
|---|---|---|---|---:|
| `15fc0a...` | RAYSOLUSDT | LONG | unresolved | — |
| `6aabd4...` | RAYSOLUSDT | LONG | STOP | `-1.0221R` |
| `293d11...` | RAYSOLUSDT | LONG | STOP | `-1.0350R` |
| `eecbdb...` | ENAUSDT | SHORT | unresolved | — |

The two resolved STOP families are the two current prospective Level Context v2 disagreements: frozen detector reports open-space, while richer Level Context sees obstacles ~`0.028R` and ~`0.214R`. This is an observation, not a rule.

## 6. Family evidence governance

Primary evidence unit = unique resolved `setup_family_id`.

Preregistered family semantics:

- earliest eligible observation = immutable primary family representative;
- later observations in the same family = correlated diagnostics only;
- unresolved families are not wins or losses.

Evidence bands:

- `<30` resolved families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

## 7. Catch-up after the pause — first mandatory operation

The shadow runner stores 400 M15 bars per symbol, approximately 100 hours. The 24h pause is therefore still fully inside the causal recovery horizon.

First operation in the new chat:

1. Resolve the latest safe fully closed M15 cutoff at run time.
2. Through an **authorized Docker/root channel**, run one canonical provider-recorded frozen-v2.2 shadow cycle covering the pause.
3. Confirm panel = 19/19 and no missing bundles.
4. Rebuild the immutable prospective ledger.
5. Run `prospective_v2_2_outcome_resolver_v1.py`.
6. Refresh `prospective_level_context_observation.py` and observation-only VSA/execution diagnostics.
7. Audit pause-window M15 continuity and any gaps/stale intervals.
8. Record hashes and a new post-catch-up checkpoint.

Do not use a noncanonical substitute if the authorized data path is unavailable. Fail closed and report the exact permission boundary.

## 8. Host-drift acceptance before development mutation

Because unattended-upgrade changed host Python/libc during the pause, before code/config/deploy mutation:

- re-confirm deployed SHA;
- re-confirm local and public health;
- inspect Docker/container status using an authorized channel;
- check whether any service restart/reboot is pending;
- run the smallest canonical runtime acceptance required by existing project docs;
- document the host package drift as an environmental event, not a strategy event.

Do not redeploy merely to make deployment SHA equal to `main`; current `main` contains governance docs only.

## 9. Repository/governance after pause

PR #57 was squash-merged after CI success.

Canonical `main` is now:

`4919fea4397d34898ddc7d4215ea898e6caea815`

It canonizes:

- approved `SYSTEM_K_TRADER_v1_3_COMPACT.md`;
- active `00_KNOWLEDGE_PRIORITY.md`;
- Builder checklist / Action guide / catalogue references.

The research branch contains the same research work but is topologically one canonical commit behind main. It was approximately `83 ahead / 1 behind` at the post-pause audit.

Do not rewrite research history. Synchronize ancestry only after the post-pause checkpoint and after verifying no governance-file content conflict.

## 10. Retained completed research

### v2.2 historical pre-holdout

- Development: n23, WR47.83%, expectancy +0.1003R, PF 1.1818.
- Validation: n10, WR30.00%, expectancy +0.2507R, PF 1.3941.
- Non-holdout: n37, WR45.95%, expectancy +0.2888R, PF 1.5592.
- Stress: n37, WR43.24%, expectancy +0.2741R, PF 1.5235.
- Promotion remains FAIL; holdout untouched.

### Level Context / MFE-MAE

Retain as diagnostics:

- losers mostly fail early;
- successful 3R trades generally show strength quickly;
- `clean break -> no revisit` remains a promising hypothesis, not a gate;
- richer Level Context is materially more discriminating than simple static clustering;
- current prospective obstacle disagreement is interesting but sample is tiny.

### Profile baselines

FAST v0:

- non-holdout expectancy about `-0.167R`, PF `0.766`;
- negative baseline; do not tune in place.

SWING v0:

- non-holdout expectancy about `-0.010R`, PF `0.986`;
- validation/stress negative; not promotable.

POSITION:

- W1 data contract built from complete D1 weeks;
- 19/19 symbols, 47–70 W1 bars;
- prototype-only.

## 11. Data assets

Deep research dataset, 19 Binance USDM symbols:

- M5 = 3000;
- M15 = 3000;
- H1 = 2000;
- H4 = 1000;
- D1 = 335–500 listing-age aware;
- funding = 19/19 from Binance `/fapi/v1/fundingRate`;
- funding completeness = PASS with expected listing-boundary head gaps only.

Keep this dataset separate from prospective frozen-v2.2 evidence.

## 12. Recommended post-catch-up work order

After P0 catch-up and host acceptance pass:

1. Continue exact frozen-v2.2 prospective accumulation and resolver.
2. Analyze fresh Level Context obstacle quality on resolved families without promoting a gate.
3. Resume portfolio/correlation and execution-economics diagnostics on newly resolved evidence.
4. Design a **new preregistered version** only when evidence justifies it; never retune frozen v2.2 in place.
5. Continue separate SWING/POSITION architecture research only after the prospective pipeline is current.

## 13. Files to read first in the new chat

- `docs/checkpoints/2026-09-13_POST_PAUSE_RESUME.md`
- `docs/CURRENT_STATE.md`
- `docs/research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`
- `docs/research/V2_2_PROSPECTIVE_SHADOW_PROTOCOL.md`
- `docs/research/CANDIDATE_RULE_SET_V2_2.md`
- `docs/research/LEVEL_CONTEXT_V2_2_MFE_MAE_STAGE3_RESULTS.md`
- `docs/research/PARALLEL_RESEARCH_RESULTS_2026-09-11.md`
- `docs/research/PROFILE_BASELINES_AND_PROSPECTIVE_UPDATE_2026-09-12.md`
- `custom_gpt/SYSTEM_K_TRADER_v1_3_COMPACT.md`
- `custom_gpt/00_KNOWLEDGE_PRIORITY.md`

## 14. New-chat recovery instruction

In the new chat use:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-13_K_TRADER_POST_PAUSE_RESUME.md">>`

Then execute **P0 post-pause catch-up/acceptance first**, before any strategy mutation.

## 15. Phase state

Phase 11G: **ACTIVE**.

Phase 12: **FUTURE / NOT ACTIVE**.
