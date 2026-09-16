# K-Trader — Post-Soak 10:30Z Catch-Up and Disk-Retention Dry-Run

Date: 2026-09-16  
Status: **ACCEPTED / DIAGNOSTIC-ONLY / DRY-RUN RETENTION VALIDATED / HOST TIMER INSTALL PENDING**

## Governance boundary

- Phase 11G remains active.
- Frozen strategy remains `candidate_rule_set_v2_2`.
- Holdout remains unopened and unauthorized.
- No production trading action occurred.
- No frozen RR, risk, max-hold, direction, symbol or eligibility rule changed.
- Current prospective tier remains `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`.

## Extended soak closure

The extended production soak ended on 2026-09-16 and was accepted as PASS.

Verified production host state:

- host `k-trader-prod-vnic`;
- root filesystem `/dev/sda1`, approximately `45G` total and `19%` used;
- container healthy;
- no production deployment or container restart performed by this post-soak work.

The earlier `15G / 87%` disk observation was not the verified K-Trader root filesystem and is superseded by the identified-host checks.

APT runtime masks were removed after soak acceptance. Both `apt-daily.timer` and `apt-daily-upgrade.timer` are restored to enabled/active state.

## Controlled prospective catch-up — 10:30Z

Cutoff:

`2026-09-16T10:30:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T103000Z`

Capture result:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- missing symbols `0`;
- signal bars evaluated `6574`;
- current-capture events `292`;
- current-capture eligible observations `44`;
- current-capture unique eligible families `34`;
- holdout opened `false`;
- production action `false`.

Frozen identity remained unchanged:

- harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`.

Capture/ledger hashes:

- bundle set `a0ba2edf0149cfd0db17d72a0c8d7870a50a1ef10d0d9d733142fbb899fa8b3e`;
- shadow summary `acba842b66a5618d7944ceadeea978cdaba1cf1bb973c9eae495f7e312f5d68e`;
- event file `20e639cbaa017e6b7da3b0be8aaa5f0e1c539d738a8f4813f83a336cc861bd68`;
- ledger event set `31f92f56a74ec4004e1e0922631907b8f5dbafc5b47022bf6f4cf500144473d6`.

Rebuilt ledger state:

- valid snapshots `15`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- eligible observations `56`;
- unique eligible families `43`.

## Persisted official funding

Funding root:

`/data/research/phase11g/v2_2_shadow_20260916T103000Z/funding_offline_v1`

- source: official Binance USD-M `/fapi/v1/fundingRate`;
- symbols `19`;
- records `1849`;
- summary SHA256 `e6a9c13b6c5ba6719c6b67f67269a5be56e57bfb7785a4fa77474c362c84affc`.

## Canonical resolver v1.1

Canonical continuation resolver:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_1.py`

Accepted output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1/20260916T103000Z`

State:

- eligible observations `56`;
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

Resolver continuity accounting:

- prior accepted terminal observations reused `17`;
- of those, current-path revalidated `11`;
- source bars aged out of the current rolling window `6` and were preserved as immutable accepted terminal outcomes;
- new resolved observations `33`;
- new unresolved observations `6`.

Outcome hashes:

- observations `a92ea777ef4e97625611cf86340a91394d46b347402010f97c032b960052a185`;
- families `57e983858608398832f1cc8d54c4dad85b9baf7eafcc823cd0211d8f4108238f`;
- summary `230ef51493c55c627f26b617657bd94c1ad3dc0fa18321a718712b2c8a3ad483`.

### Resolver parity acceptance

Two independent checks passed:

1. all `17/17` previously accepted 13:00Z observations were present in the v1.1 continuation result with **0 terminal/economic-field mismatches**;
2. replay against the archived `2026-09-13T13:00:00Z` bundle reproduced terminal state and exit time for **17/17 observations with 0 mismatches**.

Therefore the v1.1 continuity handling for aged rolling bundles is accepted.

## Disk-retention production path correction

Container mount inspection established:

`host /opt/k-trader/data -> container /data`

Therefore host-side disk-retention automation must operate below:

`/opt/k-trader/data/research`

not `/data/research`.

Repository artifacts were aligned accordingly:

- production config `ops/disk_retention/disk-retention.production.k-trader-prod-vnic.json`;
- hardened service `ops/disk_retention/ktrader-disk-retention.service` passes `--allowed-base /opt/k-trader/data/research` and grants that tree read-only access;
- hourly timer remains `ops/disk_retention/ktrader-disk-retention.timer`.

## Dry-run allowlist and validation

The production allowlist is intentionally narrow. Only direct symbol-bundle directories under two explicitly superseded/reproducible historical datasets are eligible:

- `historical_expansion_v1_20260905T144500Z/bundles/*`;
- `historical_robustness_v1_20260905T144500Z/bundles/*`.

Results, summaries, funding artifacts, current/prospective/shadow research, holdout material and canonical strategy-benchmark evidence are not eligible.

A first coarse whole-root dry-run was rejected as too coarse because selecting the oldest 20% would have selected both large root directories and effectively nominated 100% of eligible bytes.

Refined symbol-bundle granularity was then validated:

- current root filesystem usage about `19%`;
- trigger `80%` therefore `false`;
- eligible candidates `38`;
- eligible bytes about `441 MB`;
- 20% target about `88 MB`;
- deterministic oldest-first plan selected `20` bundle candidates totaling about `97 MB`;
- deletion count `0`.

Manual refined manifest:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/disk_retention_dry_run/20260916T111729Z/manifest.json`

SHA256:

`e49439915269de4d29f9c9270344a86179b3350d767ec2b0d0e1261613b11a2b`

The repository planner was also run with the production-equivalent container path and `--force-plan`:

- status `FORCED_DRY_RUN_PLAN_READY`;
- disk used `18.9996%`;
- eligible candidates `38`;
- would-delete candidates `20`;
- would-delete bytes `97,393,279`;
- actual deletion `false` by design.

Validation manifest SHA256:

`160cd8e2547115098c02d8989f4bce6cc49a9eb6693d3c24f26d77d4b212b16c`

## Host installation boundary

Host installation remains pending.

Current SentinelX privilege policy does not permit arbitrary root writes to:

- `/usr/local/sbin`;
- `/etc/k-trader`;
- `/etc/systemd/system`.

Attempting the required root directory creation correctly failed for lack of general sudo authorization. No privilege expansion was performed.

This is an intentional security boundary. Installation must be completed through a bounded owner-side root action. The installed v1 remains dry-run-only and contains no deletion/apply mode.

## Next work order

1. Continue prospective collection/resolution under the `30–49` diagnostic governance tier until the next boundary `>=50 resolved primary families`.
2. Keep frozen v2.2 unchanged and holdout closed.
3. Perform the bounded owner-side root installation of the already-reviewed dry-run disk-retention helper/config/service/timer.
4. Run the oneshot manually once on the host, inspect its hashed manifest, then enable the hourly timer only after that acceptance.
5. Do not design or enable destructive retention until a separate version is explicitly reviewed and approved.
