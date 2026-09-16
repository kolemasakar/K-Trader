# K-Trader Current State

Updated: 2026-09-16 through accepted prospective cutoff `2026-09-16T09:45:00Z` and extended-soak closure.

Current checkpoint: `docs/checkpoints/2026-09-16_EXTENDED_SOAK_CLOSURE_POST_CATCHUP.md`  
Resolver v1.1 specification: `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1_1.md`  
Historical methodology checkpoint: `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`  
Previous transition bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md` — active-soak instructions superseded by the current checkpoint.

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

`2026-09-16T09:45:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T094500Z`

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

- bundle set `98911f514bc64e264fcc88adc5bc37b84f053e89b4ae22f038cc416952f5f599`;
- bundle export summary `d6e56e6fb8a7cfcb72b1ba90dc9bbbe906b8b111dbab56bd013fc6b046ce477b`;
- shadow summary `1e5d03dfb3f83551dfe73e2ca3168fcd453a03414ef6cc6f14deca3391cbc978`;
- event file `534a3320d7acf10b2bc80b5741456172e31967125b05c5ddd07b6e10125a8fdd`.

Rebuilt prospective ledger:

- valid snapshots `14`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- deduplicated events `359`;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `648742a4d7b20b941ce26d35cbd2a86be2065a241a47990ddace1cea0d48c5cb`.

Persisted official Binance USD-M funding snapshot:

- symbols `19`;
- records `1849`;
- summary SHA256 `d793079cb3fa629b53fb8bff8e198117229e9ac45e923d4dfa836a2bcac322ea`.

### Accepted outcomes at 09:45Z

Canonical output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1/20260916T094500Z`

State:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- win rate `23.076923076923077%`;
- resolved expectancy `-0.6482720083734612R`;
- terminal states `26 STOP / 13 TIME_EXIT`;
- evidence status `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- network used by final resolver `false`;
- holdout opened `false`;
- production action `false`.

Outcome hashes:

- observations `e39e4d29c4b08fb823c3a41d1ac807c693dd1bc8c10e6fe116059eb7c453e9c0`;
- families `070ab48b4838b9bdc81041b71a268f01fba2100ad04679e8b3916adfa75eda2f`;
- summary `cd4bc59764ff15e4f9bc012979fb2d40436ae4d3ccb721686b8daaab423cba25`.

The four unresolved primary families are fresh SHORT entries at `08:00Z–08:15Z` on XRPUSDT, SUIUSDT, DOGEUSDT and ADAUSDT with only `6–7` closed M15 bars available at the accepted cutoff.

## Offline resolver v1.1

The original offline resolver v1 remains preserved. It has two known continuity limitations:

- exact-float cache identity weakness;
- after a long pause, accepted early entries can age out of the newest `400`-M15 bundle before v1 attempts prior-cache reuse.

Versioned v1.1 is now canonical for continuation:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_1.py`

Key behavior:

- stable prior identity `(setup_family_id, symbol, side, entry_time)`;
- narrow entry/stop numerical guard (`2e-9` absolute, `1e-12` relative);
- accepted resolved terminal outcomes remain immutable if their source bars age out;
- accepted outcomes are revalidated when causal source bars remain available;
- new observations fail closed if their source entry bar is unavailable;
- new realized economics use persisted official funding snapshots;
- final resolution uses no network.

Post-soak validation preserved all `12` previously accepted primary-family outcomes exactly.

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
- explicit allowlist required; shipped example has no eligible paths;
- `/data/research` is the allowed base;
- holdout/symlink/overlap protections are fail-closed;
- latest prospective capture protection is supported;
- manifests are hashed;
- live validation at `18.97%` returned `BELOW_TRIGGER_NO_ACTION`;
- forced planner validation selected one `6,907,004`-byte test candidate and performed no deletion;
- systemd service/timer templates are present and syntactically valid apart from the expected pre-install missing-helper warning.

Host installation is still **PENDING** because current SentinelX sudo policy intentionally does not permit arbitrary writes to `/usr/local/sbin`, `/etc/k-trader` or `/etc/systemd/system`. No privilege expansion was performed.

## Governance

Prospective thresholds remain:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Current state is **39 resolved families**, therefore diagnostics only. Historical trades never count toward these thresholds.

No current evidence authorizes in-place retuning, direction filtering, RR/max-hold/risk changes, holdout access, production mutation or Phase 12 activation.

## Next work order

1. continue diagnostic-only analysis under the `30–49` prospective governance tier;
2. resolve the four currently open primary families causally after sufficient closed M15 bars exist, using resolver v1.1 and persisted official funding snapshot semantics;
3. review and explicitly classify the disk-retention eligible allowlist before any destructive mode is designed;
4. perform only a bounded owner-side root installation of the dry-run retention timer; do not grant general sudo;
5. keep frozen v2.2 unchanged and holdout closed.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
