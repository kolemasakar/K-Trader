# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T10:30:00Z`, resolver-v1.1 parity acceptance and disk-retention dry-run validation.

Current checkpoint: `docs/checkpoints/2026-09-16_POST_SOAK_1030Z_AND_DISK_RETENTION_DRY_RUN.md`  
Post-30 diagnostic baseline: `docs/checkpoints/2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md`  
Resolver v1.1 specification: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_1.md`  
Historical methodology checkpoint: `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`  
Previous transition bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md` — active-soak instructions are superseded by the current checkpoint.

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Latest verified runtime state on `2026-09-16`:

- host `k-trader-prod-vnic`;
- container `k-trader-ktrader-1` healthy;
- `/health status=ok`;
- mode `read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state, not an outage;
- root filesystem `/dev/sda1` is `45G`, approximately `19%` used;
- no production deploy or container restart was performed by the post-soak research work.

Container mount inspection established the production data mapping:

`host /opt/k-trader/data -> container /data`

## Extended soak closure and APT

Extended soak:

`2026-09-14 06:08 Europe/Kyiv -> 2026-09-16 09:00 Europe/Kyiv`

Result:

`EXTENDED_PRODUCTION_SOAK = PASS`

The earlier anomalous `15G / 87%` reading was not the verified K-Trader filesystem. Re-checking the identified SentinelX host showed the expected `45G` root filesystem near the soak-start `18%` state.

APT runtime masks were removed with the existing bounded helper after soak acceptance.

Current APT state:

- `apt-daily.timer = enabled / active`;
- `apt-daily-upgrade.timer = enabled / active`;
- transient post-unfreeze package-manager activity completed.

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

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed. No rebase or force update is authorized or used.

## Track A — prospective evidence

Latest accepted cutoff:

`2026-09-16T10:30:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T103000Z`

Controlled catch-up capture:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- missing symbols `0`;
- signal bars evaluated `6574`;
- current-capture events `292`;
- current-capture eligible observations `44`;
- current-capture unique eligible families `34`;
- holdout opened `false`;
- production action `false`.

Capture hashes:

- bundle set `a0ba2edf0149cfd0db17d72a0c8d7870a50a1ef10d0d9d733142fbb899fa8b3e`;
- shadow summary `acba842b66a5618d7944ceadeea978cdaba1cf1bb973c9eae495f7e312f5d68e`;
- event file `20e639cbaa017e6b7da3b0be8aaa5f0e1c539d738a8f4813f83a336cc861bd68`.

Rebuilt prospective ledger:

- valid snapshots `15`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `31f92f56a74ec4004e1e0922631907b8f5dbafc5b47022bf6f4cf500144473d6`.

Persisted official Binance USD-M funding snapshot:

- symbols `19`;
- records `1849`;
- summary SHA256 `e6a9c13b6c5ba6719c6b67f67269a5be56e57bfb7785a4fa77474c362c84affc`.

### Accepted outcomes at 10:30Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1/20260916T103000Z`

State:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- win rate `23.076923076923077%`;
- resolved expectancy `-0.6482720085510278R`;
- evidence status `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- network used by final resolver `false`;
- holdout opened `false`;
- production action `false`.

Outcome hashes:

- observations `a92ea777ef4e97625611cf86340a91394d46b347402010f97c032b960052a185`;
- families `57e983858608398832f1cc8d54c4dad85b9baf7eafcc823cd0211d8f4108238f`;
- summary `230ef51493c55c627f26b617657bd94c1ad3dc0fa18321a718712b2c8a3ad483`.

## Offline resolver v1.1

The original offline resolver v1 remains preserved. It has two known continuity limitations:

- exact-float cache identity weakness;
- after a long pause, accepted early entries can age out of the newest `400`-M15 bundle before v1 attempts prior-cache reuse.

Versioned v1.1 is canonical for continuation:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_1.py`

Key behavior:

- stable prior identity `(setup_family_id, symbol, side, entry_time)`;
- narrow entry/stop numerical guard (`2e-9` absolute, `1e-12` relative);
- accepted resolved terminal outcomes remain immutable if their source bars age out;
- accepted outcomes are revalidated when causal source bars remain available;
- new observations fail closed if their source entry bar is unavailable;
- new realized economics use persisted official funding snapshots;
- final resolution uses no network.

10:30Z continuity accounting:

- prior accepted terminal observations reused `17`;
- current-path revalidated `11`;
- source-window expired but immutable accepted terminal observations `6`;
- new resolved observations `33`;
- new unresolved observations `6`.

Parity acceptance:

- `17/17` previously accepted observations retained with zero economic/terminal-field mismatches;
- archived 13:00Z bundle replay reproduced terminal state and exit time for `17/17` observations with zero mismatches.

