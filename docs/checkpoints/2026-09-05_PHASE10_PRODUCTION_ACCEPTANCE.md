# K-Trader Control Point — Phase 10 Production Acceptance

Date: 2026-09-05

Status: **STABLE CHECKPOINT / PHASE 10 BACKEND CLOSED / GPT BUILDER CONFIGURATION NEXT**

## Canonical repository and production state

- Repository: `kolemasakar/K-Trader`
- Production branch: `main`
- Accepted production SHA: `7c60a77b9773774373ea4a3f095c5ab2ee7767e2`
- Authentication integration fix: PR #19
- Production deployment: `Deploy Production #4`, run `33945690930`, successful re-run
- Public origin: `https://ktrader-api.duckdns.org`
- Repository remains read-only with respect to trading execution; K-Trader does not place orders.

## Production infrastructure

- Oracle Cloud Ampere A1 production VM: `k-trader-prod`
- Region: Frankfurt
- OS: Ubuntu 24.04 Minimal aarch64
- Shape: `VM.Standard.A1.Flex`
- Allocation: 1 OCPU / 6 GB RAM
- Public IPv4: `92.5.56.198`
- DNS: `ktrader-api.duckdns.org -> 92.5.56.198`
- Self-hosted runner label: `k-trader-prod-arm64`
- Runtime service user: `ktrader`
- Application bind: `127.0.0.1:8000`
- Public ingress: Caddy TCP 80/443

## Accepted runtime state

```text
DEPLOYED_SHA = 7c60a77b9773774373ea4a3f095c5ab2ee7767e2
K-Trader container = healthy
runtime uid:gid = 1002:1002
data dir owner = ktrader:ktrader
data dir mode = 750
caddy_data owner/mode = root:root 700
caddy_config owner/mode = root:root 700
API bind = 127.0.0.1:8000
public origin = https://ktrader-api.duckdns.org
mode = read_only
data_ready = true
provider = binance_usdm
action_auth_enabled = true
```

Verified HTTPS health response at activation:

```json
{"status":"ok","mode":"read_only","api_version":"phase8-v1","data_ready":true,"scanner_status":"DEGRADED","provider_id":"binance_usdm","action_auth_enabled":true}
```

`scanner_status=DEGRADED` is acceptable when usable canonical data remains ready and fresh; per-symbol failures are isolated.

## Phase 10 live acceptance evidence

Successful production deployment proved:

- native ARM64 build and container health;
- Binance USD-M REST `5m,15m,1h,4h,1d` acceptance;
- Binance USD-M public WebSocket `5m` acceptance;
- scanner `data_ready=true`;
- accepted cycle: 17 symbols ready / 3 failed;
- MTF API publication on all five canonical intervals;
- DNS and TCP 80/443 reachability;
- automatic Let's Encrypt ACME HTTP-01 validation;
- persistent TLS certificate storage;
- public HTTPS health;
- Bearer authentication enabled;
- unauthenticated protected `/v1/*` behavior checked by Phase 10 acceptance;
- authenticated Action responses checked by Phase 10 acceptance;
- final log: `PASS Phase 10 Action live acceptance`;
- immutable release promotion and `DEPLOYED_SHA` update.

## Closed activation defects

1. **Phase 9 local acceptance vs Action auth**
   - enabling `KTRADER_ACTION_API_KEY` correctly protected `/v1/*`;
   - Phase 9 local probes initially omitted the Bearer header and failed with 401;
   - PR #19 made the local acceptance path authenticate when the key is configured.

2. **Caddy persistent storage DAC permissions**
   - Caddy initially failed with `mkdir /data/caddy: permission denied` and `mkdir /config/caddy: permission denied`;
   - the container runs uid 0 but drops `CAP_DAC_OVERRIDE` with the hardened capability set;
   - production Caddy storage was corrected to root-owned mode 0700;
   - `scripts/provision_vps.sh` now provisions that ownership permanently.

Both defects failed closed and triggered rollback before the final accepted deployment.

## Network/firewall checkpoint

OCI Security List:

- stateful TCP 80 from `0.0.0.0/0`;
- stateful TCP 443 from `0.0.0.0/0`.

Host firewall:

- TCP 22/80/443 allowed before terminal reject;
- persisted with `netfilter-persistent`;
- port 8000 is not public.

## Secret handling

- `KTRADER_ACTION_API_KEY` is stored only in GitHub Environment `production` and must be entered separately in GPT Action Bearer authentication.
- The secret value is not present in this repository or checkpoint.
- The DuckDNS account token is not required by the deployed application and is not committed.

## Canonical Custom GPT state

- `custom_gpt/openapi.yaml` now uses `https://ktrader-api.duckdns.org`.
- Eight Action operations remain GET/read-only.
- `/health` remains public.
- `/v1/*` remains Bearer-protected in production.
- `custom_gpt/BUILDER_CHECKLIST.md` describes the remaining GPT-side configuration.

## Next canonical sequence

1. open the existing K_Trader GPT Builder;
2. configure Action authentication as API key / Bearer using the existing secret;
3. import canonical `custom_gpt/openapi.yaml`;
4. verify all eight operations in Preview;
5. verify `data_ready=true` canonical mode and failover to `WATCHLIST ONLY` when Action is unavailable/not ready;
6. complete publishing/privacy checks required by the selected distribution mode.

Do not expose port 8000 and do not place secret values in repository files or chat-based transition packages.
