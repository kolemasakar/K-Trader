# Phase 9 Checkpoint

Date: 2026-08-23

Status: CI/DOCKER/DEPLOYMENT AUTOMATION COMPLETE / TARGET-VPS DEPLOYMENT AND LIVE ACCEPTANCE PENDING.

## Repository-wide CI evidence

A control pull request was used because the available connector exposes PR-triggered workflow runs directly.

Initial real CI run found two invalid synthetic fixtures. Production candle validation was not weakened; the fixtures were corrected.

A later Docker gate found a real FastAPI lifecycle compatibility issue. Runtime startup/shutdown was migrated from removed event-handler methods to the ASGI lifespan contract.

Final CI run `32636825758` completed successfully:

- Python compile: PASS;
- repository-wide pytest: **92 passed**;
- one dependency deprecation warning remains in FastAPI/Starlette TestClient usage;
- Docker Compose validation: PASS;
- Docker image build: PASS;
- production runtime import from built image: PASS.

The fixes were squash-merged to main as commit:

`8ce912903224f6968479650eb0c3f4870bea6269`.

## Production preparation

Implemented:

- GitHub-hosted CI separated from production self-hosted runner;
- manual-only production deployment workflow;
- hardened non-root Docker image;
- read-only Compose root filesystem and loopback API bind;
- optional Caddy HTTPS profile;
- immutable commit-SHA deployment releases;
- rollback on process or live acceptance failure;
- target-VPS public REST/WebSocket acceptance utility;
- scanner/API readiness acceptance;
- Ubuntu/Docker provisioning script;
- checksum-verified repository runner registration script;
- canonical VPS provisioning/security documentation.

## Runner baseline

- GitHub Actions Runner: `2.336.0` Linux x64.
- SHA-256: `04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d`.
- custom label: `k-trader-prod`.

## Still pending external infrastructure

The following cannot be claimed before a real VPS is supplied/provisioned:

- Ubuntu host provisioning result;
- registered/online self-hosted runner;
- VPS DNS/HTTPS reachability;
- Binance/Bybit public REST reachability from the VPS;
- public WebSocket reachability from the VPS;
- full scanner `data_ready` result on the VPS;
- persistent SQLite/WAL behavior across a real container restart;
- public TLS endpoint acceptance.

## Phase 9 exit

Phase 9 is not fully complete until target-VPS live acceptance passes.

Repository-side preparation is complete subject to the final production-prep CI pull request.
