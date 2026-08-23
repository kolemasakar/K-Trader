# VPS Provisioning v1.0

## Target

- Ubuntu x86_64 VPS (22.04 LTS or newer; 24.04 LTS preferred).
- Private repository `kolemasakar/K-Trader`.
- Docker Engine + Compose plugin.
- Repository-scoped GitHub Actions self-hosted runner.
- Optional public DNS name for Caddy HTTPS.

K-Trader v1 uses no exchange API credentials.

## 1. Obtain the repository on the VPS

Authenticate to the private repository using an operator-controlled GitHub method. Do not store a personal access token in the repository or shell scripts.

Example after authentication:

```sh
git clone https://github.com/kolemasakar/K-Trader.git
cd K-Trader
```

## 2. Provision Ubuntu and Docker

```sh
sudo ./scripts/provision_vps.sh
```

The script:

- verifies Ubuntu;
- installs Docker from Docker's official Ubuntu repository;
- installs Docker Compose/Buildx plugins;
- enables Docker;
- creates the non-root `ktrader` user;
- creates `/opt/k-trader/{releases,data,caddy_data,caddy_config,runner}`;
- grants the `ktrader` user Docker access.

It deliberately does not alter SSH or firewall policy automatically.

## 3. Register the repository runner

In GitHub repository settings open Actions -> Runners -> New self-hosted runner and obtain a short-lived repository registration token.

Then on the VPS:

```sh
sudo env \
  GITHUB_RUNNER_URL=https://github.com/kolemasakar/K-Trader \
  GITHUB_RUNNER_TOKEN='<short-lived-token>' \
  ./scripts/register_runner.sh
```

The registration script pins GitHub Actions Runner `2.336.0` and verifies the Linux x64 archive using SHA-256:

`04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d`

The installed custom runner label is:

`k-trader-prod`

The runner is installed as a system service under user `ktrader`.

Do not reuse the registration token as an application secret. It is only for runner registration.

## 4. Production GitHub environment

Create/verify GitHub Environment:

`production`

Optional repository/environment variable:

`KTRADER_DOMAIN=api.example.com`

If no domain is configured, deployment keeps the API bound to VPS localhost only. A real HTTPS domain is required before Phase 10 Custom GPT Action activation.

## 5. Network/security checklist

Before enabling UFW, confirm SSH key access in a second session.

Typical public HTTPS deployment needs:

- SSH from trusted administration sources;
- TCP 80 for ACME/redirect;
- TCP 443 for HTTPS;
- UDP 443 only if HTTP/3 is desired.

The K-Trader application port `8000` remains bound to `127.0.0.1` and must not be exposed publicly.

Recommended host controls:

- SSH key authentication;
- disable password/root SSH login where operationally safe;
- automatic security updates or a defined patch routine;
- least-privilege operator accounts;
- no unrelated workloads on the production runner if avoidable.

## 6. First deployment

After the runner is online, start GitHub Action:

`Deploy Production`

It is manual-only and accepts `main` only.

Deployment performs:

1. immutable release build under `/opt/k-trader/releases/<commit-sha>`;
2. Docker Compose start;
3. local process health check;
4. public-provider REST checks on 5m/15m/1h/4h/1d;
5. public 5m WebSocket check;
6. scanner `data_ready` check;
7. API MTF publication check;
8. rollback to the previous release if acceptance fails.

## 7. HTTPS

When `KTRADER_DOMAIN` is non-empty, deployment enables the Caddy `https` profile.

DNS for the domain must already resolve to the VPS and ports 80/443 must be reachable.

Do not replace `https://api.k-trader.invalid` in the Custom GPT OpenAPI file until the real HTTPS endpoint passes Phase 9 acceptance.
