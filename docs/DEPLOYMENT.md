# Deployment Specification v1.8

Updated: 2026-09-09

## Target

- GitHub repository with GitHub-hosted CI for pull requests/main validation.
- Ubuntu VPS.
- Docker Engine + Docker Compose.
- Repository-scoped self-hosted GitHub Actions runner for production deployment only.
- Primary production architecture: Linux ARM64 / Oracle Ampere A1.
- Caddy HTTPS reverse proxy/TLS for the public Action endpoint.
- Policy-constrained SentinelX channel for direct ChatGPT-to-production diagnostics and controlled maintenance.

## Current production state

Latest accepted production runtime was verified on 2026-09-08.

- Host: Oracle Cloud Ampere A1, Frankfurt, Ubuntu 24.04 Minimal aarch64.
- Active allocation: 1 OCPU / 6 GB RAM.
- Production runner: `k-trader-prod-arm64`.
- Public origin: `https://ktrader-api.duckdns.org`.
- DNS: `ktrader-api.duckdns.org -> 92.5.56.198`.
- Deployed SHA: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`.
- Deployed image: `k-trader:7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`.
- GitHub Actions deployment: `Deploy Production #9`, run `34177978988`, SUCCESS.
- Runtime identity: UID/GID `1002:1002`, aligned with the host `ktrader` user.
- Persistent application data: `/opt/k-trader/data`, owner `ktrader:ktrader`.
- Persistent Caddy storage: `/opt/k-trader/caddy_data` and `/opt/k-trader/caddy_config`, owner `root:root`, mode `700`.
- K-Trader container: healthy.
- Provider REST/WebSocket acceptance: PASS.
- MTF API acceptance: PASS.
- Phase 10 Action live acceptance: PASS.
- Runtime scanner acceptance during Deploy #9: `status=DEGRADED`, `symbols_ready=18`, `symbols_failed=2`; this did not fail service health or release acceptance.
- Application remains host-loopback-only at `127.0.0.1:8000`.
- Production provider: `binance_usdm`.
- PR #33 side-to-regime scoring contract correction is present in the deployed runtime.

Repository documentation HEAD may be newer than the deployed SHA when changes are documentation-only. This does not imply an undeployed runtime behavior change and does not require a production redeploy.

## SentinelX direct operator channel

A direct ChatGPT-to-VM management channel was accepted on 2026-09-09 through SentinelX.

Purpose:

- remove the need for the operator to relay every diagnostic command manually through SSH;
- permit fast production inspection and controlled maintenance from ChatGPT;
- preserve SSH as the independent recovery/bootstrap path;
- preserve GitHub PR, CI, and deployment workflows as the only canonical source/deployment path.

Accepted capabilities, subject to host policy, include allowlisted command execution, one-off Bash/Python scripts, selected file/log inspection, Docker and K-Trader health diagnostics, approved `docker exec` operations, and selected systemd inspection/restart actions.

Security posture after hardening:

- agent runs as dedicated unprivileged user `sentinelx`;
- bootstrap `NOPASSWD: ALL` was removed;
- sudo is constrained to a narrow K-Trader/SentinelX operational set;
- arbitrary root execution is denied;
- structured filesystem access is read-only;
- current readable K-Trader paths are `/opt/k-trader/releases` and `/opt/k-trader/data`;
- no structured writable paths are exposed;
- SentinelX identity and GitHub runner credential files are outside the structured read policy;
- `/etc/sentinelx/config.yaml` is not writable by the agent through SentinelX filesystem tools.

Canonical operating/security details: `docs/SENTINELX_REMOTE_ACCESS.md`.

## Runtime layout

Persistent runtime state lives outside the runner workspace:

```text
/opt/k-trader/
  releases/<commit-sha>/
  current -> releases/<commit-sha>
  data/
  caddy_data/
  caddy_config/
  runner/
  DEPLOYED_SHA
```

The GitHub runner `_work` directory is not a persistence location.

Research persistence includes:

- immutable Phase 11F universe captures under `/opt/k-trader/data/research/universe` on the host (`/data/research/universe` in the container);
- Phase 11G materialized chains and dataset catalogue under `/opt/k-trader/data/research/phase11g` on the host (`/data/research/phase11g` in the container).

## CI gate

`.github/workflows/ci.yml` executes on GitHub-hosted `ubuntu-latest` for PRs and pushes to main.

Mandatory validation includes:

1. Python 3.12 install.
2. `compileall` over source/tests/scripts.
3. repository-wide `pytest`.
4. Docker Compose configuration validation.
5. Docker image build.
6. production runtime import from the built image.
7. `vps_acceptance.py` packaging check.
8. amd64 and arm64 container validation.