## Post-30 diagnostics

The accepted diagnostic baseline remains descriptive only. Current prospective evidence does not authorize an in-place rule change.

Key findings at 39 resolved families:

- current data do not support LONG-only or SHORT-exclusion behavior;
- rich obstacle distance remains the strongest hypothesis-generating feature, but current exploratory contrasts do not survive multiple-comparison adjustment;
- raw signal-bar VSA does not show reliable prospective separation;
- fees, funding and execution drag remain material and mandatory in future evaluation;
- correlated simultaneous exposure exists as a portfolio diagnostic dimension.

Canonical baseline:

`docs/checkpoints/2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md`

## Track B — corrected causal historical replay

Historical inference continues to use the corrected causal rolling-context replay. Earlier unbounded-context Historical Expansion v1 results are superseded for inference.

Accepted replay semantics:

- M15 context exactly `400` closed bars;
- H1 context exactly `300` closed bars;
- original frozen `signal_at()` and `level_features()`;
- original 3R / 32-M15 max hold / STOP-first / fees/slippage/funding;
- no holdout access;
- no production action.

Prospective parity gate remains PASS with `0` mismatches.

Accepted corrected historical results:

| Window | Cohort | Trades | Expectancy R | Stress expectancy R |
|---|---:|---:|---:|---:|
| P25 | 19 | 214 | +0.259415 | +0.224861 |
| R90 | 19 | 531 | +0.031637 | -0.009676 |
| R180 | 19 | 1073 | -0.013131 | -0.042896 |
| R365 | 17 | 2099 | -0.051000 | -0.074531 |

Interpretation remains unchanged: v2.2 is recent/regime-dependent, not long-horizon robust. SHORT weakness remains a future-version hypothesis only; no in-place direction filter is authorized.

## Disk retention

Approved policy remains:

- trigger at filesystem usage `>=80%`;
- oldest `20%` of explicitly eligible reproducible/temporary data;
- production/runtime, source/config/secrets, canonical/pinned evidence, current prospective artifacts, holdout and required audit evidence are protected;
- manifest-first, deterministic, oldest-first and fail-closed.

Canonical policy:

`docs/operations/DISK_RETENTION_POLICY.md`

Dry-run implementation:

`ops/disk_retention/`

Current implementation status:

- planner is **DRY-RUN ONLY** and contains no deletion/apply mode;
- host-side allowed base is now correctly `/opt/k-trader/data/research` because `/opt/k-trader/data` is bind-mounted to container `/data`;
- production config is `ops/disk_retention/disk-retention.production.k-trader-prod-vnic.json`;
- eligible paths are limited to direct symbol-bundle directories under two explicitly superseded/reproducible historical datasets;
- all prospective/shadow/current strategy evidence remains ineligible/protected;
- holdout/symlink/overlap protections are fail-closed;
- manifests are hashed.

Refined dry-run validation at approximately `19%` filesystem usage:

- trigger `false`;
- eligible candidates `38`;
- eligible bytes about `441 MB`;
- target oldest `20%` about `88 MB`;
- deterministic plan selected `20` candidates totaling about `97 MB`;
- actual deletion `0`.

Manual refined manifest SHA256:

`e49439915269de4d29f9c9270344a86179b3350d767ec2b0d0e1261613b11a2b`

Repository-planner production-equivalent validation:

- status `FORCED_DRY_RUN_PLAN_READY`;
- `38` eligible candidates;
- `20` would-delete candidates;
- `97,393,279` would-delete bytes;
- deletion remained impossible by design;
- validation manifest SHA256 `160cd8e2547115098c02d8989f4bce6cc49a9eb6693d3c24f26d77d4b212b16c`.

Host installation is still **PENDING** because current SentinelX sudo policy intentionally does not permit arbitrary writes to `/usr/local/sbin`, `/etc/k-trader` or `/etc/systemd/system`. No privilege expansion was performed. Installation must use a bounded owner-side root action, followed by a manual oneshot/manfiest review before the hourly timer is enabled.

## Governance

Prospective thresholds remain:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current state is **39 resolved families**, therefore diagnostics only. Historical trades never count toward these thresholds.

No current evidence authorizes in-place retuning, direction filtering, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue prospective collection/resolution under the `30–49` prospective governance tier;
2. resolve the four currently open primary families causally after sufficient closed M15 bars exist, using resolver v1.1 and persisted official funding snapshot semantics;
3. perform only a bounded owner-side root installation of the reviewed dry-run disk-retention helper/config/service/timer; do not grant general sudo;
4. run the retention oneshot manually, inspect its hashed manifest, then enable the hourly timer only after acceptance;
5. keep frozen v2.2 unchanged and holdout closed.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
