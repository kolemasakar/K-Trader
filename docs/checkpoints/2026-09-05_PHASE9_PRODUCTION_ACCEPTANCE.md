# K-Trader Control Point — Phase 9 Production Acceptance

Date: 2026-09-05

Status: **STABLE CHECKPOINT / PHASE 9 CLOSED / PHASE 10 NEXT**

## Canonical repository state

- Repository: `kolemasakar/K-Trader`
- Branch at accepted runtime: `main`
- Accepted production SHA: `9ed572349ed0195e518f128894a1f187419dbcc1`
- Production-fix PR: #17
- Production deployment run: `33920829993` — SUCCESS
- Repository remains read-only with respect to trading execution; K-Trader does not place orders.

## Production infrastructure

- Oracle Cloud Ampere A1 production VM: `k-trader-prod`
- Region: Frankfurt
- OS: Ubuntu 24.04 Minimal aarch64
- Shape: `VM.Standard.A1.Flex`
- Allocation: 1 OCPU / 6 GB RAM
- Public IPv4: `92.5.56.198`
- Self-hosted runner label: `k-trader-prod-arm64`
- Runtime service user: `ktrader`

## Accepted runtime state

```text
DEPLOYED_SHA = 9ed572349ed0195e518f128894a1f187419dbcc1
container = healthy
runtime uid:gid = 1002:1002
data dir owner = ktrader:ktrader
data dir mode = 750
API bind = 127.0.0.1:8000
mode = read_only
data_ready = true
provider = binance_usdm
action_auth_enabled = false
```

Latest operator health response at checkpoint:

```json
{"status":"ok","mode":"read_only","api_version":"phase8-v1","data_ready":true,"scanner_status":"DEGRADED","provider_id":"binance_usdm","action_auth_enabled":false}
```

`scanner_status=DEGRADED` is acceptable when usable canonical data remains ready and fresh; per-symbol failures are isolated.

## Phase 9 live acceptance evidence

Successful production workflow proved:

- native ARM64 image build;
- host/container runtime identity alignment;
- writable persistent SQLite data path;
- Binance USD-M REST data on `5m,15m,1h,4h,1d`;
- Binance USD-M public WebSocket `5m`;
- scanner `data_ready=true`;
- final deployment-cycle scanner result: 13 symbols ready / 7 failed;
- MTF API publication on all five canonical intervals;
- Docker `healthy` state;
- immutable release promotion and `DEPLOYED_SHA` update.

## Persistent paths

```text
/opt/k-trader/releases/<sha>/
/opt/k-trader/current
/opt/k-trader/data/ktrader.db
/opt/k-trader/data/backups/
/opt/k-trader/data/research/
/opt/k-trader/DEPLOYED_SHA
/opt/k-trader/runner/
```

Persistent state is outside the GitHub Actions runner `_work` tree.

## Closed production defects

1. **SQLite bind-mount UID mismatch**
   - original image user UID/GID `999:999` did not match host `ktrader` `1002:1002`;
   - failure: `sqlite3.OperationalError: unable to open database file`;
   - permanent fix: build runtime identity from deployment user's UID/GID and fail deployment if data path is not writable.

2. **Docker health vs partial scanner degradation**
   - partial symbol failures produced valid `DEGRADED` scanner state with `data_ready=true`;
   - old health semantics incorrectly marked the container unhealthy;
   - permanent fix preserves public `/health` shape while allowing fresh usable degraded scanner state to remain service-healthy.

## Custom GPT / public endpoint state

Phase 10 is **not active yet**.

- `KTRADER_DOMAIN` is not configured.
- `KTRADER_ACTION_API_KEY` is not configured.
- Caddy public HTTPS profile is not active.
- API remains localhost-only.
- `custom_gpt/openapi.yaml` must retain `https://api.k-trader.invalid` until live Phase 10 acceptance passes.

## Next canonical sequence

1. choose API domain/subdomain;
2. DNS A record -> `92.5.56.198`;
3. OCI ingress TCP 80/443;
4. configure GitHub Environment `production` variable `KTRADER_DOMAIN`;
5. configure GitHub Environment `production` secret `KTRADER_ACTION_API_KEY`;
6. redeploy `main`;
7. pass public HTTPS/Action acceptance;
8. render deployment-specific OpenAPI;
9. configure and validate the Custom GPT Action.

Do not bypass Phase 10 acceptance and do not expose port 8000 publicly.
