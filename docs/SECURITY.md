# Security Specification v1.2

## v1 trust boundary

K-Trader v1 is read-only and uses public exchange market-data APIs only.

Prohibited in v1:
- exchange API secrets
- account access
- order endpoints
- withdrawal/deposit endpoints
- automated execution

## Public K-Trader API

- Production origin: `https://ktrader-api.duckdns.org`.
- HTTPS only when exposed publicly.
- GET/read-only operations only.
- `/health` is public; `/v1/*` requires Bearer authentication when `KTRADER_ACTION_API_KEY` is configured.
- Input validation for symbols/query parameters.
- Rate limiting.
- Bounded response sizes.
- No arbitrary URL fetching from API parameters.
- No shell/command execution surfaces.
- Application port 8000 binds to host loopback only.
- Public ingress terminates at Caddy on 80/443.

## Container baseline

The production K-Trader container runs:

- as a non-root user;
- with read-only root filesystem;
- with all Linux capabilities dropped;
- with `no-new-privileges`;
- with persistent write access only to `/data`;
- with temporary `/tmp` backed by tmpfs.

The Caddy container:

- runs as uid 0;
- drops all capabilities and adds back only `NET_BIND_SERVICE`;
- uses `no-new-privileges`;
- persists TLS/config state through `/data` and `/config` bind mounts;
- requires host `/opt/k-trader/caddy_data` and `/opt/k-trader/caddy_config` to be `root:root` mode `0700` under the current capability-dropped profile.

The ownership requirement exists because uid 0 without `CAP_DAC_OVERRIDE` cannot bypass ordinary DAC write permissions.

## VPS

- Minimal exposed ports.
- SSH key authentication; disable password/root login where operationally safe.
- Confirm SSH access before changing firewall rules.
- Regular OS/container updates.
- `/opt/k-trader/data` is owned by the dedicated `ktrader` runtime/runner user.
- Caddy persistent storage is root-owned as documented above.
- Do not expose port 8000 publicly.
- Production OCI ingress allows TCP 80/443 for HTTPS/ACME.
- Host iptables allows 22/80/443 before a terminal reject; rules are persisted with `netfilter-persistent`.

## GitHub CI and production runner

Trust separation is mandatory:

- pull-request and main validation runs on GitHub-hosted runners;
- production self-hosted runner is manual-deploy only;
- production deploy accepts `main` only;
- self-hosted runner belongs to the private K-Trader repository;
- no untrusted fork/PR code executes on the production runner;
- deployment checkout credentials are not persisted;
- GitHub runner registration token is short-lived and must never be committed;
- runner release archive is checksum-verified before registration;
- `KTRADER_ACTION_API_KEY` is stored only as a GitHub `production` Environment secret and GPT Action authentication value, never in repository files or logs.

Pinned provisioning baseline:

- GitHub Actions Runner `2.336.0` Linux x64;
- SHA-256 `04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d`.

Runner upgrades must retain checksum verification and be validated by the hosted CI gate before production use.

## Release rollback

Production deploy creates immutable commit-SHA release directories.

A new release becomes `current` only after process health plus market/runtime acceptance and, when a public domain is configured, Phase 10 HTTPS/Action acceptance. Failure triggers rollback to the previous release when available.

Phase 10 activation exercised this behavior twice: an authentication-integration defect and a Caddy storage-permission defect both failed closed and rolled back before the final successful deployment.

## Fail-closed rules

Any uncertainty in provider freshness, data integrity, authentication, public HTTPS readiness or engine readiness prevents release promotion or tradable signal output as applicable.

Provider fallback creates a new coherent provider context; it never splices OHLCV series across exchanges.
