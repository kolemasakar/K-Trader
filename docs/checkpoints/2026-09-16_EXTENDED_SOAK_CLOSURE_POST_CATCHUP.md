# K-Trader — Extended Soak Closure and Post-Soak Catch-up

Date: 2026-09-16  
Status: **ACCEPTED / EXTENDED SOAK PASS / POST-SOAK CATCH-UP COMPLETE**

## Production soak closure

Extended soak window:

`2026-09-14 06:08 Europe/Kyiv -> 2026-09-16 09:00 Europe/Kyiv`

Soak-end audit result:

`EXTENDED_PRODUCTION_SOAK = PASS`

Verified after the deadline:

- host `k-trader-prod-vnic`;
- production image remains `k-trader:81b79b281a4cc330b7c11058d202e0d74fb6d70e`;
- container `k-trader-ktrader-1` remains healthy;
- `/health`: `status=ok`, `mode=read_only`, `data_ready=true`, provider `binance_usdm`;
- scanner `DEGRADED` remains the known fail-closed/history-readiness condition, not an outage;
- root filesystem is `45G`, approximately `19%` used;
- no production deploy or container restart was performed by this work;
- holdout remained unopened.

The earlier anomalous `15G / 87%` disk reading was not the verified K-Trader filesystem. Re-checking the identified SentinelX host showed `/dev/sda1 45G` at `19%`, consistent with the `18%` soak-start state.

## APT restoration

The accepted soak-start runtime masks were removed with the existing bounded helper:

`sudo /usr/local/sbin/ktrader-apt-freeze unfreeze`

Post-unfreeze state:

- `apt-daily.timer = enabled / active`;
- `apt-daily-upgrade.timer = enabled / active`;
- transient package-manager activity completed;
- no K-Trader deploy/restart followed.

## Controlled prospective catch-up

Safe closed-M15 cutoff:

`2026-09-16T09:45:00Z`

Source branch state used for capture:

`583e0252714b2730a17c6f15e5a9c7bab2e3fef4`

The source was executed from a temporary exact-commit archive; the production checkout was not changed.

Frozen identity before execution:

- harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`;
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`.

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T094500Z`

Capture result:

- `VALID_SHADOW_CAPTURE`;
- panel `19/19`;
- missing symbols `[]`;
- provider `binance_usdm`;
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

Rebuilt ledger:

- valid snapshots `14`;
- rejected snapshots `1` known infrastructure-invalid first attempt;
- deduplicated events `359`;
- eligible observations `56`;
- unique eligible families `43`;
- ledger event set SHA256 `648742a4d7b20b941ce26d35cbd2a86be2065a241a47990ddace1cea0d48c5cb`.

## Funding snapshot

The existing v1 offline resolver correctly failed closed on newly resolved observations requiring funding data.

A persisted official Binance USD-M funding snapshot was then collected under the current run root:

`/data/research/phase11g/v2_2_shadow_20260916T094500Z/funding_offline_v1`

Result:

- symbols `19`;
- funding records `1849`;
- summary SHA256 `d793079cb3fa629b53fb8bff8e198117229e9ac45e923d4dfa836a2bcac322ea`.

## Offline resolver continuity finding

`prospective_v2_2_outcome_resolver_offline_v1.py` has a second long-pause limitation in addition to its known exact-float cache weakness: it attempts to recompute every ledger row from the newest `400`-M15 bundle before prior-cache reuse. Accepted early observations can therefore age out of the current bundle and produce `SOURCE_ENTRY_BAR_UNAVAILABLE` followed by `KeyError: target`.

This is a research-tool continuity bug only. Frozen v2.2, production and holdout were unaffected.

## Resolver v1.1

A versioned fix was added without modifying v1:

`research/strategy_benchmark_v1/prospective_v2_2_outcome_resolver_offline_v1_1.py`

Initial source commit:

`579fde247eda1bf214aa79a32820efae31742e2c`

Semantics:

- accepted terminal observations are matched by stable identity `(setup_family_id, symbol, side, entry_time)`;
- entry/stop guard remains fail-closed with absolute tolerance `2e-9` and relative tolerance `1e-12`;
- accepted terminal rows are revalidated against current causal bars when the entry bar remains available;
- if the accepted source bar has aged out, the accepted terminal row remains immutable;
- new observations must have causal source bars available or fail closed;
- newly resolved economics use only the persisted official funding snapshot;
- final resolver network use is `false`.

Validation:

- prior accepted observations reused `17`;
- prior terminal paths revalidated `11`;
- accepted observations whose entry bars aged out `6`;
- maximum accepted-prior entry delta `0`;
- maximum accepted-prior stop delta `1.0704848964725178e-9`;
- all `12` previously accepted primary-family outcomes preserved exactly;
- new resolved observations `32`;
- new unresolved observations `7`.

Canonical v1.1 output:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_1/20260916T094500Z`

