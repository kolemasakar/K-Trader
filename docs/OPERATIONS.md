# Operations Specification v1.0

## Service expectations

- Scanner runs continuously.
- Provider health and last-data timestamps are observable.
- WebSocket reconnects are automatic.
- REST reconciliation detects/repairs confirmed gaps by refetching provider-native bars.
- Stale or incomplete state fails closed to NO TRADE.

## Required operational status

Expose/record:
- service uptime
- active provider
- provider health
- last REST success
- last WS message
- last closed 5m bar
- last reconciliation
- active universe size
- candidate/signal counts
- database health
- engine version

## Restart/recovery

On restart:
1. Load configuration.
2. Validate database/migrations.
3. Discover provider instruments.
4. REST-bootstrap required history.
5. Validate continuity/freshness.
6. Start live streams.
7. Enable signal evaluation only after data readiness passes.

## Logging

Use structured logs with timestamps, component, provider, symbol where relevant, severity and reason codes.

## Backups

SQLite database and configuration SHALL have a documented backup/restore procedure before production hardening is complete.
