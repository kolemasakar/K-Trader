# Phase 9.1 Checkpoint - Oracle ARM64 / Multi-arch

Date: 2026-08-23

Status: VERIFIED / ORACLE LIVE DEPLOYMENT PENDING EXTERNAL A1 CAPACITY.

## Scope

Phase 9.1 adapts the repository-side deployment baseline for Oracle Cloud Always Free Ampere A1 while retaining amd64 compatibility.

## Implemented

- primary production deployment runner target changed to ARM64 via custom label `k-trader-prod-arm64`;
- deploy workflow verifies the production host reports `aarch64` or `arm64`;
- GitHub Actions Runner registration auto-detects Linux x64 vs arm64;
- official Runner `2.336.0` SHA-256 is pinned for both architectures;
- Ubuntu provisioning accepts `arm64` and `amd64` and configures the matching Docker repository architecture;
- CI split into native `docker-amd64` and emulated `docker-arm64` image gates;
- ARM64 CI uses QEMU + Buildx, verifies the image reports `arm64`, imports the production ASGI application, and checks that the target-host acceptance utility is packaged;
- Oracle A1 provisioning documentation added/updated;
- hosting decision record added: Oracle primary; home PC + Tailscale Funnel potential fallback only; Cloudflare edge/serverless deferred to future projects.

## Verification evidence

PR #3 (`Phase 9.1 Oracle ARM64 and multi-arch CI`) passed GitHub Actions CI run:

`32646869264`

Result:

- Python compile: PASS;
- shell script syntax validation: PASS;
- repository-wide pytest: **92 passed, 1 dependency deprecation warning**;
- Docker Compose validation: PASS;
- linux/amd64 production image build: PASS;
- amd64 production ASGI import: PASS;
- amd64 packaged acceptance utility: PASS;
- QEMU/Buildx ARM64 environment: PASS;
- linux/arm64 production image build/load: PASS;
- image architecture assertion `arm64`: PASS;
- ARM64 production ASGI import under QEMU: PASS;
- ARM64 packaged acceptance utility: PASS.

PR #3 was squash-merged to `main` as:

`8e7ef38311e8c92398eb7cf530c92ff773e2a9a1`

## Runner checksums

GitHub Actions Runner `2.336.0`:

```text
linux-x64:
04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d

linux-arm64:
58b758e420b87093fbd4bfddd368074960053e2f1388f01848c82624b90f27d1
```

## Oracle external status

OCI account/home region preparation is complete for Germany Central (Frankfurt).

Target VM:

```text
Canonical Ubuntu 24.04 Minimal aarch64
VM.Standard.A1.Flex
2 OCPU / 12 GB RAM
```

On 2026-08-23, A1 creation was blocked by external host capacity in AD-1, AD-2, and AD-3. A reduced 1 OCPU / 6 GB A1 request was also unavailable in all three ADs.

No paid shape is approved as a workaround.

## Remaining Phase 9 live gate

Real Oracle VM deployment/live provider acceptance remains pending only because OCI A1 capacity is unavailable.

After capacity becomes available:

1. create the Oracle A1 host;
2. assign/verify public IPv4 and SSH access;
3. run Ubuntu/Docker provisioning;
4. register the ARM64 production runner;
5. execute `Deploy Production`;
6. pass REST/WS/scanner/MTF acceptance;
7. verify persistent SQLite across restart;
8. configure DNS/TLS and pass public HTTPS acceptance.
