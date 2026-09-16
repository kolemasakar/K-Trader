# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T12:00:00Z`, hypothesis preregistration, path-quality analysis and fail-closed pipeline hardening.

Current checkpoint: `docs/checkpoints/2026-09-16_PREREG_PATH_PIPELINE_HARDENING.md`  
Previous diagnostic checkpoint: `docs/checkpoints/2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md`  
Resolver specification: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`  
Hypothesis preregistration: `docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`  
Historical methodology checkpoint: `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime state:

- host `k-trader-prod-vnic`;
- container `k-trader-ktrader-1` healthy;
- `/health status=ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state, not an outage;
- root filesystem `/dev/sda1` approximately `19%` used;
- no production deploy or container restart was performed by current research work.

Container mapping:

`host /opt/k-trader/data -> container /data`

Extended production soak remains accepted:

`EXTENDED_PRODUCTION_SOAK = PASS`

APT timers are restored and enabled/active.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

Canonical main baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Frozen candidate:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

Prospective boundary:

`2026-09-11T20:00:00Z`

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

No frozen rule, RR, 32-M15 max hold, risk gate, symbol/direction filter or holdout authorization changed.

## Track A — accepted prospective state

Latest accepted capture cutoff:

`2026-09-16T12:00:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T120000Z`

Capture:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- current-capture eligible setups `44`;
- current-capture events `295`;
- current-capture unique eligible families `34`;
- holdout opened `false`;
- production action `false`.

Capture hashes:

- bundle set `48dc64d60545224533b84fceb5bc1e85cb2f51b37a2edafb25b88c7615c73e6c`;
- bundle export summary `104589aaff6eb088901a40b4461523c9a74d390160fa9773a5f44aabb7521719`;
- event file `ae811bd344ce1e3cf1c8ac4d67f0536c1d38c44146df1fceff87757c35f9cdee`;
- shadow summary `55906a0fdb7c25f376213eb22ec4629cc06f70ad6b918f334b19536683198a8a`.

Prospective ledger:

- discovered snapshots `18`;
- valid snapshots `17`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- deduplicated events `365`;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `14afc359ed316fd21ee2d309100aeda856d61d9e5b7a3f6e15d199be6b90190c`.

Official Binance USD-M funding snapshot:

- symbols `19`;
- records `1849`;
- summary SHA256 `22a5785767abf3717eadda2c69c78524e5e8195ac975544c6557dafed7ed8b7c`.

### Resolver-v1.2 outcome at 12:00Z

Output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_2/20260916T120000Z`

State:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- win rate `23.0769230769%`;
- expectancy `-0.6482720085510278R`;
- evidence `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- network used `false`;
- holdout opened `false`;
- production action `false`.

Summary SHA256:

`6e7f07d0d54d421967bb689d71798f943e26e065f29de5e58838a789ca9a5a58`

Open primary families at this accepted cutoff:

- SUIUSDT entry `08:00Z`: `16/32` M15 bars;
- XRPUSDT entry `08:00Z`: `16/32` M15 bars;
- ADAUSDT entry `08:15Z`: `15/32` M15 bars;
- DOGEUSDT entry `08:15Z`: `15/32` M15 bars.

If STOP/3R does not occur first, max-hold boundaries remain `16:00Z` and `16:15Z` on 2026-09-16.

## Resolver v1.2 / provenance hardening

Resolver v1.2 changes only the absolute prior-price identity guard from `2e-9` to `3e-9` while preserving v1.1 outcome semantics.

Hardening: **PASS**.

- observed stop drift passes;
- `2.5e-9` inside-tolerance test passes;
- `3.5e-9` outside-tolerance test fails closed;
- missing funding snapshot fails closed;
- `50/50` prior resolved observations retained;
- terminal/economic mismatches `0`;
- aged-out immutable accepted outcomes preserved `6`.

Hardening report SHA256:

`6b780390daabad1b74824bcc2a01fdbc40457b639aa253dc425c4334155fa369`

12:00Z provenance audit: **PASS**.

- family set `43/43` matches outcomes;
- primary identity mismatches `0`;
- symbol/side inconsistencies `0`;
- exact identity duplicates after dedup `0`;
- multi-observation families `13`, expected under family semantics;
- observations/families hashes match accepted summary.

Provenance report SHA256:

`5c4341421d1e702f3256e50639c9e909c1880053346bc26a1d98142e6d8d4e0e`

## Post-30 / portfolio diagnostics

Current evidence remains diagnostic only.

- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.679800R`;
- no supported general LONG-only / SHORT-exclusion rule;
- obstacle `<1R/<3R` remains hypothesis-generating;
- raw VSA does not provide reliable separation;
- max concurrent exposure `6`;
- largest correlated cohort `4`.