The production self-hosted runner never executes PR CI.

Latest accepted code validation before this documentation branch:

- canonical main SHA `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`;
- post-merge Tests run `34177001398`: PASS;
- post-merge CI run `34177001482`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS.

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

```text
approved main
-> immutable release export
-> derive runtime UID/GID from production runner user
-> verify persistent data directory is writable
-> Docker Compose build/start
-> localhost process health
-> provider REST/WS acceptance
-> scanner/API readiness acceptance
-> public HTTPS + Phase 10 Action acceptance
-> mark release current
```

If a required acceptance step fails, deployment fails closed and returns to the previous release when available.

## Runtime identity and storage contract

The K-Trader image accepts `KTRADER_RUNTIME_UID` and `KTRADER_RUNTIME_GID`; deployment derives these from the self-hosted runner user with `id -u` / `id -g`.

This is required because `/opt/k-trader/data` is a host bind mount. The container process identity must match host ownership. Do not hard-code a base-image system UID such as `999` as a production contract.

Current verified application identity:

```text
/opt/k-trader/data  ktrader:ktrader  uid:gid 1002:1002
```

Caddy storage uses a different ownership contract because the capability-dropped root process must have ordinary DAC write access:

```text
/opt/k-trader/caddy_data   root:root 0700
/opt/k-trader/caddy_config root:root 0700
```

`scripts/provision_vps.sh` creates these directories with that ownership.

## Container security baseline

K-Trader container:

- non-root user;
- runtime UID/GID aligned with deployment host user;
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

The read-only root filesystem is intentional. Operator diagnostics that need to execute a temporary Python script should stream the host file into `docker exec -i ... python -` rather than `docker cp` it into the container root filesystem.

## Health semantics

`/health` preserves its public response shape. Scanner partial failures may produce `scanner_status=DEGRADED` while the service remains usable when canonical data is ready and fresh.

The Docker healthcheck evaluates service readiness, not a requirement that scanner status itself equal `READY`. Stale scanner data still fails the health gate.

Accepted Deploy #9 evidence:

- provider: `binance_usdm`;
- provider REST/WebSocket acceptance: PASS;
- scanner readiness acceptance: PASS with 18 ready / 2 failed and DEGRADED status;
- MTF API publication: PASS;
- K-Trader container: healthy;
- Caddy HTTPS/TLS: PASS;
- Phase 10 Action live acceptance: PASS;
- final deployed SHA: `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`.

## HTTPS and Action gate

The Caddy Compose profile is enabled when `KTRADER_DOMAIN` is set.

Current production configuration:

- `KTRADER_DOMAIN=ktrader-api.duckdns.org` as a GitHub `production` Environment variable;
- `KTRADER_ACTION_API_KEY` as a GitHub `production` Environment secret;
- DNS A record to `92.5.56.198`;
- OCI stateful ingress TCP 80/443;
- host firewall explicitly allows TCP 80/443 before terminal reject;
- firewall rules persisted through `netfilter-persistent`.

When `KTRADER_DOMAIN` is non-empty, deployment requires public HTTPS and Phase 10 Action acceptance before release promotion.

## Target-VPS live acceptance

`scripts/vps_acceptance.py` validates the first usable provider in configured priority order:

- instrument discovery;
- closed contiguous REST candles on 5m/15m/1h/4h/1d;
- public 5m WebSocket event.

`scripts/phase9_acceptance.sh` additionally requires scanner data readiness and API publication of all five canonical timeframes. Local protected `/v1/*` checks use Bearer authentication when `KTRADER_ACTION_API_KEY` is configured.

`scripts/phase10_action_acceptance.py` validates the public HTTPS/read-only Action boundary and required TradingDecision response fields.

Provider failure is isolated; bars from failed and fallback providers are never combined.

## Historical fail-closed evidence

Earlier Phase 10 deployment incidents validated rollback behavior:

- local acceptance initially lacked Bearer authentication after Action auth activation; PR #19 fixed the integration defect;
- Caddy initially could not persist ACME state under incorrect host bind-mount ownership; ownership/provisioning were corrected.

Subsequent accepted deployments culminated in Deploy Production #9 on `7fa20c3d7f0d89ae628eb2bf21e4c50164eb3eab`.

## Provisioning

Canonical operator instructions are in `docs/VPS_PROVISIONING.md`.

Provisioning and runner registration remain separate from normal deployment because runner registration requires a short-lived GitHub token.
