# K-Trader Current State

Updated: 2026-09-14 through accepted prospective cutoff `2026-09-13T13:00:00Z` and extended production soak start.

Current checkpoint: `docs/checkpoints/2026-09-14_EXTENDED_SOAK_PAUSE_START.md`  
Prospective checkpoint: `docs/checkpoints/2026-09-13_V2_2_PROSPECTIVE_1300Z.md`  
Prospective outcome addendum: `docs/checkpoints/2026-09-13_V2_2_PROSPECTIVE_1300Z_OUTCOME_ADDENDUM.md`  
Historical methodology checkpoint: `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`  
Bootstrap: `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md`

## Production

Accepted/deployed application SHA:

`81b79b281a4cc330b7c11058d202e0d74fb6d70e`

Accepted soak-start runtime state at `2026-09-14T03:08Z`:

- `status=ok`;
- `mode=read_only`;
- `data_ready=true`;
- provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness state;
- root filesystem usage `18%`;
- no production deploy or restart was performed during the latest research work.

## Extended soak pause

Active window:

`2026-09-14 06:08 Europe/Kyiv -> 2026-09-16 09:00 Europe/Kyiv`.

Allowed:

- published K_Trader read-only analysis and data access;
- production API read-only traffic;
- normal runtime/data-pipeline activity;
- passive logs and health checks.

Forbidden until soak closure:

- deploy or container restart;
- configuration mutation;
- frozen v2.2 retuning;
- holdout opening;
- manual prospective capture/resolution;
- package upgrades;
- installation of new VM automation, including disk-retention timer.

APT freeze at soak start:

- `apt-daily.timer = masked-runtime`;
- `apt-daily-upgrade.timer = masked-runtime`;
- no next timer activation;
- `apt-daily.service = inactive`;
- `apt-daily-upgrade.service = inactive`;
- no package-management lock holder observed.

The timer units may show `failed` under `systemctl is-active` while runtime-masked; the corresponding services are inactive and this is the accepted freeze state.

## Research isolation

Research branch:

`research-strategy-benchmark-v1`

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

Latest accepted capture/ledger cutoff:

`2026-09-13T13:00:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T130000Z`

Capture state:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- signal bars evaluated `3097`;
- deduplicated events `131`;
- eligible observations `17`;
- unique eligible families `12`;
- valid snapshots `13`;
- rejected snapshots `1` known infrastructure-invalid snapshot;
- holdout unopened;
- production action false.

Capture hashes:

- bundle set: `61b4dfe96204bef61ea04cbec4b783de476f3cb2ef57a6e1cc0643fdde4b05b5`;
- bundle export summary: `a1776c6c1a834d5476317ce41ff6ccadc694c425938fa644e5de417581e7210b`;
- shadow summary: `b80bbd4c4e886bf09eee9e0c90eae5e9d9a4935c3172b591ca13b98d1607789a`;
- event file: `06567e0bdc6d848bededdb5fa35f0a3e79499ff11b5cd3ce8b7bdd1fa56a2c04`;
- ledger event set: `dd49c4bfffe2acdd4db8227e0d1d9a39a754c1ebf66d187257d6194681b3c5e2`.

Accepted offline outcome state at 13:00Z:

- unique primary families `12`;
- resolved primary families `12`;
- unresolved primary families `0`;
- resolved wins/losses `1 / 11`;
- resolved win rate `8.3333%`;
- resolved expectancy `-0.9007780994315739R`;
- evidence status `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`;
- network used by final offline resolver: false;
- holdout opened: false;
- production action: false.

Outcome hashes:

- funding summary `a86f971d935a6fa73aba60279def60f73561dd74d54d78b41e605755f0c7a272`;
- promoted cache `c0ba653fc0bc12f1b4253619f0fe7b5e56949d54b24fca13e6fec6387add2284`;
- observation set `3e292b44d9ad2641e4e47c96c96492533167a260c7628e04ba9e228e7e6386fb`;
- family set `28a417ec91457291e88bedda53fc0a3e5ab21d1cc419312baa878555e5b63b17`;
- outcome summary `a4ea3745ac3b325c6c6aace8d6427a0c159c3810bac49674cfca883d25333c3d`.