A post-hoc discovery signal was observed for `SHORT × low H1 EMA20/50 separation / ATR14`:

- discovery cutpoint `<0.9033277894201235`;
- LOW SHORT: `n=10`, expectancy `-0.137355R`;
- other SHORT: `n=16`, expectancy `-1.018829R`;
- difference `+0.881473R`;
- exploratory permutation `p≈0.00061`;
- BH-adjusted `q≈0.00366` across six exploratory contrasts;
- leave-one-symbol-out sign positive `8/8`.

The LOW group is temporally concentrated, especially on 2026-09-15, so regime/time confounding remains plausible.

This is not a frozen-v2.2 rule.

## Preregistered future hypotheses

Canonical preregistration:

`docs/research/PROSPECTIVE_HYPOTHESES_PREREG_2026-09-16.md`

Future confirmation boundary:

`entry_time >= 2026-09-16T13:00:00Z`

Anything before this boundary is discovery/context only and cannot count as confirmatory evidence, including the four families already open before the boundary.

Primary H1 freezes:

`SHORT && h1_ema_sep_atr < 0.9033277894201235`

The cutpoint cannot be re-estimated from confirmation data. H1 requires at least `20` resolved future primary SHORT families in LOW and `20` in REST, fixed effect-size/statistical/concentration checks, and remains eligible only for a future versioned proposal even if supported.

Secondary preregistered hypotheses cover obstacle inside 1R, obstacle inside 3R and same-side 60-minute portfolio concentration.

## Path quality / MFE / MAE

