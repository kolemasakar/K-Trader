# VPS Provisioning v1.4

## Target

Primary production target for K-Trader v1:

- Oracle Cloud Always Free Ampere A1;
- Germany Central (Frankfurt) home region;
- Ubuntu 24.04 LTS Minimal aarch64;
- `VM.Standard.A1.Flex`;
- active production allocation: 1 OCPU / 6 GB RAM;
- Docker Engine + Compose plugin;
- repository-scoped GitHub Actions self-hosted runner on Linux ARM64;
- public DNS name for Caddy HTTPS.

The deployment tooling also keeps Linux amd64 compatibility as a fallback path. K-Trader v1 uses no exchange API credentials.

## Current verified production host

Phase 10 public HTTPS deployment was verified on 2026-09-05.

```text
Name: k-trader-prod
Region: Germany Central (Frankfurt)
Image: Canonical Ubuntu 24.04 Minimal aarch64
Shape: VM.Standard.A1.Flex
OCPU: 1
Memory: 6 GB
Public IPv4: 92.5.56.198
Public DNS: ktrader-api.duckdns.org
Runner label: k-trader-prod-arm64
Deployment run: 33945690930 (Deploy Production #4, successful re-run)
Deployed SHA: 7c60a77b9773774373ea4a3f095c5ab2ee7767e2
```

The application remains local at `127.0.0.1:8000`; Caddy exposes only the HTTPS reverse-proxy path on 80/443.

## 1. Oracle instance baseline

Use only resources explicitly marked Always Free-eligible in the OCI console.

Canonical VM baseline matching the active production host:

```text
Name: k-trader-prod
Region: Germany Central (Frankfurt)
Image: Canonical Ubuntu 24.04 Minimal aarch64
Shape: VM.Standard.A1.Flex
OCPU: 1
Memory: 6 GB
Capacity: on-demand
Fault domain: let Oracle choose
```

Networking target:

```text
VCN: k-trader-vcn
Public subnet: k-trader-public-subnet
Private IPv4: automatic
Public IPv4: required before SSH/public deployment
IPv6: optional; not required in v1
```

Use SSH public-key authentication. Never commit or upload the private SSH key to this repository.

If OCI reports `Out of capacity` for A1, do not switch to a non-Always-Free shape without an explicit architecture/cost decision. Historical capacity shortage on 2026-08-23 was later resolved and the production A1 instance was provisioned successfully.

## 2. Obtain the repository on the host

Authenticate to the private repository using an operator-controlled GitHub method. Do not store a personal access token in the repository or shell scripts.

Example after authentication:

```sh
git clone https://github.com/kolemasakar/K-Trader.git
cd K-Trader
```

## 3. Provision Ubuntu and Docker

```sh
sudo ./scripts/provision_vps.sh
```

The script:

- verifies Ubuntu;
- accepts Ubuntu `arm64` and `amd64` only;
- installs Docker from Docker's official Ubuntu repository for the detected architecture;
- installs Docker Compose/Buildx plugins;
- enables Docker;
- creates the non-root `ktrader` user;
- creates `/opt/k-trader/{releases,data,caddy_data,caddy_config,runner}`;
- grants the `ktrader` user Docker access;
- creates application data as `ktrader`-owned;
- creates Caddy persistent storage as `root:root` mode `0700`.

It deliberately does not alter SSH or firewall policy automatically.

The host `ktrader` user must own the persistent K-Trader data tree before normal production deployment. Current verified production ownership is:

```text
/opt/k-trader/data -> uid:gid 1002:1002, owner ktrader:ktrader, mode 750
```

The numeric identity is host-specific. Do not treat `1002` as a universal constant. `scripts/deploy.sh` derives the production runtime UID/GID dynamically from the self-hosted runner user and builds the K-Trader container with matching ownership.

Caddy uses a separate storage ownership contract:

```text
/opt/k-trader/caddy_data   -> root:root, mode 700
/opt/k-trader/caddy_config -> root:root, mode 700
```

The Caddy container starts as uid 0 but drops all Linux capabilities except `NET_BIND_SERVICE`. With `CAP_DAC_OVERRIDE` absent, uid 0 must own `/data` and `/config` to persist ACME certificates and autosave configuration through ordinary DAC permissions. Do not change these directories to `ktrader:ktrader` under the current security profile.

## 4. Register the repository runner

In GitHub repository settings open Actions -> Runners -> New self-hosted runner and obtain a short-lived repository registration token.

Then on the host:

```sh
sudo env \
  GITHUB_RUNNER_URL=https://github.com/kolemasakar/K-Trader \
  GITHUB_RUNNER_TOKEN='<short-lived-token>' \
  ./scripts/register_runner.sh
```

