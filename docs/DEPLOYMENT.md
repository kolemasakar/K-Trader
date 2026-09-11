# Deployment Specification v1.10

Updated: 2026-09-11

## Target

- GitHub repository with GitHub-hosted CI for pull requests/main validation;
- Ubuntu production VPS;
- Docker Engine + Docker Compose;
- repository-scoped self-hosted GitHub Actions runner for production deployment only;
- primary production architecture: Linux ARM64 / Oracle Ampere A1;
- Caddy HTTPS reverse proxy/TLS for the public Action endpoint;
- policy-constrained SentinelX channel for diagnostics and controlled maintenance.

## Current production state

Latest accepted production runtime was verified on 2026-09-11.

- host: Oracle Cloud Ampere A1, Ubuntu 24.04 aarch64;
- active allocation: 1 OCPU / 6 GB RAM;
- production runner label: `k-trader-prod-arm64`;
- public origin: `https://ktrader-api.duckdns.org`;
- deployed SHA: `30119a44fa82b1029d2de6e3a6f76320a7705079`;
- deployed image: `k-trader:30119a44fa82b1029d2de6e3a6f76320a7705079`;
- GitHub Actions deployment: `Deploy Production #11`, SUCCESS;
- runtime identity: UID/GID `1002:1002` aligned with host user `ktrader`;
- persistent application data: `/opt/k-trader/data`;
- persistent Caddy storage: `/opt/k-trader/caddy_data`, `/opt/k-trader/caddy_config`;
- application container: healthy;
- `/health`: `status=ok`, `data_ready=true`;
- provider: `binance_usdm`;
- provider REST/WebSocket acceptance: PASS;
- MTF API acceptance: PASS;
- public HTTPS / Phase 10 Action acceptance: PASS;
- application API remains host-loopback-only at `127.0.0.1:8000` behind Caddy;
- Action authentication remains enabled;
- FAST production lifecycle: `setup_interval=5m`, `setup_max_age_bars=12`, TTL `3600s`;
- M15/H1 lifecycle profiles remain research-only.

Documentation-only commits may make repository `main` newer than the deployed runtime SHA without requiring a production redeploy.

## 2026-09-11 runtime hardening acceptance

The deployed runtime includes two operational hardening changes with no trading-rule changes.

### D1 history retry backoff

Young contracts that cannot satisfy the mandatory D1 history requirement remain fail-closed but no longer trigger the same impossible provider bootstrap every scanner cycle.

Accepted behavior:

- D1 minimum remains unchanged;
- insufficient-history symbols remain ineligible;
- retry is deferred until the next UTC day boundary;
- no alternate symbol is promoted merely to fill the analysis shortlist;
- RR, ATR, TTL, target, scoring and structure logic are unchanged.

### Recent MTF contiguity heal

Runtime readiness now validates contiguity of the recent required MTF window in addition to count and freshness.

If a recent sequence has a gap:

```text
recent MTF gap
-> readiness fails
-> canonical bootstrap repair
-> symbol remains fail-closed
-> analysis resumes only on valid contiguous history
```

Production verification after Deploy #11:

- `IOSTUSDT 15m`: required recent 250-bar window contiguous, gaps `[]`;
- `DOTUSDT 15m`: required recent 250-bar window contiguous, gaps `[]`;
- both repair bootstraps succeeded.

## Scanner health semantics

Scanner partial failures may produce `scanner_status=DEGRADED` while service health remains `ok` when canonical usable data is ready and fresh.

Accepted post-deploy observation:

- scanner: `DEGRADED`;
- `symbols_ready=17`;
- `symbols_failed=3`;
- `live_streaming=true`;
- current failed symbols: `牛来USDT`, `MARSCOINUSDT`, `PONSUSDT`;
- reason: insufficient closed D1 history;
- retries deferred to the next UTC day boundary;
- `/v1/signals`: `0`.

This DEGRADED state is expected young-contract ineligibility, not evidence of the prior mature-symbol `15m` gap defect.

The Docker healthcheck evaluates service readiness, not a requirement that scanner status equal `READY`. Stale or unusable scanner state still fails the health gate.

## Runtime layout

Persistent state lives outside the GitHub runner workspace:

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

The runner `_work` directory is not a persistence location.

Research persistence includes:

- immutable universe captures under `/opt/k-trader/data/research/universe` on the host (`/data/research/universe` in the container);
- Phase 11G artefacts/catalogue under `/opt/k-trader/data/research/phase11g` (`/data/research/phase11g` in the container).

