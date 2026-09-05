# Deployment Specification v1.5

## Target

- Private GitHub repository.
- GitHub-hosted CI for pull requests/main validation.
- Ubuntu VPS.
- Docker Engine + Docker Compose.
- Repository-scoped self-hosted GitHub Actions runner for production deployment only.
- Primary production architecture: Linux ARM64 / Oracle Ampere A1.
- Caddy HTTPS reverse proxy/TLS for the public Action endpoint.

## Current production state

Phase 10 public HTTPS production deployment was verified on 2026-09-05.

- Host: Oracle Cloud Ampere A1, Frankfurt, Ubuntu 24.04 Minimal aarch64.
- Active allocation: 1 OCPU / 6 GB RAM.
- Production runner: `k-trader-prod-arm64`.
- Public origin: `https://ktrader-api.duckdns.org`.
- DNS: `ktrader-api.duckdns.org -> 92.5.56.198`.
- Deployed SHA: `7c60a77b9773774373ea4a3f095c5ab2ee7767e2`.
- GitHub Actions deployment: `Deploy Production #4`, run `33945690930`, successful re-run attempt.
- Runtime identity: UID/GID `1002:1002`, aligned with the host `ktrader` user.
- Persistent application data: `/opt/k-trader/data`, owner `ktrader:ktrader`, mode `750`.
- Persistent Caddy storage: `/opt/k-trader/caddy_data` and `/opt/k-trader/caddy_config`, owner `root:root`, mode `700`.
- Final local health: `status=ok`, `mode=read_only`, `data_ready=true`.
- Final Docker state: K-Trader `healthy`; Caddy active on 80/443.
- Application remains host-loopback-only at `127.0.0.1:8000`.
- Phase 10 public HTTPS/Action live acceptance: PASS.

The canonical OpenAPI file now uses `https://ktrader-api.duckdns.org` because the live Phase 10 Action gate passed.

## Runtime layout

Persistent runtime state lives outside the runner workspace:

`/opt/k-trader/`
- `releases/<commit-sha>/`
- `current -> releases/<commit-sha>`
- `data/`
- `caddy_data/`
- `caddy_config/`
- `runner/`
- `DEPLOYED_SHA`

The GitHub runner `_work` directory is not a persistence location.

## CI gate

`.github/workflows/ci.yml` executes on GitHub-hosted `ubuntu-latest` for PRs and pushes to main.

Mandatory jobs:

1. Python 3.12 install.
2. `compileall` over source/tests/scripts.
3. repository-wide `pytest`.
4. Docker Compose configuration validation.
5. Docker image build.
6. production runtime import from the built image.
7. verify `vps_acceptance.py` is packaged in the image.
8. validate both amd64 and arm64 container builds.

The production self-hosted runner never executes PR CI.

## Production deploy

`.github/workflows/deploy.yml` is `workflow_dispatch` only.

Requirements:

- ref must be `main`;
- runner labels: `self-hosted`, `linux`, `k-trader-prod-arm64`;
- host architecture must be `aarch64`/`arm64`;
- GitHub environment: `production`;
- checkout credentials are not persisted after checkout.

Deployment uses `scripts/deploy.sh`.

Flow:

approved main
-> immutable release export
-> derive runtime UID/GID from the production runner user
-> verify persistent application data directory is writable
-> Docker Compose build/start with matching K-Trader runtime identity
-> localhost process health
-> provider REST/WS acceptance
-> scanner/API readiness acceptance
-> public HTTPS + Phase 10 Action acceptance when `KTRADER_DOMAIN` is configured
-> mark release current

If the new release fails any required acceptance step, `deploy.sh` returns to the previous release when available.

## Runtime identity and persistent storage

The K-Trader container image accepts build arguments `KTRADER_RUNTIME_UID` and `KTRADER_RUNTIME_GID`. Production deployment exports these from the self-hosted runner user with `id -u` / `id -g` before the image is built.

This is required because `/opt/k-trader/data` is a host bind mount. The K-Trader process identity must match the host owner of the persistent SQLite/research/backup tree. Deployment fails closed before build if the production data directory is not writable by the deployment user.

Do not hard-code a base-image system UID such as `999` as a production ownership contract. The verified Oracle production identity is currently `1002:1002`, but the deployment mechanism is intentionally dynamic.

Caddy has a different storage requirement. The Caddy container runs as uid 0 with all Linux capabilities dropped. Because `CAP_DAC_OVERRIDE` is absent, its bind-mounted `/data` and `/config` trees must be writable through ordinary DAC ownership/mode bits. The verified production contract is:

```text
/opt/k-trader/caddy_data   root:root 0700
/opt/k-trader/caddy_config root:root 0700
```

