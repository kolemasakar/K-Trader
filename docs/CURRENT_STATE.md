# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T11:45:00Z`, resolver-v1.2 parity acceptance, updated post-30 diagnostics and completed dry-run retention installation validation.

Current checkpoint: `docs/checkpoints/2026-09-16_PROSPECTIVE_1145Z_RESOLVER_V1_2.md`  
Post-30 diagnostic baseline: `docs/checkpoints/2026-09-16_POST30_PROSPECTIVE_DIAGNOSTIC_BASELINE.md`  
Resolver v1.2 specification: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`  
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
- no production deploy or container restart was performed by the research continuation.

Container mount mapping:

`host /opt/k-trader/data -> container /data`

## Extended soak closure and APT

Extended soak:

`2026-09-14 06:08 Europe/Kyiv -> 2026-09-16 09:00 Europe/Kyiv`

Result:

`EXTENDED_PRODUCTION_SOAK = PASS`

APT runtime masks were removed with the existing bounded helper after soak acceptance.

Current APT state:

- `apt-daily.timer = enabled / active`;
- `apt-daily-upgrade.timer = enabled / active`.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

Current research HEAD at this checkpoint series is descendant of canonical main with no rebase/force update.

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

No frozen rule, RR, 8h max-hold, risk gate, symbol/direction filter or holdout authorization changed.

## Track A — prospective evidence

Latest accepted cutoff:

`2026-09-16T11:45:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T114500Z`

Capture:

- `VALID_SHADOW_CAPTURE`;
- provider `binance_usdm`;
- panel `19/19`;
- missing symbols `0`;
- signal bars evaluated `6574`;
- event count `295`;
- current-capture eligible observations `44`;
- current-capture unique eligible families `34`;
- holdout opened `false`;
- production action `false`.

Capture hashes:

- bundle set `971c4f62fd8d5a5341e8ae625e38558a3ae270be2222488636535619582aa2cf`;
- bundle export summary `ecfefa9a709682615c52daa7a33d55ff03cd9c1e0f3f5bcd5548b0a24f5b4a3a`;
- event file `ed1c6826bb63124a98081bd7998a0bde155c2d02654116146403aa46e767ff7e`;
- shadow summary `d4f52490488867d425a2eda1079b684f18322278c8e66b0272ba55071b574b3b`.

Rebuilt prospective ledger:

- discovered snapshots `17`;
- valid snapshots `16`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- deduplicated events `365`;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `3139b622956c90618222b864ef401ee179f99c18c4b60309822e724aa7288d36`.

No new independent family was added at 11:45Z.

Persisted official Binance USD-M funding snapshot:

- symbols `19`;
- records `1849`;
- summary SHA256 `b1d94137e7cb4474d7ac0a35f1336c1fe337bf0b4deba10bd746db5e8daaa8d3`.

### Accepted outcomes at 11:45Z

Validated v1.2 output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_2/20260916T114500Z`

State:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- win rate `23.076923076923077%`;
- resolved expectancy `-0.6482720085510278R`;
- evidence status `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- network used `false`;
- holdout opened `false`;
- production action `false`.

Validation summary SHA256:

`923d990bdd8d94b676ff0c79a92469ba78b65a469cba689e4d759da2914bd6d2`

## Offline resolver v1.2

Original v1 and versioned v1.1 remain preserved.

v1.2 is the current versioned continuation:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_2.py`

Specification:

`docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_2.md`

v1.2 preserves all v1.1 outcome semantics and output schema. The only change is:

`PRIOR_PRICE_ABS_TOL: 2e-9 -> 3e-9`

The relative tolerance remains `1e-12`.

Reason:

- one stable-identity RAYSOLUSDT observation showed stop representation drift `2.1062864785648117e-9`;
- across all `50` previously resolved observations, maximum entry delta remained exactly `0.0`;
- maximum stop delta was `2.1062864785648117e-9`;
- parity across all `50` previously resolved rows produced `0` terminal/economic mismatches.

11:45Z resolver accounting:

- prior resolved observations reused `50`;
- current-path revalidated `44`;
- source-window-expired immutable accepted outcomes `6`;
- newly resolved observations `0`;
- new unresolved observations `6` representing `4` unresolved primary families.

## Four open primary families

At `11:45Z`:

- SUIUSDT entry `08:00Z`: `15` M15 bars observed; max-hold boundary `16:00Z`;
- XRPUSDT entry `08:00Z`: `15` M15 bars observed; max-hold boundary `16:00Z`;
- ADAUSDT entry `08:15Z`: `14` M15 bars observed; max-hold boundary `16:15Z`;
- DOGEUSDT entry `08:15Z`: `14` M15 bars observed; max-hold boundary `16:15Z`.

