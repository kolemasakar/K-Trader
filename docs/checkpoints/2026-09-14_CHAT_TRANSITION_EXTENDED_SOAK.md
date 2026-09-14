# K-Trader — Chat Transition During Extended Soak

Date: 2026-09-14
Status: ACCEPTED / READY FOR NEW CHAT

## Active operational boundary

Extended production soak is active:

- start `2026-09-14 06:08 Europe/Kyiv`
- planned end `2026-09-16 09:00 Europe/Kyiv`
- published K_Trader read-only traffic is allowed
- VM/research state mutation is forbidden until soak-end verification

APT timers are runtime-masked; APT services are inactive. Production health at soak start was `ok`, mode `read_only`; disk usage was `18%`.

## Frozen research state

- strategy `candidate_rule_set_v2_2`
- frozen harness SHA256 `b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08`
- protocol SHA256 `ba671cbed71fdc79380f37a72b75f93e75aa3ee895f5385ef433f497165de5a3`
- prospective boundary `2026-09-11T20:00:00Z`
- holdout `UNTOUCHED / NOT AUTHORIZED`
- latest accepted prospective cutoff `2026-09-13T13:00:00Z`
- 12 unique primary families / 12 resolved / 0 unresolved
- 1 win / 11 losses
- expectancy `-0.9007780994315739R`
- evidence status `OBSERVATION_ONLY_LT_30_RESOLVED_FAMILIES`

No retuning is authorized.

## Historical state

Corrected causal rolling replay is authoritative for historical inference:

- M15 400 closed bars
- H1 300 closed bars
- prospective parity 0 mismatches
- P25 expectancy `+0.259415R`
- R90 `+0.031637R`
- R180 `-0.013131R`
- R365 `-0.051000R`

Earlier unbounded-context historical results remain superseded for inference.

## Disk policy

Approved disk retention policy is canonical at:

`docs/operations/DISK_RETENTION_POLICY.md`

Automatic VM retention is not installed yet and must remain deferred until soak closure.

## Documentation synchronization

Synchronized during transition preparation:

- `docs/CURRENT_STATE.md` — commit `0d2edb0e9ce2b2a047267504d18237e8dc546b8c`
- `docs/handoffs/BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md` — commit `6372a1a6ea1c68a2350f2b7ac2e2e9c16045b132`
- `docs/checkpoints/README.md` — commit `28acfba487e8a54463b348e66f28bd2663392cd2`

Before this checkpoint, research branch ancestry verification showed:

- canonical main baseline `4919fea4397d34898ddc7d4215ea898e6caea815`
- research branch status `ahead`
- ahead by `133`
- behind by `0`
- merge base exactly canonical main
- no rebase / no force update

## New-chat recovery

Use:

`віднови <<File name="BOOTSTRAP_PACKAGE_2026-09-14_K_TRADER_EXTENDED_SOAK_HANDOFF.md">>`

If current time is before soak end, do not mutate project/VM state.

At or after `2026-09-16 09:00 Europe/Kyiv`, the first user command should be `статус`. Perform read-only soak-end audit before any unfreeze or research action. If soak passes, unfreeze APT, verify timer restoration, then run one controlled prospective catch-up cycle and causal outcome resolution. Disk-retention automation is considered only after soak closure.
