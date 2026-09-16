# Research Storage Growth — 2026-09-16

Status: **READ-ONLY PLANNING SNAPSHOT**

## Current state

Verified filesystem:

- capacity: `47,321,268,224` bytes;
- used: `9,038,782,464` bytes;
- utilization: approximately `19.1%` by byte calculation (`df` rounded display: 20%);
- inode use: approximately `5%`;
- `/data/research` total: approximately `1.446 GB`.

The research tree is bursty: large one-off research/export days coexist with a much smaller steady universe-snapshot stream. Therefore a single linear growth forecast would be misleading.

## Planning scenarios

Additional data required to reach 70% filesystem use: approximately `24.09 GB`.

Additional data required to reach 80% filesystem use: approximately `28.82 GB`.

Scenario time to 70%:

| Sustained net growth | Approx. days |
|---:|---:|
| 10 MiB/day | 2297 |
| 50 MiB/day | 459 |
| 100 MiB/day | 230 |
| 250 MiB/day | 92 |
| 500 MiB/day | 46 |

Scenario time to 80%:

| Sustained net growth | Approx. days |
|---:|---:|
| 10 MiB/day | 2748 |
| 50 MiB/day | 550 |
| 100 MiB/day | 275 |
| 250 MiB/day | 110 |
| 500 MiB/day | 55 |

## Operational decision

`ktrader-disk-retention.timer` remains **disabled by design**.

No destructive retention mode is authorized.

Recommended review points remain:

- around `70%`: review actual sustained growth and eligible-data inventory;
- at `>=80%`: execute the accepted retention planning policy, still fail-closed and manifest-first.

The 70% level is a review/warning point only; it does not trigger deletion.

Canonical diagnostic implementation:

`ops/research_storage/research_storage_growth_diagnostics.py`

Runtime report SHA256 at this snapshot:

`4cbdbd2a61c556073a0afa09453f8d51e2d30a9119312fd1141f81fc54c9e3f8`
