# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T12:00:00Z` and the parallel diagnostic package.

Current checkpoint: `docs/checkpoints/2026-09-16_PARALLEL_DIAGNOSTICS_1200Z.md`  
Resolver checkpoint: `docs/checkpoints/2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md`  
Resolver v1.2 specification: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`  
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

## Track A — latest prospective state

Latest accepted capture cutoff:

`2026-09-16T12:00:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T120000Z`

Capture state:

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

### Accepted resolver-v1.2 outcome at 12:00Z

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

Four primary families remain causal/open at 12:00Z:

- SUIUSDT entry `08:00Z`: `16/32` M15 bars;
- XRPUSDT entry `08:00Z`: `16/32` M15 bars;
- ADAUSDT entry `08:15Z`: `15/32` M15 bars;
- DOGEUSDT entry `08:15Z`: `15/32` M15 bars.

If STOP/3R does not occur first, max-hold boundaries remain `16:00Z` and `16:15Z` on 2026-09-16.

## Resolver v1.2 hardening

v1.2 preserves v1.1 semantics and changes only the absolute prior-price identity guard:

`2e-9 -> 3e-9`

Hardening at 12:00Z: **PASS**.

- observed maximum relevant drift passes;
- an inside-tolerance case passes;
- an outside-tolerance `3.5e-9` case fails closed;
- missing funding snapshot fails closed with `FUNDING_SUMMARY_MISSING`;
- `50/50` prior resolved observations remain present;
- economic/terminal mismatches `0`;
- aged-out immutable accepted outcomes preserved `6`.

Hardening report SHA256:

`6b780390daabad1b74824bcc2a01fdbc40457b639aa253dc425c4334155fa369`

## Provenance audit

12:00Z provenance audit: **PASS**.

- family set `43/43` matches outcomes;
- primary identity mismatches `0`;
- symbol/side family inconsistencies `0`;
- exact identity duplicates after ledger dedup `0`;
- multi-observation families `13`, expected under family semantics;
- observations and families hashes match accepted summary.

Report SHA256:

`5c4341421d1e702f3256e50639c9e909c1880053346bc26a1d98142e6d8d4e0e`

## Post-30 / portfolio diagnostics

Current 39-resolved-family evidence remains diagnostic only.

Base findings:

- LONG expectancy `-0.585215R`;
- SHORT expectancy `-0.679800R`;
- no supported general LONG-only / SHORT-exclusion rule;
- obstacle `<1R/<3R` remains hypothesis-generating but the original broad contrasts do not survive BH adjustment;
- raw VSA does not provide reliable separation;
- max concurrent exposure `6`;
- largest correlated cohort `4`.

12:00Z report hashes:

- descriptive `81c90dbedf726366f26bdb0703f6dd9ea5ddc0b39237c0ebf2a882771ea0cc17`;
- statistical `38063ca5d80b9cb8da02d17f3b92cc02b3b151cfb658f1b9dcbba1c4476b8fc2`.

### Registered hypothesis: SHORT × low H1 EMA separation / ATR

Exploratory data-derived tercile cutpoint:

`H1 EMA20/50 separation / ATR14 < 0.9033277894201235`

Prospective diagnostic:

- LOW SHORT: `n=10`, expectancy `-0.137355R`;
- other SHORT: `n=16`, expectancy `-1.018829R`;
- difference `+0.881473R`;
- permutation `p≈0.00061`;
- BH-adjusted `q≈0.00366` across six exploratory interaction contrasts;
- leave-one-symbol-out sign remains positive `8/8`.

Important limitation: LOW observations are concentrated mainly on `2026-09-15`, so regime/time confounding remains plausible. The threshold is post-hoc and is **not a rule**.

Report hashes:

- extended diagnostics `22ef770b4f9be8dee4c5f9121df9a28afda6ea319d6a86ba6dcc4d2fa1eb80e2`;
- interaction statistics `4a9160e718b5f59e88aa6ae47ecc695ab021030bdd551b0c1460331b17eb64ed`;
- leave-one-symbol-out robustness `ee7028f64f87a2c995651f19fed6dbc6a46843a27507c87f31d119112f0210ba`.

## Track B — causal historical context

Accepted corrected causal rolling-context results remain:

| Window | Trades | Expectancy R | Stress expectancy R |
|---|---:|---:|---:|
| P25 | 214 | +0.259415 | +0.224861 |
| R90 | 531 | +0.031637 | -0.009676 |
| R180 | 1073 | -0.013131 | -0.042896 |
| R365 | 2099 | -0.051000 | -0.074531 |

Current prospective expectancy `-0.648272R` and win rate `23.08%` are below all four historical windows. This reinforces a regime/current-condition weakness interpretation.

Historical-vs-prospective report SHA256:

`dbb09c81ee29e5da43e825b9b9a7d9e72f213c6eb1b2b01f4318fb43d2e35315`

The prospective-derived SHORT low-trend cutpoint has a better-than-rest SHORT expectancy by sign in all four historical windows, including P25 and R365 with small permutation p-values. This is **historical hypothesis context only**, not fresh OOS validation.

Historical-context report SHA256:

`7be8b49cf07ed0798646b6cc6b54277e28d3dcf379c257e251637dae4d0c23ac`

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

Current state remains **39 resolved primary families**. Historical trades never count toward these thresholds.

The SHORT-low-trend result is registered as a **future-version hypothesis only**. It does not authorize an EMA-separation filter, a SHORT filter, or the specific `0.9033277894` threshold in frozen v2.2.

No evidence currently authorizes RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue causal prospective collection/resolution under the `30–49` tier;
2. resolve the four open primary families after STOP/3R or their actual max-hold boundaries;
3. preserve resolver v1.2 hardening and provenance invariants;
4. track the SHORT-low-trend hypothesis without modifying frozen v2.2; any future test must be preregistered and use fresh independent evidence;
5. keep holdout closed and disk-retention timer disabled.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
