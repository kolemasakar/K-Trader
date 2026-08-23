# Phase 11F Checkpoint - Operations Hardening / Continuous Research Capture

Date: 2026-08-23

Status: VERIFIED.

## Implemented

- production runtime reuses the exact normalized instruments/tickers from the selected live universe request cycle for research capture; no second provider fetch is issued for historical rank context;
- periodic provider-coherent universe capture with a default 300-second interval;
- each capture is stored as an immutable one-snapshot `ktrader.universe_archive.v1` artifact under a provider/date directory, preserving the Phase 11E snapshot digest and avoiding repeated rewrite of one ever-growing archive file;
- configurable disk-space guard before each scanner cycle;
- low-disk state is a hard fail-closed condition that clears publishable runtime state before provider/bootstrap writes continue;
- online SQLite backup through `sqlite3.Connection.backup()`;
- `PRAGMA integrity_check` is mandatory before an atomic backup replace;
- periodic backup scheduling with configurable retention;
- standalone `scripts/backup_sqlite.py` operator utility;
- restore regression opens a produced backup as a new `CandleRepository` and verifies persisted candle state;
- scanner-age watchdog integrated into `/health` without changing the existing response shape;
- production Docker healthcheck now requires `/health` to report `status=ok`, not merely HTTP 200;
- bounded Docker json-file log rotation for K-Trader and Caddy;
- operations configuration exposed through production environment variables and the existing persistent `/data` volume.

## Default production operations values

```text
research capture interval : 300 seconds
SQLite backup interval    : 21600 seconds (6 hours)
backup retention          : 7 files
minimum free bytes        : 2147483648 (2 GiB)
minimum free percentage   : 5 percent
scanner watchdog max age  : 180 seconds
container log max size    : 10 MiB
container log files       : 5
```

The disk requirement is the maximum of the configured absolute-byte threshold and percentage threshold.

## Research capture layout

```text
/data/research/universe/<provider>/YYYY/MM/DD/
  YYYYMMDDTHHMMSSffffffZ_<snapshot-sha-prefix>.jsonl
```

Each file is independently digest-verifiable and contains exactly one Phase 11E universe snapshot. This write pattern is intentionally immutable and O(1) per capture; it does not rewrite the full historical archive on every scanner cycle.

A later dataset-catalogue phase may group these immutable captures into larger audited cohorts without changing the captured source observations.

## SQLite backup / recovery model

Production backups are created online from the live WAL database. A backup is accepted only after SQLite integrity verification succeeds. The temporary file is atomically replaced into its final name only after that verification.

The runtime does not automatically overwrite the live database from a backup. Recovery remains an explicit operator action after stopping the service. Tests validate recoverability by opening a generated backup as a fresh repository and checking persisted data.

## Operational safety behavior

Disk guard failure occurs before provider selection/bootstrap for the cycle. The scanner publishes an ERROR state with `data_ready=false` and no stale market/decision state is retained as current publishable data.

Research-capture or backup errors that occur after a successful preflight do not fabricate analysis; they are recorded as operations warnings and make the successful scanner cycle DEGRADED rather than silently hiding the maintenance failure.

## Watchdog behavior

The public `/health` JSON schema is unchanged. When the runtime app configures a scanner-age threshold, health is `degraded` if the last completed scan is older than that threshold. Docker healthcheck parses the JSON body and succeeds only when `status` equals `ok`.

## Verification evidence

PR #9 (`Phase 11F operations hardening`) GitHub Actions CI run:

`32656033224`

Integrated result:

- Python compile: PASS;
- shell syntax validation: PASS;
- repository-wide pytest: **155 passed, 1 dependency deprecation warning**;
- Docker Compose validation: PASS;
- linux/amd64 Docker build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production ASGI import: PASS;
- packaged target-host acceptance utility on both architectures: PASS.

PR #9 was squash-merged to `main` as:

`ae3620f7ce4bb6b857098ba470a5f2ddbfe374d5`

## Trading / research guardrails

Phase 11F does not change Trading Engine setup discovery, RR, ATR-used, VSA/Trap, scoring, grading or signal eligibility. Setup Score remains non-probabilistic and `estimated_probability` remains null/N/A.

## Remaining live work

Repository-side operations hardening is verified, but target-host evidence still requires the Oracle A1 production VM:

- real persistence across container/host restart;
- real scheduled backup generation on the persistent volume;
- real disk-guard/watchdog behavior under target-host conditions;
- continuous prospective universe capture from public provider APIs;
- live REST/WebSocket/scanner acceptance and HTTPS activation.
