# Security Specification v1.1

## v1 trust boundary

K-Trader v1 is read-only and uses public exchange market-data APIs only.

Prohibited in v1:
- exchange API secrets
- account access
- order endpoints
- withdrawal/deposit endpoints
- automated execution

## Public K-Trader API

- HTTPS only when exposed publicly.
- GET/read-only operations only.
- Input validation for symbols/query parameters.
- Rate limiting.
- Bounded response sizes.
- No arbitrary URL fetching from API parameters.
- No shell/command execution surfaces.
- Application port 8000 binds to host loopback only.

## Container baseline

The production K-Trader container runs:

- as a non-root user;
- with read-only root filesystem;
- with all Linux capabilities dropped;
- with `no-new-privileges`;
- with persistent write access only to `/data`;
- with temporary `/tmp` backed by tmpfs.

## VPS

- Minimal exposed ports.
- SSH key authentication; disable password/root login where operationally safe.
- Confirm SSH access before changing firewall rules.
- Regular OS/container updates.
- Persistent `/opt/k-trader` directories owned by the dedicated runtime/runner user.
- Do not expose port 8000 publicly.
- Use DNS + Caddy TLS before enabling Custom GPT Action access.

## GitHub CI and production runner

Trust separation is mandatory:

- pull-request and main validation runs on GitHub-hosted runners;
- production self-hosted runner is manual-deploy only;
- production deploy accepts `main` only;
- self-hosted runner belongs to the private K-Trader repository;
- no untrusted fork/PR code executes on the production runner;
- deployment checkout credentials are not persisted;
- GitHub runner registration token is short-lived and must never be committed;
- runner release archive is checksum-verified before registration.

Pinned provisioning baseline:

- GitHub Actions Runner `2.336.0` Linux x64;
- SHA-256 `04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d`.

Runner upgrades must retain checksum verification and be validated by the hosted CI gate before production use.

## Release rollback

Production deploy creates immutable commit-SHA release directories.

A new release becomes `current` only after process health plus market/runtime acceptance. Failure triggers rollback to the previous release when available.

## Fail-closed rules

Any uncertainty in provider freshness, data integrity or engine readiness prevents tradable signal output.

Provider fallback creates a new coherent provider context; it never splices OHLCV series across exchanges.
