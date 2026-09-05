# Phase 9 Checkpoint

Date: 2026-09-05

Status: COMPLETE / ORACLE ARM64 PRODUCTION DEPLOYMENT AND LIVE ACCEPTANCE VERIFIED.

## Repository and CI baseline

Phase 9 repository preparation, Oracle ARM64 adaptation, runtime hardening and the production UID/health correction have passed repository-wide CI.

Latest production-fix evidence before deployment:

- PR #17: `K-Trader: align production runtime UID and health readiness`;
- final PR head: `8e68bbfd89dd5f9922b8975af241c16b378102fa`;
- pytest: **170 passed**;
- Docker amd64: PASS;
- Docker arm64: PASS;
- merge to `main`: `9ed572349ed0195e518f128894a1f187419dbcc1`.

Earlier Phase 9/9.1 repository verification remains valid, including CI runs `32636825758`, `32637233264`, and `32646869264`.

## Production host

Verified Oracle Cloud production VM:

```text
Name: k-trader-prod
Region: Germany Central (Frankfurt)
Image: Canonical Ubuntu 24.04 Minimal aarch64
Shape: VM.Standard.A1.Flex
OCPU: 1
Memory: 6 GB
Public IPv4: 92.5.56.198
Architecture: aarch64
```

The production host is isolated from the separate K-Geopolitical Monitor VM.

## GitHub Actions runner

Repository-scoped self-hosted runner is registered and active as a system service under user `ktrader`.

```text
Runner name: k-trader-prod-vnic-k-trader
Labels: k-trader-prod, k-trader-prod-arm64
Runner version observed during production deploy: 2.337.0
```

Production deployment workflow remains manual-only and targets approved `main` on the ARM64 runner.

## Runtime identity incident and correction

The first production attempt exposed a real bind-mount ownership defect:

- host `/opt/k-trader/data` owner was UID/GID `1002:1002`;
- the original image user was UID/GID `999:999`;
- SQLite failed with `sqlite3.OperationalError: unable to open database file`.

A temporary ownership change proved the root cause. PR #17 then replaced the fragile fixed-image identity assumption with dynamic production identity alignment:

- deployment derives runtime UID/GID from the self-hosted runner user;
- Docker build creates the non-root `ktrader` user with that identity;
- deployment fails closed if `/opt/k-trader/data` is not writable;
- production host ownership is restored to `ktrader:ktrader`.

Final verified state:

```text
container uid:gid = 1002:1002
/opt/k-trader/data owner = ktrader:ktrader
/opt/k-trader/data mode = 750
```

The numeric ID is host-specific and is not a hard-coded production contract.

## Health-semantics correction

Live Phase 9 acceptance also exposed a second mismatch:

- scanner can validly be `DEGRADED` when some symbols fail independently;
- `data_ready=true` can still be true with coherent usable canonical data;
- the old container health rule incorrectly treated any degraded scanner result as container failure.

PR #17 aligned Docker health with runtime readiness while preserving the existing public `/health` response shape. Stale/incomplete runtime still fails health; partial symbol failures do not take the whole service offline when data remains ready and fresh.

## Successful production deployment

GitHub Actions run:

```text
33920829993 -> SUCCESS
```

Deployed release:

```text
9ed572349ed0195e518f128894a1f187419dbcc1
```

Deployment evidence:

- approved `main` checkout: PASS;
- Oracle production architecture check: PASS;
- image built natively for ARM64 with runtime UID/GID `1002:1002`;
- container start: PASS;
- Binance USD-M REST acceptance on `5m,15m,1h,4h,1d`: PASS;
- Binance USD-M public WebSocket `5m`: PASS;
- scanner `data_ready=true`: PASS;
- final deployment-cycle scanner state: `DEGRADED`, 13 symbols ready / 7 failed;
- MTF API publication on `5m,15m,1h,4h,1d`: PASS;
- Docker container: `healthy`;
- release promotion: PASS.

## Final operator verification

Verified after workflow success:

```text
DEPLOYED_SHA:
9ed572349ed0195e518f128894a1f187419dbcc1

HEALTH:
status=ok
mode=read_only
data_ready=true
scanner_status=DEGRADED
provider_id=binance_usdm
action_auth_enabled=false

CONTAINER:
healthy

UID:
uid=1002(ktrader) gid=1002(ktrader)

DATA_DIR:
1002:1002 ktrader:ktrader 750 /opt/k-trader/data
```

`action_auth_enabled=false` is expected because Phase 10 public HTTPS/Action activation has not started yet.

## Persistence state

Persistent runtime state exists under `/opt/k-trader/data`, including:

- `ktrader.db`;
- SQLite WAL/SHM files while active;
- `backups/`;
- `research/`.

The production runtime can create/open SQLite state with the final non-root identity. Continuous capture and backup evidence can now accumulate prospectively.

## Phase 9 exit

Phase 9 exit criteria are satisfied for localhost production:

- Oracle ARM64 host available and provisioned;
- runner online;
- production deployment successful;
- target-host provider REST/WebSocket acceptance successful;
- scanner/API readiness successful;
- persistent data write path operational;
- Docker health successful;
- immutable release promoted and recorded in `DEPLOYED_SHA`.

## Next gate: Phase 10

Public Custom GPT Action activation remains intentionally pending.

Next sequence:

1. choose real API domain/subdomain;
2. create DNS A record to the production public IPv4;
3. open OCI inbound TCP 80/443;
4. configure GitHub `production` variable `KTRADER_DOMAIN`;
5. configure GitHub `production` secret `KTRADER_ACTION_API_KEY`;
6. redeploy with the Caddy HTTPS profile;
7. pass `scripts/phase10_action_acceptance.py` against the real HTTPS origin;
8. only then render the deployment-specific OpenAPI and replace the `.invalid` server in the GPT Action configuration.

The repository template `custom_gpt/openapi.yaml` must remain on `https://api.k-trader.invalid` until Phase 10 live acceptance passes.