Outcome state:

- unique primary families `43`;
- resolved primary families `39`;
- unresolved primary families `4`;
- wins / losses `9 / 30`;
- resolved win rate `23.076923076923077%`;
- resolved expectancy `-0.6482720083734612R`;
- terminal states: `26 STOP`, `13 TIME_EXIT`;
- evidence status `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`;
- holdout opened `false`;
- production action `false`;
- network used by final resolver `false`.

Canonical artifact hashes:

- observations `e39e4d29c4b08fb823c3a41d1ac807c693dd1bc8c10e6fe116059eb7c453e9c0`;
- families `070ab48b4838b9bdc81041b71a268f01fba2100ad04679e8b3916adfa75eda2f`;
- summary `cd4bc59764ff15e4f9bc012979fb2d40436ae4d3ccb721686b8daaab423cba25`.

The four unresolved primary families are fresh SHORT entries from `2026-09-16T08:00Z` and `08:15Z` on XRPUSDT, SUIUSDT, DOGEUSDT and ADAUSDT, with only `6–7` closed M15 bars available at the cutoff. Their unresolved state is normal causal censoring.

## Governance

The project has crossed the preregistered `>=30` resolved prospective-family boundary.

Current level:

`DIAGNOSTIC_30_49_RESOLVED_FAMILIES`

This allows diagnostics only. It does **not** authorize:

- in-place retuning of frozen v2.2;
- LONG-only / SHORT filtering;
- RR, max-hold, risk-gate or symbol-filter changes;
- holdout opening;
- production strategy/risk/execution mutation;
- Phase 12 activation.

## Disk-retention dry-run implementation

The approved retention policy remains `>=80%` filesystem usage -> oldest `20%` of explicitly eligible reproducible/temporary data.

A new fail-closed **dry-run-only** planner was added under:

`ops/disk_retention/`

Properties:

- no delete/apply code exists in v1;
- explicit allowlist only;
- allowed base restricted to `/data/research`;
- symlinks and overlapping candidates fail closed;
- holdout paths are always protected;
- protected paths/globs and latest prospective capture protection are supported;
- plans are oldest-first by timestamp and target `20%` of eligible bytes;
- every run writes a hashed manifest.

Validation against the live data filesystem:

- root usage `18.97%`;
- real result `BELOW_TRIGGER_NO_ACTION`;
- forced planner validation selected one test candidate totaling `6,907,004` bytes;
- candidate remained present after the test;
- `DELETION_PERFORMED=false`.

Systemd service/timer templates were added. `systemd-analyze verify` found no template syntax issue; the expected pre-install warning is that `/usr/local/sbin/ktrader-disk-retention` does not yet exist. Unrelated existing OCI agent unit permission warnings were also emitted.

### Host installation boundary

The mechanism is **not installed on the host yet**.

Current SentinelX sudo grants intentionally permit only bounded APT helper, Docker read/exec and selected service inspection/restart operations. They do not permit writing `/usr/local/sbin`, `/etc/k-trader` or `/etc/systemd/system`.

No sudo or Docker privilege was broadened. Host installation therefore remains a separate bounded owner-side root action after review.

## Phase state

- Phase 11G: **ACTIVE**;
- Phase 12: **FUTURE / NOT ACTIVE**;
- frozen candidate: unchanged;
- holdout: **UNTOUCHED / NOT AUTHORIZED**;
- production deployed SHA: unchanged `81b79b281a4cc330b7c11058d202e0d74fb6d70e`.

## Next work order

1. continue diagnostic-only prospective analysis under the `30–49` governance tier;
2. resolve the four currently open families causally after sufficient closed M15 bars exist, using v1.1 plus persisted funding snapshot semantics;
3. review/approve an explicit disk-retention eligible allowlist before any future destructive mode is designed;
4. perform the bounded root installation of the dry-run timer without granting general sudo;
5. keep holdout closed and frozen v2.2 unchanged.
