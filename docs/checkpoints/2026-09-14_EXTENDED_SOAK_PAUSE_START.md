# K-Trader — Extended Soak Pause Start

Date: 2026-09-14
Status: ACTIVE

## Window

- start: `2026-09-14 06:08 Kyiv` (`2026-09-14T03:08Z`)
- planned end: `2026-09-16 09:00 Kyiv`
- mode: extended production soak with user read-only traffic allowed

## Allowed during soak

- published K_Trader read-only analysis and data access
- production API read-only traffic
- normal runtime/data pipeline activity
- health checks and passive logging

## Forbidden during soak

- deploys or container restarts
- configuration mutations
- frozen v2.2 retuning
- holdout opening
- manual prospective captures/resolution runs
- package upgrades
- new VM automation installation, including disk-retention timer

## Start verification

- production health: `ok`, mode `read_only`
- provider: `binance_usdm`
- scanner status: `DEGRADED` (known fail-closed/history-readiness state)
- root filesystem usage: `18%`
- `apt-daily.timer`: `masked-runtime`
- `apt-daily-upgrade.timer`: `masked-runtime`
- timer next activation: none
- `apt-daily.service`: inactive
- `apt-daily-upgrade.service`: inactive
- package-management lock holders: none observed

`systemctl is-active` reports `failed` for the two runtime-masked timer units; the corresponding services are inactive and no next activation exists. This is accepted as the intended freeze state.

## End procedure

At or after `2026-09-16 09:00 Kyiv`:

1. verify production health, uptime/restarts, disk, package drift, research state and relevant logs;
2. if soak passes, run `/usr/local/sbin/ktrader-apt-freeze unfreeze`;
3. verify timers return to their normal enabled/active state;
4. run one controlled prospective catch-up capture and outcome resolution as needed;
5. only after soak closure consider installing the disk-retention automation.
