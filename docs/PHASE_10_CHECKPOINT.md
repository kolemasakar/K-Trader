# Phase 10 Production Activation Checkpoint

Date: 2026-09-05

Status: COMPLETE / PUBLIC HTTPS + ACTION API LIVE ACCEPTANCE VERIFIED.

## Production endpoint

- Public origin: `https://ktrader-api.duckdns.org`.
- DNS A record: `ktrader-api.duckdns.org -> 92.5.56.198`.
- Production host: Oracle Cloud Ampere A1, Frankfurt, Ubuntu 24.04 Minimal aarch64.
- Application bind remains local-only: `127.0.0.1:8000`.
- Public ingress is terminated by Caddy on TCP 80/443; HTTP redirects to HTTPS.
- `KTRADER_ACTION_API_KEY` is configured only as a GitHub `production` Environment secret and must not be committed or copied into documentation.

## Network and host firewall evidence

OCI ingress was verified for stateful TCP 80 and 443 from `0.0.0.0/0`.

Host iptables policy keeps the terminal reject while explicitly allowing SSH/HTTP/HTTPS before it:

```text
-A INPUT ... --dport 22 -j ACCEPT
-A INPUT ... --dport 80 -j ACCEPT
-A INPUT ... --dport 443 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
```

The rules were persisted through `netfilter-persistent`. Port 8000 was not exposed publicly.

## Phase 10 deployment defects discovered and resolved

### 1. Phase 9 acceptance did not authenticate local `/v1/*` probes

The first public deployment attempt enabled `KTRADER_ACTION_API_KEY`, which correctly protected all `/v1/*` endpoints. The existing Phase 9 acceptance script still queried protected local endpoints without a Bearer header and therefore looped on `401 Unauthorized`.

Resolution:

- PR #19: `Fix Phase 10 authenticated Phase 9 acceptance`;
- local Phase 9 acceptance now sends `Authorization: Bearer ...` when `KTRADER_ACTION_API_KEY` is configured;
- behavior remains compatible with deployments where Action authentication is disabled;
- repository CI and Tests passed before merge;
- merged production SHA: `7c60a77b9773774373ea4a3f095c5ab2ee7767e2`.

### 2. Caddy persistent storage ownership

The next deployment passed Phase 9 but failed TLS with:

```text
mkdir /config/caddy: permission denied
mkdir /data/caddy: permission denied
obtaining certificate: failed storage check
```

The Caddy container runs as uid 0 but with all Linux capabilities dropped. Without `CAP_DAC_OVERRIDE`, uid 0 cannot write a bind-mounted directory owned by another uid when ordinary mode bits deny owner-write access for that identity.

Production storage was corrected to:

```text
/opt/k-trader/caddy_data   -> 0:0 mode 700
/opt/k-trader/caddy_config -> 0:0 mode 700
```

The canonical provisioning script now creates these two Caddy storage directories as `root:root` mode `0700`, while K-Trader data remains owned by the dedicated `ktrader` runtime user.

## TLS evidence

After the storage correction, Caddy completed Let's Encrypt ACME HTTP-01 validation and persisted the issued certificate under `/opt/k-trader/caddy_data`.

Verified log evidence included:

```text
authorization finalized ... authz_status=valid
validations succeeded; finalizing order
successfully downloaded available certificate chains
certificate obtained successfully
```

A direct HTTPS health request then returned:

```json
{"status":"ok","mode":"read_only","api_version":"phase8-v1","data_ready":true,"scanner_status":"DEGRADED","provider_id":"binance_usdm","action_auth_enabled":true}
```

## Final deployment evidence

GitHub Actions workflow: `Deploy Production #4`, run ID `33945690930`, re-run attempt.

Result: SUCCESS.

Production SHA:

`7c60a77b9773774373ea4a3f095c5ab2ee7767e2`

Acceptance evidence:

```text
PASS provider=binance_usdm symbol=BTCUSDT rest_intervals=5m,15m,1h,4h,1d websocket=5m
PASS runtime status=DEGRADED provider=binance_usdm symbols_ready=17 symbols_failed=3
PASS MTF API provider=binance_usdm symbol=FLOCKUSDT intervals=5m,15m,1h,4h,1d
K-Trader container: healthy
Caddy: listening on 80/443
PASS Phase 10 Action live acceptance
Deployed 7c60a77b9773774373ea4a3f095c5ab2ee7767e2
```

`DEGRADED` scanner status is acceptable when canonical data remains fresh and `data_ready=true`; per-symbol failures remain isolated.

## Canonical repository state after this checkpoint

- `custom_gpt/openapi.yaml` uses `https://ktrader-api.duckdns.org` as the production server origin.
- Bearer authentication remains mandatory for `/v1/*` in the production Action path.
- `/health` remains public and read-only.
- application port 8000 remains host-loopback-only.
- Caddy certificate/config state is persistent outside the GitHub runner workspace.
- production deployment remains manual-only from approved `main` and fail-closed with rollback.

## Remaining product-side work

The backend/API activation is complete. The remaining Phase 10 product configuration is performed in the existing K_Trader GPT Builder:

1. import the canonical production `custom_gpt/openapi.yaml`;
2. configure API-key authentication as Bearer using the same secret stored in GitHub Environment `production`;
3. verify all eight read-only operations in Preview;
4. verify fallback to `WATCHLIST ONLY` if Action readiness/authentication fails;
5. complete publishing/privacy checks appropriate to the selected GPT distribution mode.

No secret value is recorded in this checkpoint.