`scripts/provision_vps.sh` creates these directories with that ownership. Do not change them to the `ktrader` user while the current Caddy security profile remains capability-dropped.

## Container security baseline

K-Trader container:

- non-root user;
- runtime UID/GID aligned with the deployment host user;
- read-only root filesystem;
- writable `/data` persistent volume only;
- temporary `/tmp` tmpfs;
- all Linux capabilities dropped;
- `no-new-privileges`;
- application port bound to host loopback only;
- restart policy `unless-stopped`.

Caddy container:

- reverse-proxy/TLS role only;
- all capabilities dropped, then only `NET_BIND_SERVICE` added;
- `no-new-privileges`;
- persistent `/data` and `/config` bind mounts;
- public host ports 80/443 only.

## Health semantics

`/health` preserves its public response shape. Scanner partial failures may produce `scanner_status=DEGRADED` while the service remains usable when canonical data is ready and fresh.

The Docker healthcheck therefore evaluates service readiness from the health response without requiring the scanner status string itself to be `READY`. A fresh `data_ready=true` runtime can remain Docker-healthy even when some symbols fail independently. Stale scanner data still degrades health and fails the container health gate.

Verified final Phase 10 deployment evidence:

- provider acceptance: Binance USD-M REST `5m,15m,1h,4h,1d` plus WebSocket `5m` — PASS;
- scanner: `DEGRADED`, 17 symbols ready / 3 failed in the accepted deployment cycle;
- `data_ready=true`;
- MTF API publication for all five canonical intervals — PASS;
- K-Trader container — `healthy`;
- Caddy HTTPS — PASS;
- Phase 10 Action live acceptance — PASS.

## HTTPS and Action gate

The Caddy Compose profile is enabled when `KTRADER_DOMAIN` is set.

Caddy terminates TLS and proxies to the internal K-Trader service. The application itself remains bound to host `127.0.0.1:8000`.

Current production configuration:

- `KTRADER_DOMAIN=ktrader-api.duckdns.org` as a GitHub `production` Environment variable;
- `KTRADER_ACTION_API_KEY` as a GitHub `production` Environment secret;
- DNS A record to `92.5.56.198`;
- OCI stateful ingress TCP 80/443;
- host firewall explicitly allows TCP 80/443 before its terminal reject;
- host firewall rules persisted through `netfilter-persistent`.

When `KTRADER_DOMAIN` is non-empty:

- `KTRADER_ACTION_API_KEY` is mandatory;
- DNS must resolve to the production host;
- ports 80/443 must be reachable;
- deployment waits for `https://<KTRADER_DOMAIN>` and executes `scripts/phase10_action_acceptance.py`;
- the release is not marked current unless the public Action endpoint passes acceptance.

This prevents a locally healthy release from being promoted while the public HTTPS endpoint or Action authentication is broken.

## Phase 10 incident evidence

Two fail-closed deployment attempts proved rollback behavior before final success:

1. the first public deployment exposed that Phase 9 local `/v1/*` acceptance requests lacked Bearer authentication once Action auth was enabled; PR #19 fixed that integration defect;
2. the next attempt reached HTTPS but Caddy could not persist ACME state because the capability-dropped root process did not own the host bind mounts; ownership was corrected and the provisioning contract was hardened.

Both failed attempts rolled back to the previous accepted release. The successful re-run then passed all Phase 9 and Phase 10 gates and promoted SHA `7c60a77b9773774373ea4a3f095c5ab2ee7767e2`.

Detailed evidence is in `docs/PHASE_10_CHECKPOINT.md`.

## Target-VPS live acceptance

`scripts/vps_acceptance.py` validates the first usable provider in configured priority order:

- instrument discovery;
- closed contiguous REST candles on 5m/15m/1h/4h/1d;
- public 5m WebSocket event.

`scripts/phase9_acceptance.sh` additionally requires:

- scanner `data_ready=true`;
- at least one published candidate/NO_TRADE analysis;
- API publication of all five canonical timeframes;
- Bearer authentication on local `/v1/*` checks when `KTRADER_ACTION_API_KEY` is configured.

When public HTTPS is enabled, `scripts/phase10_action_acceptance.py` additionally requires:

- HTTPS origin;
- read-only health mode;
- `data_ready=true`;
- Action authentication enabled when the production API key is configured;
- unauthenticated protected requests rejected;
- authenticated scanner status/signals/candidates responses with required TradingDecision fields.

Provider failure is recorded and the next provider is tried. Bars from failed and fallback providers are never combined.

## Provisioning

Canonical operator instructions are in `docs/VPS_PROVISIONING.md`.

Provisioning and runner registration are intentionally separate from normal deployment because runner registration requires a short-lived GitHub token.
