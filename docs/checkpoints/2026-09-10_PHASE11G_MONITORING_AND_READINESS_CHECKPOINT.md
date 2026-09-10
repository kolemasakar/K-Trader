# Phase 11G - Monitoring and Readiness Checkpoint

Date: 2026-09-10

Status: **CONTINUOUS PROVIDER-RECORDED DISCOVERY ACTIVE / FAST M5 TTL60 PRODUCTION / FIRST NATURAL TRADABLE SIGNAL NOT YET OBSERVED / PARALLEL READINESS WORK ACTIVE**

## Purpose

Record the accepted project boundary after the horizon time-split study and before the next approximately 24-hour manual prospective-discovery review. This checkpoint does not change Trading Engine rules, runtime configuration, provider selection, catalogue eligibility, RR, ATR, setup lifecycle, structural-target semantics or probability policy.

## Canonical repository identity

- repository: `kolemasakar/K-Trader`;
- default branch: `main`;
- canonical main SHA: `1e6e20fb5d0e74aaf620f3aebf69429e0c0f3198`;
- commit: `Phase 11G: validate horizon profiles on time-split data (#43)`;
- GitHub commit verification: `verified=true`, reason `valid`;
- PR #43 was docs/research-only and therefore did not require a production redeploy.

## Production identity

Accepted production runtime remains:

- deployed SHA/image baseline: `9a257957e033f6265b9e746cb9f15e755ff87b72`;
- provider: `binance_usdm`;
- FAST profile: setup interval `5m`, `setup_max_age_bars=12`, TTL `60m`;
- public `/health` at the checkpoint: `status=ok`, `data_ready=true`, scanner status reported `DEGRADED`;
- production remains read-only;
- no direct source mutation on PROD is permitted.

The `DEGRADED` scanner status is not treated as evidence of database corruption. Earlier direct audits showed transient `missing bars: 1` readiness errors while persisted M5 sequences subsequently became contiguous. Persistent bootstrap failures are separately attributable to insufficient D1 history on young contracts and remain fail-closed.

## Continuous research capture

At the checkpoint inspection:

- date partition: `/data/research/universe/binance_usdm/2026/09/10/`;
- captured files observed for the UTC day: `37`;
- latest observed capture: `20260910T030035463646Z_4f4c1ee74537.jsonl`;
- latest capture time: `2026-09-10T03:00:35.463646Z`;
- universe size: `50` ranked Binance USD-M perpetual instruments;
- capture accumulation remains active and is not affected by disabling the ChatGPT scheduled signal-watch task.

## Runtime data integrity

Direct read-only checks at the checkpoint:

- SQLite database: `/data/ktrader.db`;
- `PRAGMA integrity_check`: `ok`;
- observed database size: `28,422,144` bytes;
- completed `.db` backups observed: `7`;
- latest completed backup observed: `/data/backups/ktrader_20260909T230747121442Z.db`.

No database mutation was performed by this checkpoint.

## Dataset catalogue state

Canonical materialized catalogue remains:

- schema: `ktrader.dataset_catalogue.v1`;
- entries: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- canonical loader with `verify_artifacts=True`: `PASS`.

Observed catalogue file SHA-256 remains:

`d1b1c42b51a2f54c865d03e21bae3faa2a0e58166baa46c7a01a241b47eed250`

This differs from an earlier recorded catalogue SHA. Because full loader/artifact verification passes, the drift is an unresolved provenance question, not evidence of corruption. Root-cause closure is explicitly included in the parallel readiness work.

## Current top-20 bootstrap eligibility observation

The latest captured top-20 universe included:

`IOSTUSDT, XRPUSDT, DOGEUSDT, USELESSUSDT, NEARUSDT, 牛来USDT, PUMPUSDT, SUIUSDT, 1000PEPEUSDT, ENAUSDT, WLDUSDT, ARBUSDT, PONSUSDT, RAYSOLUSDT, KATUSDT, ADAUSDT, MARSCOINUSDT, TRUMPUSDT, DOTUSDT, SOPHUSDT`.

Latest bootstrap state was successful for the mature-history members except the following fail-closed young contracts:

- `牛来USDT`: insufficient D1 history, observed `11/250`;
- `PONSUSDT`: insufficient D1 history, observed `4/250`;
- `KATUSDT`: insufficient D1 history, observed `192/250`;
- `MARSCOINUSDT`: insufficient D1 history, observed `9/250`.

These failures do not justify reducing the canonical D1 history requirement.

## Signal monitoring decision

The temporary ChatGPT condition-watch task for the first natural K-Trader tradable signal was disabled by operator decision.

Operational policy now is:

- continue provider-recorded production capture continuously;
- do not run an automated ChatGPT signal check each hour;
- perform the next signal/discovery control manually after approximately 24 hours;
- preserve unchanged hard gates throughout the accumulation interval.

The last checked live prospective state before disabling automated monitoring contained zero tradable LONG/SHORT signals. No new Phase 11G chain was materialized.

## Trading-horizon state

Unchanged:

- FAST / M5 / 60m: **production validated**;
- INTRADAY / M15: **research only, universal TTL unresolved**;
- MEDIUM / H1 / 8-12h: **research-only lifecycle design band, time-split validated**;
- no non-FAST profitability optimum is claimed.

## Parallel work approved while waiting for natural signal evidence

The following work can proceed without waiting for the first tradable signal:

1. operational integrity audit: capture continuity, database/WAL, backups, disk and scanner-cycle behavior;
2. scanner `DEGRADED` / M5 reconciliation audit and fail-closed validation;
3. catalogue integrity and catalogue-SHA drift root-cause audit;
4. deterministic prospective discovery-report design so a manual 24-hour review yields a full rejection funnel instead of only `signals=0`;
5. outcome-pipeline readiness validation using existing deterministic contracts/tests without fabricating a real outcome;
6. documentation/provenance hardening for the above results.

Work that remains blocked on natural evidence:

- materializing/registering a new catalogue chain;
- exporting a real immutable WIN/LOSS outcome sample for a new signal;
- profitability calibration or probability estimation;
- Phase 12 multi-provider activation.

## Invariants

No parallel-readiness task may:

- lower `RR >= 3`;
- relax `ATR_USED_OVER_80`;
- widen context freshness;
- synthesize structural targets;
- refresh stale setup confirmation time;
- weaken minimum MTF history;
- fabricate ranks, outcomes or probabilities;
- materialize a chain that has not naturally survived all hard gates.

## Next execution sequence

Proceed immediately with read-only/non-signal-dependent work in this order:

`Operational integrity -> scanner reconciliation -> catalogue SHA root cause -> deterministic daily discovery report -> outcome-pipeline readiness -> control checkpoint`.

The next approximately 24-hour prospective signal review remains manual.