## CI gate

`.github/workflows/ci.yml` runs on GitHub-hosted runners for pull requests/main validation.

Canonical required jobs:

- Python 3.12 repository-wide validation;
- Python 3.14 repository-wide validation;
- Docker amd64 build/runtime validation;
- Docker arm64 build/runtime validation;
- `canonical-merge-gate` requiring all canonical jobs to succeed.

The production self-hosted runner does not execute pull-request CI.

PR #46 acceptance immediately before Deploy #11:

- Python 3.12: PASS;
- Python 3.14: PASS;
- Docker amd64: PASS;
- Docker arm64: PASS;
- `canonical-merge-gate`: PASS;
- squash merge produced runtime SHA `30119a44fa82b1029d2de6e3a6f76320a7705079`.

## Production deploy

`.github/workflows/deploy.yml` remains `workflow_dispatch` only.

Requirements:

- ref: `main`;
- runner labels include `self-hosted`, `linux`, `k-trader-prod-arm64`;
- host architecture must be ARM64;
- GitHub environment: `production`;
- checkout credentials are not persisted after checkout.

Deployment uses `scripts/deploy.sh` and immutable releases.

Canonical flow:

```text
approved main
-> exact checkout
-> architecture gate
-> immutable release export
-> derive runtime UID/GID
-> build image
-> start candidate release
-> localhost health
-> provider REST/WS acceptance
-> scanner/MTF readiness acceptance
-> public HTTPS + Phase 10 Action acceptance
-> promote current symlink + DEPLOYED_SHA
```

If required acceptance fails, deployment fails closed and rolls back to the previous accepted release when available.

## Deploy Production #11 evidence

Run #11 was manually dispatched on `main` and checked out exact SHA:

`30119a44fa82b1029d2de6e3a6f76320a7705079`

Acceptance log recorded:

- ARM64 architecture gate: PASS;
- image build: PASS;
- application container healthy;
- public provider REST/WebSocket acceptance: PASS;
- scanner data readiness: PASS;
- MTF API: PASS;
- public HTTPS / Phase 10 Action live acceptance: PASS;
- release promoted;
- `/opt/k-trader/DEPLOYED_SHA` updated to exact SHA;
- `/opt/k-trader/current` points to exact release directory.

## Runtime identity and storage contract

The image accepts `KTRADER_RUNTIME_UID` and `KTRADER_RUNTIME_GID`; deployment derives these from the self-hosted runner account.

Current application identity remains:

```text
/opt/k-trader/data  ktrader:ktrader  uid:gid 1002:1002
```

The container runtime identity must match host ownership of the bind-mounted persistent data directory.

Caddy persistent storage remains separately owned according to the Caddy runtime contract.

## Container security baseline

K-Trader container:

- non-root runtime user;
- host-aligned runtime UID/GID;
- read-only root filesystem;
- persistent writable `/data` volume;
- temporary `/tmp` tmpfs;
- Linux capabilities dropped;
- `no-new-privileges`;
- application port bound to host loopback;
- restart policy `unless-stopped`.

Caddy:

- reverse-proxy/TLS role only;
- minimal capability set required for public ports;
- persistent `/data` and `/config` mounts;
- public host ports 80/443.

## SentinelX operator channel

Policy-constrained SentinelX access is accepted for direct production diagnostics and selected maintenance.

Security boundary:

- agent runs unprivileged;
- unrestricted `NOPASSWD: ALL` is prohibited;
- arbitrary root execution is denied;
- structured K-Trader filesystem access is read-only;
- approved readable K-Trader trees include `/opt/k-trader/releases` and `/opt/k-trader/data`;
- SSH remains the independent recovery/bootstrap path;
- source changes and production activation must still go through GitHub PR/CI/deploy.

Canonical details: `docs/SENTINELX_REMOTE_ACCESS.md`.

## Research/production separation

Production runtime and research artefacts share data acquisition, but research does not silently alter live trading rules.

- FAST M5/60m is the only active production lifecycle profile;
- M15/H1 studies are research-only;
- `RR >= 3`, ATR-used, HTF, primary-level strength, structural target and freshness rules are unchanged by research tooling;
- dataset materialization is not a deployment operation;
- probability calibration is not active.

Current research/control state is documented in:

`docs/checkpoints/2026-09-11_PHASE11G_24H_CONTROL_AND_RUNTIME_HARDENING.md`.