The registration script pins GitHub Actions Runner `2.336.0`; the runner may auto-update after registration. The active production runner reported version `2.337.0` during production deployment. The script auto-detects the host architecture and verifies the official release archive SHA-256.

Checksums:

```text
linux-x64:
04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d

linux-arm64:
58b758e420b87093fbd4bfddd368074960053e2f1388f01848c82624b90f27d1
```

Custom labels:

```text
all production hosts: k-trader-prod
Oracle ARM64 host:     k-trader-prod-arm64
amd64 fallback host:   k-trader-prod-x64
```

The current production workflow intentionally targets `k-trader-prod-arm64` because Oracle A1 is the primary hosting plan.

The runner is installed as a system service under user `ktrader`.

Do not reuse the registration token as an application secret. It is only for runner registration.

## 5. Production GitHub environment

Create/verify GitHub Environment:

`production`

Current public production configuration:

- Environment variable: `KTRADER_DOMAIN=ktrader-api.duckdns.org`;
- Environment secret: `KTRADER_ACTION_API_KEY=<high-entropy secret>`.

Do not commit the Action API key. The same secret is configured later as the Bearer API key in the GPT Action. The secret value is intentionally absent from repository files and checkpoints.

If no domain is configured, deployment keeps the API bound to host localhost only. A real HTTPS domain is required for Custom GPT Action activation.

## 6. Network/security checklist

Before changing firewall rules, confirm SSH key access in a second session.

Current verified public production ingress:

- OCI stateful TCP 22 for SSH;
- OCI stateful TCP 80 for ACME/redirect;
- OCI stateful TCP 443 for HTTPS;
- host iptables explicitly allows TCP 22/80/443 before the terminal reject;
- host rules are persisted with `netfilter-persistent`.

The K-Trader application port `8000` remains bound to `127.0.0.1` and must not be exposed publicly.

UDP 443 is published by the Caddy Compose service for HTTP/3; OCI UDP exposure is optional because HTTP/1.1 and HTTP/2 over TCP 443 are sufficient for the Action path.

Recommended host controls:

- SSH key authentication;
- disable password/root SSH login where operationally safe;
- automatic security updates or a defined patch routine;
- least-privilege operator accounts;
- no unrelated workloads on the production runner if avoidable.

## 7. Production deployment

After the ARM64 runner is online, start GitHub Action:

`Deploy Production`

It is manual-only and accepts `main` only.

Deployment performs:

1. immutable release build under `/opt/k-trader/releases/<commit-sha>`;
2. derive runner-user UID/GID and verify `/opt/k-trader/data` is writable;
3. native ARM64 Docker Compose build/start with matching K-Trader container runtime identity;
4. local process health check;
5. public-provider REST checks on 5m/15m/1h/4h/1d;
6. public 5m WebSocket check;
7. scanner `data_ready` check;
8. API MTF publication check;
9. if `KTRADER_DOMAIN` is configured, wait for public HTTPS and run Phase 10 Action acceptance;
10. mark the release current only after all required acceptance checks pass;
11. rollback to the previous release if any required acceptance check fails.

Verified Phase 10 production result on 2026-09-05:

```text
GitHub Actions: Deploy Production #4, run 33945690930, successful re-run
Release: 7c60a77b9773774373ea4a3f095c5ab2ee7767e2
Runtime uid:gid: 1002:1002
Provider acceptance: binance_usdm PASS
REST intervals: 5m,15m,1h,4h,1d
WebSocket: 5m PASS
Scanner: DEGRADED, data_ready=true, symbols_ready=17, symbols_failed=3
MTF API: PASS on all five canonical intervals
Docker: healthy
HTTPS: PASS
Phase 10 Action live acceptance: PASS
Public origin: https://ktrader-api.duckdns.org
```

`DEGRADED` scanner state is allowed when usable canonical data remains ready and fresh; per-symbol failures are isolated rather than forcing the entire service offline.

## 8. HTTPS and Custom GPT Action

When `KTRADER_DOMAIN` is non-empty, deployment enables the Caddy `https` profile.

Current DNS:

`ktrader-api.duckdns.org -> 92.5.56.198`

Caddy automatically obtained a Let's Encrypt certificate by HTTP-01 after the persistent storage ownership was corrected. Certificate and ACME account state persist under `/opt/k-trader/caddy_data`.

`scripts/phase10_action_acceptance.py` verifies the public HTTPS origin, read-only mode, scanner readiness, authentication behavior, and required Action response fields.

The accepted canonical production OpenAPI origin is now `https://ktrader-api.duckdns.org`. `custom_gpt/openapi.yaml` may be imported into the GPT Action after configuring Bearer API-key authentication.

Detailed activation and incident evidence is recorded in `docs/PHASE_10_CHECKPOINT.md`.
