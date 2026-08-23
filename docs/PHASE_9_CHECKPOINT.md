# Phase 9 Checkpoint

Date: 2026-08-23

Status: REPOSITORY-SIDE COMPLETE THROUGH PHASE 9.1 / ORACLE A1 DEPLOYMENT AND LIVE ACCEPTANCE PENDING.

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

## Production-prep gate

PR #2 validated the deployment/provisioning additions with CI run `32637233264`.

Result:

- repository-wide pytest: PASS;
- compile source/tests/scripts: PASS;
- Docker Compose validation: PASS;
- Docker image build: PASS;
- production runtime import: PASS;
- packaged target-host acceptance utility: PASS.

PR #2 was squash-merged as:

`377b4b412afcb85ccb8fa6a0b567482119c21349`.

## Phase 9.1 Oracle ARM64 adaptation

Primary production hosting is now Oracle Cloud Always Free Ampere A1 in Germany Central (Frankfurt).

Repository changes:

- production workflow targets custom runner label `k-trader-prod-arm64`;
- runner installer supports both Linux arm64 and x64;
- GitHub Actions Runner `2.336.0` official SHA-256 is pinned per architecture;
- Ubuntu provisioning supports `arm64` and `amd64`;
- CI contains separate amd64 and arm64 Docker gates;
- ARM64 image is built under QEMU/Buildx, architecture-checked, runtime-imported, and checked for the packaged acceptance utility;
- amd64 support is retained as a future fallback host path.

Phase 9.1 PR CI must pass before this subsection is marked VERIFIED.

## Runner baseline

GitHub Actions Runner: `2.336.0`.

```text
linux-x64 SHA-256:
04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d

linux-arm64 SHA-256:
58b758e420b87093fbd4bfddd368074960053e2f1388f01848c82624b90f27d1
```

Custom labels:

```text
k-trader-prod
k-trader-prod-arm64   # primary Oracle production runner
k-trader-prod-x64     # retained fallback architecture
```

## Oracle external infrastructure status

OCI Free Tier account and Germany Central (Frankfurt) home region are prepared.

Target VM:

```text
Canonical Ubuntu 24.04 Minimal aarch64
VM.Standard.A1.Flex
2 OCPU / 12 GB RAM
```

On 2026-08-23, OCI returned `Out of capacity` for A1 in AD-1, AD-2, and AD-3. A reduced 1 OCPU / 6 GB request was also unavailable in all three ADs.

No paid shape is approved as a workaround. Retry the A1 request when capacity becomes available.

## Still pending external infrastructure

The following cannot be claimed before the real Oracle A1 host is available:

- Ubuntu ARM64 host provisioning result;
- registered/online `k-trader-prod-arm64` self-hosted runner;
- DNS/HTTPS reachability;
- Binance/Bybit public REST reachability from Oracle;
- public WebSocket reachability from Oracle;
- full scanner `data_ready` result on Oracle;
- persistent SQLite/WAL behavior across a real container restart;
- public TLS endpoint acceptance.

## Hosting decisions

- Primary: Oracle Cloud Always Free Ampere A1.
- Potential fallback only, not implemented: home Windows PC + Tailscale Funnel.
- Cloudflare Workers + Durable Objects: not planned for K-Trader v1; retain only as a future-project architecture idea.

## Phase 9 exit

Phase 9 is not fully complete until Oracle target-host live acceptance passes.
