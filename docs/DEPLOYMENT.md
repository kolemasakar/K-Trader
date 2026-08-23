# Deployment Specification v1.0

## Target

- Private GitHub repository
- Ubuntu VPS
- Docker Engine + Docker Compose
- Self-hosted GitHub Actions runner
- HTTPS reverse proxy / TLS

## Runtime layout

Persistent runtime state SHOULD live outside the runner workspace:

`/opt/k-trader/`
- `app/`
- `data/`
- `config/`
- `logs/`

## CI/CD flow

push/merge to `main`
-> checkout
-> tests
-> docker compose build
-> docker compose up -d --remove-orphans
-> health check
-> status

The scanner itself runs continuously under Docker with `restart: unless-stopped`; GitHub Actions is deployment automation, not the scanner scheduler.

## Network acceptance before provider selection

From the VPS, verify for each candidate provider:
- DNS resolution
- HTTPS public REST access
- public WebSocket handshake/stream
- latency/reliability
- absence of provider access errors

Provider selection must comply with applicable provider terms and regional availability; the infrastructure is not intended to bypass restrictions.

## Runner policy

- Use only with the private repository.
- Production deploy workflow triggers from approved `main` state.
- Do not automatically execute untrusted fork/PR code on the production self-hosted runner.
