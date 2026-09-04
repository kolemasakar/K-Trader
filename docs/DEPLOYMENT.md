# Deployment Specification v1.3

## Target

- Private GitHub repository.
- GitHub-hosted CI for pull requests/main validation.
- Ubuntu VPS.
- Docker Engine + Docker Compose.
- Repository-scoped self-hosted GitHub Actions runner for production deployment only.
- Primary production architecture: Linux ARM64 / Oracle Ampere A1.
- Caddy HTTPS reverse proxy/TLS when a real domain is configured.

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
-> Docker Compose build/start
-> localhost process health
-> provider REST/WS acceptance
-> scanner/API readiness acceptance
-> if `KTRADER_DOMAIN` is configured: public HTTPS + Phase 10 Action acceptance
-> mark release current

If the new release fails any required acceptance step, `deploy.sh` returns to the previous release when available.

## Container security baseline

K-Trader container:

- non-root user;
- read-only root filesystem;
- writable `/data` persistent volume only;
- temporary `/tmp` tmpfs;
- all Linux capabilities dropped;
- `no-new-privileges`;
- application port bound to host loopback only;
- restart policy `unless-stopped`.

## HTTPS and Action gate

The optional Caddy Compose profile is enabled only when `KTRADER_DOMAIN` is set.

Caddy terminates TLS and proxies to the internal K-Trader service. The application itself remains bound to host `127.0.0.1:8000`.

When `KTRADER_DOMAIN` is non-empty:

- `KTRADER_ACTION_API_KEY` is mandatory;
- DNS must resolve to the production host;
- ports 80/443 must be reachable;
- deployment waits for `https://<KTRADER_DOMAIN>` and executes `scripts/phase10_action_acceptance.py`;
- the release is not marked current unless the public Action endpoint passes acceptance.

This prevents a locally healthy release from being promoted while the public HTTPS endpoint or Action authentication is broken.

## Target-VPS live acceptance

`scripts/vps_acceptance.py` validates the first usable provider in configured priority order:

- instrument discovery;
- closed contiguous REST candles on 5m/15m/1h/4h/1d;
- public 5m WebSocket event.

`scripts/phase9_acceptance.sh` additionally requires:

- scanner `data_ready=true`;
- at least one published candidate/NO_TRADE analysis;
- API publication of all five canonical timeframes.

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