The three VTHO primary families that were unresolved at 12:00Z were resolved by 13:00Z as STOP outcomes. Two additional VTHO observations are correlated diagnostics and do not increase independent family evidence.

Important resolver implementation note:

- offline resolver v1 has an exact-float cache-identity weakness;
- stable identity should be `(setup_family_id, symbol, side, entry_time)` with tight numerical tolerance for entry/stop comparison;
- no repository v1.1 fix is currently canonical;
- the accepted 13:00Z result used a temporary normalized/promoted cache plus unchanged offline resolver for final verification.

Next prospective hard milestone:

`>=30 unique resolved prospective frozen-v2.2 setup families`.

## Track B — corrected causal historical replay

Historical inference uses the corrected causal rolling-context replay. Earlier unbounded-context Historical Expansion v1 results are superseded for inference.

Accepted replay semantics:

- rolling M15 context exactly `400` closed bars;
- rolling H1 context exactly `300` closed bars;
- original frozen `signal_at()` and `level_features()`;
- original 3R / 32-M15 max hold / STOP-first / fees/slippage/funding;
- no holdout access;
- no production action.

Prospective parity gate:

- symbols `19/19`;
- decision bars `1824`;
- signal cases `70`;
- structural cases `69`;
- mismatches `0`;
- PASS;
- parity SHA256 `47b03d3c7280d8cc2c7f3f73af529fb2fa89e9ccf47c8b2132d289438396effe`.

Accepted corrected historical results:

| Window | Cohort | Trades | Expectancy R | Stress expectancy R |
|---|---:|---:|---:|---:|
| P25 | 19 | 214 | +0.259415 | +0.224861 |
| R90 | 19 | 531 | +0.031637 | -0.009676 |
| R180 | 19 | 1073 | -0.013131 | -0.042896 |
| R365 | 17 | 2099 | -0.051000 | -0.074531 |

Interpretation remains unchanged: v2.2 is a recent/regime-dependent candidate, not a long-horizon robust strategy. SHORT weakness is a future-version hypothesis only; no in-place LONG-only filter is authorized.

Accepted runtime evaluator SHA256:

`c0dead4957622515a7d432d8142ac7ae8915f46e36905a5cc0e483c93e78b7e7`

## Disk retention policy

Approved requirement:

- trigger when filesystem usage reaches or exceeds `80%`;
- delete oldest `20%` of explicitly eligible reproducible/temporary data;
- protected data includes production DB/runtime state, source/config/secrets, canonical docs/checkpoints, pinned evidence, current prospective artifacts, holdout and required audit manifests;
- cleanup must be manifest-first, deterministic, oldest-first and fail-closed.

Canonical policy:

`docs/operations/DISK_RETENTION_POLICY.md`

The automatic VM cleanup mechanism is NOT installed yet. Installation is deferred until after soak closure.

## Governance

Prospective thresholds remain unchanged:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Historical trades never count toward prospective family thresholds. Neither historical results nor the current prospective sample authorize in-place retuning of frozen v2.2.

## Repository

Canonical `main` baseline:

`4919fea4397d34898ddc7d4215ea898e6caea815`

Research branch remains a descendant of canonical main with no rebase or force update. Production remains deployed on `81b79...`; research/documentation updates do not require redeployment.

## Next work order after soak

At or after `2026-09-16 09:00 Europe/Kyiv`:

1. verify production health, container uptime/restarts, disk, APT/package drift, logs and research state before any mutation;
2. if soak passes, run `sudo /usr/local/sbin/ktrader-apt-freeze unfreeze` and verify normal timer state;
3. perform one controlled prospective catch-up capture at a safe closed-M15 cutoff;
4. rebuild ledger and resolve any new families/outcomes causally, using official funding snapshots when required;
5. preserve frozen v2.2 and keep holdout closed;
6. only after soak closure, implement disk-retention automation using dry-run/allowlist/protected-list/manifest semantics.

Phase 11G remains **ACTIVE**.  
Phase 12 remains **FUTURE / NOT ACTIVE**.
