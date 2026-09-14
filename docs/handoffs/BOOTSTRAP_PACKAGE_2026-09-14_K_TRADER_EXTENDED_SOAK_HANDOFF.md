# BOOTSTRAP PACKAGE — K-Trader Extended Soak Handoff

Date: 2026-09-14
Status: AUTHORITATIVE CHAT TRANSITION PACKAGE
Branch: `research-strategy-benchmark-v1`

## Recovery instruction

In a new chat, use:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md">>`

Then continue from the work order in this package. Do not reconstruct state from older bootstrap files if this package is available.

## Project phase

- Phase 11G: ACTIVE
- Phase 12: FUTURE / NOT ACTIVE
- production deployed SHA: `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- canonical main baseline: `4919fea4397d34898ddc7d4215ea898e6caea815`
- research branch: `research-strategy-benchmark-v1`
- no rebase / no force update

## Production state at handoff

Latest accepted verification at soak start (`2026-09-14T03:08Z`):

- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner `DEGRADED` = known fail-closed/history-readiness state, not outage
- root disk usage `18%`

Published K_Trader may be used during soak for read-only analysis and data access.

## Active extended soak pause

Window:

- start: `2026-09-14 06:08 Europe/Kyiv`
- planned end: `2026-09-16 09:00 Europe/Kyiv`

Allowed during soak:

- published K_Trader read-only use
- production API read-only traffic
- normal runtime/data-pipeline activity
- passive logs and health checks

Forbidden until soak closure:

- deploys
- container restarts
- configuration mutations
- package upgrades
- frozen v2.2 retuning
- holdout opening
- manual prospective captures/resolution runs
- installation of new VM automation, including disk-retention timer

APT freeze accepted at start:

- `apt-daily.timer = masked-runtime`
- `apt-daily-upgrade.timer = masked-runtime`
- no next activation
- `apt-daily.service = inactive`
- `apt-daily-upgrade.service = inactive`
- no package lock holder observed

Helper:

`/usr/local/sbin/ktrader-apt-freeze`

Do not unfreeze before soak-end verification.

## Frozen v2.2 identity

Strategy:

`candidate_rule_set_v2_2`

Frozen harness SHA256:

`b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`

Protocol SHA256:

`ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`

Prospective boundary:

`2026-09-11T20:00:00Z`

Frozen rules include:

- H1 EMA20/50 separation / ATR14 >= 0.20
- M15 signal body/range <= 0.60
- structural risk distance >= 1.25%
- structural space open OR next confirmed obstacle >= 3R
- target 3R
- max hold 32 M15 = 8h
- STOP-first same-bar semantics
- fees 5 bps/side
- base slippage 2 bps/side; stress 5 bps/side
- official Binance funding

Holdout:

`UNTOUCHED / NOT AUTHORIZED`

Do not change RR, max hold, risk gates, symbols/directions or any other frozen parameter in place.

## Prospective evidence — accepted 13:00Z state

Latest accepted cutoff:

`2026-09-13T13:00:00Z`

Run root:

`/data/research/phase11g/v2_2_shadow_20260913T130000Z`

Capture:

- `VALID_SHADOW_CAPTURE`
- panel `19/19`
- signal bars evaluated `3097`
- events `131`
- eligible observations `17`
- unique eligible families `12`
- valid snapshots `13`
- rejected snapshots `1` known infrastructure-invalid snapshot
- holdout false
- production action false

Capture hashes:

- bundle set `61b4dfe96204bef61ea04cbec4b783de476f3cb2ef57a6e1cc0643fdde4b05b5`
- bundle export summary `a1776c6c1a834d5476317ce41ff6ccadc694c425938fa644e5de417581e7210b`
- shadow summary `b80bbd4c4e886bf09eee9e0c90eae5e9d9a4935c3172b591ca13b98d1607789a`
- event file `06567e0bdc6d848bededdb5fa35f0a3e79499ff11b5cd3ce8b7bdd1fa56a2c04`
- ledger event set `dd49c4bfffe2acdd4db8227e0d1d9a39a754c1ebf66d187257d6194681b3c5e2`

Accepted outcome state:

- unique primary families `12`
- resolved primary families `12`
- unresolved `0`
- wins/losses `1 / 11`
- win rate `0.08333333333333333`
- expectancy `-0.9007780994315739R`
- evidence status `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`

Outcome hashes:

- funding summary `a86f971d935a6fa73aba60279def60f73561dd74d54d78b41e605755f0c7a272`
- promoted cache `c0ba653fc0bc12f1b4253619f0fe7b5e56949d54b24fca13e6fec6387add2284`
- observations `3e292b44d9ad2641e4e47c96c96492533167a260c7628e04ba9e228e7e6386fb`
- families `28a417ec91457291e88bedda53fc0a3e5ab21d1cc419312baa878555e5b63b17`
- summary `a4ea3745ac3b325c6c6aace8d6427a0c159c3810bac49674cfca883d25333c3d`

Three VTHO primary families that were unresolved at 12:00Z resolved as STOP by 13:00Z. Two extra VTHO rows are correlated observations only.

## Offline resolver caveat

`prospective_v2_2_outcome_resolver_offline_v1.py` has an exact-float cache-identity weakness.

Accepted handling:

- stable identity is `(setup_family_id, symbol, side, entry_time)`;
- entry/stop numeric comparison uses tight tolerance;
- terminal/exit consistency remains exact;
- no repository v1.1 resolver fix exists yet;
- 13:00Z used a temporary normalized/promoted cache followed by the unchanged offline resolver for final verification.

Do not claim a v1.1 canonical resolver exists.

## Governance thresholds

Evidence unit = unique resolved prospective `setup_family_id`, earliest eligible observation immutable primary.

- `<30` resolved families: observation only
- `30–49`: diagnostics
- `50–99`: hypotheses/ablation only
- `>=100`: versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion

Historical trades never count toward prospective thresholds.

Next prospective hard milestone:

`>=30 unique resolved prospective frozen-v2.2 families`

## Corrected historical Track B

Historical inference must use corrected causal rolling replay, not superseded unbounded-context runs.

Protocol:

`docs/research/FROZEN_V2_2_CAUSAL_ROLLING_CONTEXT_REPLAY_V1_PROTOCOL.md`

Supersession:

`docs/research/FROZEN_V2_2_HISTORICAL_EXPANSION_V1_SUPERSESSION.md`

Context per historical decision:

- M15 exactly 400 closed bars
- H1 exactly 300 closed bars

Parity:

- 19/19 symbols
- 1824 decision bars
- 70 signal cases
- 69 structural cases
- 0 mismatches
- PASS
- SHA `47b03d3c7280d8cc2c7f3f73af529fb2fa89e9ccf47c8b2132d289438396effe`

Accepted corrected results:

- P25: 214 trades, expectancy `+0.259415R`, stress `+0.224861R`
- R90: 531 trades, expectancy `+0.031637R`, stress `-0.009676R`
- R180: 1073 trades, expectancy `-0.013131R`, stress `-0.042896R`
- R365: 2099 trades on 17-symbol cohort, expectancy `-0.051000R`, stress `-0.074531R`

Interpretation:

- edge decays materially with horizon
- v2.2 is recent/regime-dependent, not long-horizon robust
- SHORT weakness is hypothesis only
- no LONG-only frozen-v2.2 modification is authorized

Accepted runtime evaluator SHA:

`c0dead4957622515a7d432d8142ac7ae8915f46e36905a5cc0e483c93e78b7e7`

## Disk-retention policy

Approved policy:

`docs/operations/DISK_RETENTION_POLICY.md`

Requirement:

- trigger at filesystem usage >=80%
- remove oldest 20% of explicitly eligible reproducible/temporary data
- protect production DB/runtime, code/config/secrets, canonical docs/checkpoints, pinned evidence, current prospective artifacts, holdout and audit manifests
- manifest-first, deterministic oldest-first, fail-closed

Automatic disk-retention mechanism is NOT installed on VM yet. Installation is deferred until after soak closure. Preferred implementation: root helper + systemd oneshot + hourly timer, initially dry-run with explicit allowlist/protected-list, then apply only after validation.

## Key canonical documents

- `docs/CURRENT_STATE.md`
- `docs/checkpoints/2026-09-14_EXTENDED_SOAK_PAUSE_START.md`
- `docs/checkpoints/2026-09-13_V2_2_PROSPECTIVE_1300Z.md`
- `docs/checkpoints/2026-09-13_V2_2_PROSPECTIVE_1300Z_OUTCOME_ADDENDUM.md`
- `docs/checkpoints/2026-09-13_V2_2_CAUSAL_ROLLING_REPLAY_ACCEPTANCE.md`
- `docs/operations/DISK_RETENTION_POLICY.md`
- `docs/research/PROSPECTIVE_FAMILY_OUTCOME_SEMANTICS_V1.md`
- `docs/research/PROSPECTIVE_V2_2_OFFLINE_RESOLVER_V1.md`

## First action in the new chat

If current time is before `2026-09-16 09:00 Europe/Kyiv`:

- do not mutate VM/research state;
- only answer status/read-only questions;
- preserve APT runtime masks.

At or after `2026-09-16 09:00 Europe/Kyiv`, on user command `статус`:

1. verify exact local time;
2. read-only check production health;
3. check container uptime/restart evidence;
4. check disk usage;
5. check APT timer/service state and package/dpkg activity;
6. inspect logs/package drift since soak start;
7. verify research branch/state;
8. only if soak passes, instruct owner to run `sudo /usr/local/sbin/ktrader-apt-freeze unfreeze`;
9. verify restored APT timers;
10. run one controlled prospective catch-up capture at a safe closed-M15 cutoff;
11. rebuild ledger and resolve new outcomes causally;
12. after soak closure, design/install disk-retention automation in dry-run-first mode.

Do not open holdout. Do not retune frozen v2.2.