No STOP/3R terminal occurred by 11:45Z. They must remain unresolved until a causal terminal occurs or the 32-M15 max-hold boundary is actually reached.

## Post-30 diagnostics

Updated diagnostic-only analysis at 11:45Z remains consistent with the prior accepted baseline.

Descriptive report SHA256:

`ff12665d0781b29a932e66923c88868c66e071e2c89559f49fbeb96c3c1e6717`

Statistical report SHA256:

`e467c88533f1fd989180902b7745afe3f773830ec8dbdb5a8cc629b4c85c6483`

Key findings remain:

- SHORT vs LONG: no statistically supported separation;
- rich obstacle `<1R` / `<3R`: strongest current hypothesis-generating feature, but does not survive Benjamini-Hochberg adjustment;
- raw signal-bar VSA: no reliable separation;
- fees, funding and execution drag remain material;
- correlated simultaneous exposure remains a portfolio diagnostic dimension;
- no diagnostic authorizes an in-place frozen-v2.2 rule change.

## Track B — corrected causal historical replay

Historical inference continues to use the corrected causal rolling-context replay. Earlier unbounded-context Historical Expansion v1 results are superseded for inference.

Accepted replay semantics:

- M15 context exactly `400` closed bars;
- H1 context exactly `300` closed bars;
- original frozen `signal_at()` and `level_features()`;
- original 3R / 32-M15 max hold / STOP-first / fees/slippage/funding;
- no holdout access;
- no production action.

Accepted corrected historical results:

| Window | Cohort | Trades | Expectancy R | Stress expectancy R |
|---|---:|---:|---:|---:|
| P25 | 19 | 214 | +0.259415 | +0.224861 |
| R90 | 19 | 531 | +0.031637 | -0.009676 |
| R180 | 19 | 1073 | -0.013131 | -0.042896 |
| R365 | 17 | 2099 | -0.051000 | -0.074531 |

Interpretation remains unchanged: v2.2 is recent/regime-dependent, not long-horizon robust. SHORT weakness remains a future-version hypothesis only; no in-place direction filter is authorized.

## Disk retention

Approved policy:

- trigger at filesystem usage `>=80%`;
- oldest `20%` of explicitly eligible reproducible/temporary data;
- production/runtime, source/config/secrets, canonical/pinned evidence, current prospective artifacts, holdout and required audit evidence are protected;
- manifest-first, deterministic, oldest-first and fail-closed.

Canonical policy:

`docs/operations/DISK_RETENTION_POLICY.md`

Implementation:

`ops/disk_retention/`

Current state:

- helper `/usr/local/sbin/ktrader-disk-retention` installed;
- config `/etc/k-trader/disk-retention.json` installed;
- systemd service installed and sandbox-tested;
- planner is **DRY_RUN_ONLY** and contains no destructive mode;
- host-side allowed base is `/opt/k-trader/data/research`;
- eligible candidates are limited to direct symbol-bundle directories under two explicitly superseded/reproducible historical datasets;
- all prospective/shadow/current strategy evidence remains ineligible/protected;
- holdout/symlink/overlap protections are fail-closed.

Accepted host dry-run manifest:

- filesystem use `19.000516%`;
- trigger `false`;
- eligible candidates `38`;
- would-delete candidates `20`;
- would-delete bytes `97,393,279`;
- deletion performed `false`;
- manifest SHA256 `d1ecdb98b8d4fc000098482126c3f9542a67562e44b5eddb73411187e3037d20`.

Systemd oneshot sandbox test:

- `Result=success`;
- `ExecMainStatus=0`;
- `ActiveState=inactive` after completion, expected for oneshot.

`ktrader-disk-retention.timer` is **disabled by design**. At current ~19% disk use, hourly dry-run execution provides little operational value and would only generate recurring manifests. No general sudo or Docker privilege was expanded.

## Governance

Prospective thresholds remain:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current state is **39 resolved families**, therefore diagnostics only. Historical trades never count toward these thresholds.

No current evidence authorizes in-place retuning, direction filtering, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue prospective collection under the `30–49` diagnostic-only governance tier;
2. run a fresh capture/funding/resolver cycle after a suitable future closed-bar cutoff; the four currently open primary families may resolve before max hold, otherwise their max-hold boundaries are `16:00Z` and `16:15Z` on 2026-09-16;
3. use resolver v1.2 for continuation and preserve accepted prior terminal outcomes;
4. keep `ktrader-disk-retention.timer` disabled unless disk pressure or an explicitly approved monitoring policy justifies periodic execution;
5. keep frozen v2.2 unchanged and holdout closed.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
