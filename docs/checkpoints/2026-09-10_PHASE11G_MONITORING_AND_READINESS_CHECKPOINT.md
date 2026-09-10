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

Cross-day continuity audit over `2026-09-09T00:00:46Z` through `2026-09-10T03:00:35Z` found:

- captures: `327`;
- median interval: approximately `300.005s`;
- maximum observed interval: approximately `301.608s`;
- gaps greater than `420s`: `0`.

Capture continuity is therefore accepted for this interval.

## Runtime data integrity

Direct read-only checks at the checkpoint:

- SQLite database: `/data/ktrader.db`;
- `PRAGMA integrity_check`: `ok`;
- observed database size: `28,422,144` bytes;
- WAL size observed: `5,454,912` bytes;
- completed `.db` backups observed: `7`;
- latest completed backup observed: `/data/backups/ktrader_20260909T230747121442Z.db`;
- root filesystem: `45G` total, approximately `6.6G` used, `38G` available (`15%` used).

No database mutation was performed by this checkpoint.

## Dataset catalogue state

Canonical materialized catalogue remains:

- schema: `ktrader.dataset_catalogue.v1`;
- entries: `2`;
- symbols: `SUIUSDT`, `XRPUSDT`;
- canonical loader with `verify_artifacts=True`: `PASS`.

Two different SHA-256 values were previously compared as though they represented the same identity. The audit resolved that distinction:

- canonical semantic catalogue digest stored in `catalogue_sha256`: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- raw SHA-256 of the serialized `catalogue.json` file: `d1b1c42b51a2f54c865d03e21bae3faa2a0e58166baa46c7a01a241b47eed250`.

This difference is **by design, not drift**. `catalogue_sha256` is calculated over the canonical payload `{schema_version, entries}`. The serialized file additionally contains the `catalogue_sha256` field itself, so its raw file-content SHA is a separate content identity and is not expected to equal the semantic catalogue digest.

The earlier corruption concern is closed. Full loader/artifact verification remains PASS.

## Current top-20 bootstrap eligibility observation

The latest captured top-20 universe included:

`IOSTUSDT, XRPUSDT, DOGEUSDT, USELESSUSDT, NEARUSDT, 牛来USDT, PUMPUSDT, SUIUSDT, 1000PEPEUSDT, ENAUSDT, WLDUSDT, ARBUSDT, PONSUSDT, RAYSOLUSDT, KATUSDT, ADAUSDT, MARSCOINUSDT, TRUMPUSDT, DOTUSDT, SOPHUSDT`.

Latest bootstrap state was successful for the mature-history members except the following fail-closed young contracts:

- `牛来USDT`: insufficient D1 history, observed `11/250`;
- `PONSUSDT`: insufficient D1 history, observed `4/250`;
- `KATUSDT`: insufficient D1 history, observed `192/250`;
- `MARSCOINUSDT`: insufficient D1 history, observed `9/250`.

These failures do not justify reducing the canonical D1 history requirement.

A 24-hour bootstrap telemetry audit found that the failure volume is an operational retry issue rather than broad provider/data failure:

- approximately `5,081` bootstrap-run records in the inspected rolling interval;
- approximately `4,907` failures;
- all inspected failures were `BootstrapError: Insufficient closed 1d bars`;
- failing symbols were only `MARSCOINUSDT`, `PONSUSDT`, `牛来USDT`, and `KATUSDT`;
- mature-history symbols continued to produce successful bootstrap results.

The current runtime retries known history-incomplete contracts too frequently. This is operational inefficiency/noise; eligibility remains correctly fail-closed. A retry/backoff hardening change may be implemented only if it preserves all history requirements and does not convert an ineligible symbol into READY.

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
2. scanner `DEGRADED` / M5 reconciliation and known-insufficient-history retry audit;
3. catalogue integrity and catalogue-SHA identity audit;
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

`Operational integrity -> scanner retry/reconciliation hardening -> deterministic daily discovery report -> outcome-pipeline readiness -> control checkpoint`.

The catalogue SHA identity question is closed. The next approximately 24-hour prospective signal review remains manual.