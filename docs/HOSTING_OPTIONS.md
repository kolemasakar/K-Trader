# Hosting Options v1.0

## Primary production path

Oracle Cloud Always Free is the primary hosting plan for K-Trader v1.

Target:

```text
Oracle Cloud
Germany Central (Frankfurt)
VM.Standard.A1.Flex
Ubuntu 24.04 Minimal aarch64
2 OCPU / 12 GB RAM target
Docker + self-hosted GitHub runner + K-Trader runtime
```

As of 2026-08-23, OCI returned `Out of capacity` for `VM.Standard.A1.Flex` in Frankfurt AD-1, AD-2, and AD-3, including a reduced 1 OCPU / 6 GB request. This is an external capacity blocker, not a repository defect.

Do not switch to a non-Always-Free shape merely to bypass capacity.

## Potential fallback - not implemented

Home Windows PC + Tailscale Funnel is retained as a potential fallback plan.

Possible future topology:

```text
Home Windows PC
-> Docker/Python K-Trader
-> persistent local SQLite
-> Tailscale Funnel HTTPS
-> Custom GPT Action
```

Status: design option only. No implementation work is approved at this time.

The repository keeps Linux amd64 Docker/runner compatibility so an amd64 host can remain a future fallback path.

## Future-project architecture idea - not for K-Trader v1

Cloudflare Workers + Durable Objects is intentionally not part of the current K-Trader implementation.

It may be evaluated for future projects that are designed around a serverless/edge runtime from the beginning. Migrating K-Trader v1 to that model would require a substantially different runtime architecture and is not planned.
