# Hosting Options v1.1

## Primary production path

Oracle Cloud Always Free is the active primary hosting path for K-Trader v1.

Verified production host:

```text
Oracle Cloud
Germany Central (Frankfurt)
VM.Standard.A1.Flex
Ubuntu 24.04 Minimal aarch64
1 OCPU / 6 GB RAM
Docker + self-hosted GitHub runner + K-Trader runtime
```

Production status on 2026-09-04:

- Oracle A1 VM `k-trader-prod` is running;
- repository-scoped ARM64 GitHub Actions runner is active;
- production deployment run `33920829993` completed successfully;
- deployed SHA `9ed572349ed0195e518f128894a1f187419dbcc1`;
- target-host REST/WebSocket/scanner/MTF acceptance passed;
- Docker runtime is healthy;
- API remains bound to `127.0.0.1:8000` pending Phase 10 public HTTPS activation.

Historical note: on 2026-08-23 OCI returned `Out of capacity` for `VM.Standard.A1.Flex` in Frankfurt AD-1, AD-2 and AD-3, including a reduced 1 OCPU / 6 GB request. This external blocker later cleared and no paid shape was required.

## Potential fallback - not implemented

Home Windows PC + Tailscale Funnel is retained only as a potential fallback plan.

Possible future topology:

```text
Home Windows PC
-> Docker/Python K-Trader
-> persistent local SQLite
-> Tailscale Funnel HTTPS
-> Custom GPT Action
```

Status: design option only. No implementation work is approved at this time because Oracle ARM64 production is operational.

The repository keeps Linux amd64 Docker/runner compatibility so an amd64 host can remain a future fallback path.

## Future-project architecture idea - not for K-Trader v1

Cloudflare Workers + Durable Objects is intentionally not part of the current K-Trader implementation.

It may be evaluated for future projects that are designed around a serverless/edge runtime from the beginning. Migrating K-Trader v1 to that model would require a substantially different runtime architecture and is not planned.