Runtime report:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_path_quality/20260916T120000Z/report.json`

SHA256:

`4cf1085bbcd35bb381f1f2981136f6f66f97c734b5efa10fedf9a8a9d7e41030`

Reproducible implementation:

`research/strategy_benchmark_v1/prospective_path_quality_diagnostics.py`

Overall 39 resolved primary families:

- mean MFE `0.8013R`;
- mean MAE `1.0491R`;
- median realized result `-1.0247R`;
- median hold `20` M15 bars.

STOP outcomes (`26`):

- expectancy `-1.0669R`;
- mean MFE `0.7015R`;
- mean MAE `1.3103R`;
- `17/26` reached at least `+0.5R`;
- `7/26` reached at least `+1R` but still finished non-positive;
- none reached `+2R` before STOP.

TIME_EXIT outcomes (`13`):

- expectancy `+0.1890R`;
- wins `9/13`;
- mean MFE `1.0010R`;
- mean MAE `0.5265R`;
- median hold `33` under current resolver counting semantics.

TIME_EXIT by achieved MFE:

- `<0.5R`: n=3, expectancy `-0.5869R`;
- `0.5–1R`: n=5, expectancy `+0.1439R`;
- `1–2R`: n=3, expectancy `+0.4769R`;
- `2–3R`: n=2, expectancy `+1.0336R`.

These are future exit-management hypotheses only; they do not authorize break-even, trailing, partial exits or max-hold changes.

## Execution-cost / symbol / temporal diagnostics

- post-cost expectancy `-0.6483R`;
- estimated mean pre-cost expectancy `-0.5811R`;
- mean execution drag about `0.0671R`;
- only one resolved family crossed from pre-cost positive to post-cost non-positive.

Therefore trading costs are material but not the primary source of current weakness.

Leave-one-symbol-out expectancy remains negative after every single-symbol exclusion, approximately `-0.576R` to `-0.740R`; the result is not driven by one symbol alone.

By entry day:

- 2026-09-12: `-1.005R`;
- 2026-09-13: `-1.133R`;
- 2026-09-14: `-0.798R`;
- 2026-09-15: `-0.146R`.

This keeps regime/time variation as a central research explanation.

## Historical context

Accepted corrected causal rolling-context results remain:

| Window | Trades | Expectancy R | Stress expectancy R |
|---|---:|---:|---:|
| P25 | 214 | +0.259415 | +0.224861 |
| R90 | 531 | +0.031637 | -0.009676 |
| R180 | 1073 | -0.013131 | -0.042896 |
| R365 | 2099 | -0.051000 | -0.074531 |

Current prospective expectancy and win rate are below all four historical windows, reinforcing a current-regime weakness interpretation.

Historical data show the same directional sign for the discovery-stage SHORT-low-trend hypothesis across all four windows, but this is context only, not fresh OOS confirmation.

## Fail-closed prospective research orchestration

Canonical runner:

`research/strategy_benchmark_v1/run_prospective_research_pipeline_v1.py`

Properties:

- plan-only by default;
- explicit `--execute` required;
- stages: capture -> funding -> resolver v1.2 -> post-30 diagnostics -> statistical diagnostics;
- hashed manifest records planned/executed stage state;
- any non-zero stage stops all later stages;
- execute mode rejects an existing run root;
- missing scripts/prior outcomes fail closed;
- no holdout or production action.

Plan-mode validation for the future 13:00Z boundary produced a five-stage PLAN_ONLY manifest without executing stages.

Plan manifest SHA256:

`f684f38bf8793c1cbc0cfc0f0a01fc58ca07466b31a94ec83d05db62faafba73`

Synthetic failure-path validation intentionally failed funding with rc=7 and confirmed that resolver and later stages were not executed:

`LATER_STAGES_BLOCKED=PASS`

Failure manifest SHA256:

`e2c1ecb3f2fb92fcbf9e1f67317d4d16282b474f3eaff633f3196bf203eba51b`

Regression tests:

`research/strategy_benchmark_v1/tests/test_prospective_research_pipeline_v1.py`

Result: **4/4 PASS**.

## Disk retention

Dry-run helper/config/service are installed and sandbox-tested. Planner remains `DRY_RUN_ONLY`; destructive mode is absent.

Accepted host dry-run:

- disk use `19.000516%`;
- trigger false;
- eligible candidates `38`;
- would-delete candidates `20`;
- would-delete bytes `97,393,279`;
- deletion performed false;
- manifest SHA256 `d1ecdb98b8d4fc000098482126c3f9542a67562e44b5eddb73411187e3037d20`.

`ktrader-disk-retention.timer` remains **disabled by design**.

## Governance

Prospective thresholds remain:

- `<30`: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current accepted state remains **39 resolved primary families**. Historical trades never count toward these thresholds.

No current evidence authorizes in-place retuning, direction filtering, exit-management modification, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue causal prospective collection/resolution under the `30–49` tier;
2. resolve the four pre-prereg open primary families after STOP/3R or actual max-hold boundaries, but do not count them toward confirmation H1–H4;
3. collect future confirmation observations only from `entry_time >= 2026-09-16T13:00:00Z`;
4. use the fail-closed runner for future controlled cycles after explicit execution decisions;
5. preserve resolver/provenance invariants, frozen v2.2 and closed holdout;
6. keep disk-retention timer disabled unless disk pressure or a separately approved monitoring policy justifies it.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
