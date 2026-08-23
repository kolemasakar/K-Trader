# Phase 9 Checkpoint

Date: 2026-08-23

Status: REPOSITORY-SIDE COMPLETE / TARGET-VPS DEPLOYMENT AND LIVE ACCEPTANCE PENDING.

## Repository-wide CI evidence

A control pull request was used because the available connector exposes PR-triggered workflow runs directly.

Initial real CI found two invalid synthetic fixtures. Production candle validation was not weakened; only the fixtures were corrected.

A later Docker gate found a real FastAPI lifecycle compatibility issue. Runtime startup/shutdown was migrated to the ASGI lifespan contract.

Successful CI run `32636825758` proved the repaired complete repository:

- Python compile: PASS;
- repository-wide pytest: **92 passed**;
- one dependency deprecation warning remains in FastAPI/Starlette TestClient usage;
- Docker Compose validation: PASS;
- Docker image build: PASS;
- production runtime import from built image: PASS.

Those fixes were squash-merged as:

`8ce912903224f6968479650eb0c3f4870bea6269`.

## Final production-prep gate

PR #2 validated the deployment/provisioning additions with CI run `32637233264`.

Result:

- repository-wide pytest: PASS;
- compile source/tests/scripts: PASS;
- Docker Compose validation: PASS;
- Docker image build: PASS;
- production runtime import: PASS;
- packaged VPS acceptance utility: PASS.

PR #2 was squash-merged as:

`377b4b412afcb85ccb8fa6a0b567482119c21349`.

## Production preparation implemented

- GitHub-hosted CI separated from production self-hosted runner;
- current Node-24 GitHub Action major versions in CI/deploy workflows;
- manual-only production deployment workflow on `main`;
- hardened non-root Docker image;
- read-only Compose root filesystem and loopback API bind;
- optional Caddy HTTPS profile;
- immutable commit-SHA deployment releases;
- rollback on process or live acceptance failure;
- target-VPS public REST checks on all five canonical timeframes;
- target-VPS public 5m WebSocket acceptance;
- scanner `data_ready` and MTF API acceptance;
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

All work that can be completed solely inside the repository is complete and CI-validated.
