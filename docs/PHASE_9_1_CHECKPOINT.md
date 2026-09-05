# Phase 9.1 Checkpoint - Oracle ARM64 / Multi-arch

Date: 2026-09-05

Status: VERIFIED / ORACLE ARM64 PRODUCTION HOST ACTIVE.

## Scope

Phase 9.1 adapts the repository-side deployment baseline for Oracle Cloud Always Free Ampere A1 while retaining amd64 compatibility, and now includes verified live production operation on the Oracle ARM64 target.

## Implemented

- primary production deployment runner target changed to ARM64 via custom label `k-trader-prod-arm64`;
- deploy workflow verifies the production host reports `aarch64` or `arm64`;
- GitHub Actions Runner registration auto-detects Linux x64 vs arm64;
- official Runner `2.336.0` SHA-256 is pinned for both architectures;
- Ubuntu provisioning accepts `arm64` and `amd64` and configures the matching Docker repository architecture;
- CI split into native `docker-amd64` and emulated `docker-arm64` image gates;
- ARM64 CI uses QEMU + Buildx, verifies the image reports `arm64`, imports the production ASGI application, and checks that the target-host acceptance utility is packaged;
- Oracle A1 provisioning documentation added/updated;
- production runtime UID/GID is derived from the host runner user and injected into the image build;
- persistent bind-mounted data ownership is verified before deployment;
- amd64 compatibility remains available as a fallback architecture.

## Repository verification evidence

Initial Phase 9.1 verification:

- PR #3 CI run `32646869264`: SUCCESS;
- repository-wide pytest: **92 passed**;
- Docker Compose validation: PASS;
- linux/amd64 production image build/runtime import: PASS;
- linux/arm64 QEMU/Buildx build: PASS;
- ARM64 architecture assertion: PASS;
- ARM64 production runtime import: PASS;
- PR #3 squash merge: `8e7ef38311e8c92398eb7cf530c92ff773e2a9a1`.

Latest production hardening verification:

- PR #17 final CI: **170 tests PASS**;
- docker-amd64: PASS;
- docker-arm64: PASS;
- merge to `main`: `9ed572349ed0195e518f128894a1f187419dbcc1`.

## Runner checksums

GitHub Actions Runner `2.336.0` registration package checksums remain:

```text
linux-x64:
04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d

linux-arm64:
58b758e420b87093fbd4bfddd368074960053e2f1388f01848c82624b90f27d1
```

The registered runner auto-updated and reported version `2.337.0` during the successful production workflow.

## Oracle production state

Verified production VM:

```text
Name: k-trader-prod
Region: Germany Central (Frankfurt)
Image: Canonical Ubuntu 24.04 Minimal aarch64
Shape: VM.Standard.A1.Flex
OCPU: 1
Memory: 6 GB
Public IPv4: 92.5.56.198
```

Historical note: on 2026-08-23 A1 creation was blocked by external capacity in Frankfurt AD-1, AD-2 and AD-3, including a reduced 1 OCPU / 6 GB request. Capacity later became available and the production VM was created successfully.

No paid shape was required.

## Production runner

The repository-scoped ARM64 runner is registered as a system service under user `ktrader`.

```text
Runner name: k-trader-prod-vnic-k-trader
Labels: k-trader-prod, k-trader-prod-arm64
```

## Live production acceptance

GitHub Actions run `33920829993` completed with `success`.

Verified:

- approved `main` SHA `9ed572349ed0195e518f128894a1f187419dbcc1`;
- native ARM64 build;
- runtime UID/GID `1002:1002` matching host `ktrader`;
- writable `/opt/k-trader/data` persistent tree;
- Binance USD-M REST acceptance on `5m,15m,1h,4h,1d`;
- public WebSocket `5m` acceptance;
- scanner `data_ready=true`;
- final deployment-cycle scanner state `DEGRADED`, 13 ready / 7 failed;
- MTF API publication on all five canonical intervals;
- Docker `healthy`;
- local `/health` returns `status=ok`, `mode=read_only`, `data_ready=true`.

## Phase 9.1 exit

Phase 9.1 is complete.

Remaining public DNS/TLS and Custom GPT Action activation belong to Phase 10 and are intentionally not part of this checkpoint.
