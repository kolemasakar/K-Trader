# SentinelX Remote Operator Access

Updated: 2026-09-09

## Purpose

SentinelX provides a direct, policy-constrained management channel from ChatGPT to the K-Trader production VM (`k-trader-prod-vnic`) without requiring the operator to copy every command through an interactive SSH session.

The channel is intended for production diagnostics, read-only inspection, controlled command/script execution, container health checks, selected service operations, repository/release inspection, and other explicitly permitted K-Trader maintenance tasks.

SSH remains the out-of-band recovery and bootstrap path. SentinelX is not a replacement for the production deployment workflow or GitHub Actions.

## Connection identity

- Host: `k-trader-prod-vnic`.
- Platform: Oracle Cloud Ampere A1 / Ubuntu 24.04 / ARM64 (`aarch64`).
- SentinelX agent: `sentinelx-cloud-core`.
- Agent version at acceptance: `0.11.18`.
- SentinelX host id: `host_8c63c46648154724`.
- Transport: outbound connection from the VM to the SentinelX hub; no dedicated inbound management port is required.
- ChatGPT connector: SentinelX MCP integration.

The direct channel was accepted on 2026-09-09 by successfully executing code on the VM and verifying host identity, container state, application health, and policy enforcement.

## Available capabilities

Within the configured SentinelX policy, ChatGPT can perform operations including:

- execute allowlisted shell commands;
- run one-off Bash or Python scripts as the unprivileged `sentinelx` service user;
- inspect selected files and directories;
- inspect K-Trader release and persistent-data paths;
- inspect Docker containers and K-Trader application health;
- execute approved commands inside the `k-trader-ktrader-1` container;
- inspect selected systemd service state and restart explicitly approved services;
- inspect logs covered by the policy;
- use SentinelX structured Git/filesystem operations where the configured path policy permits them.

The current production deployment itself remains GitHub-driven. Canonical source repository: `kolemasakar/K-Trader`, branch `main`.

## Security boundary

The initial SentinelX installer configuration granted unrestricted passwordless sudo. That bootstrap configuration was hardened on 2026-09-09.

Current principles:

- `sentinelx` is a dedicated unprivileged Linux user;
- unrestricted `NOPASSWD: ALL` is not permitted;
- sudo is restricted to a narrow set of approved K-Trader/SentinelX operational commands;
- arbitrary root commands are denied;
- SentinelX must not be allowed to rewrite its own policy file as a normal operating capability;
- structured filesystem access is read-only and intentionally narrow;
- no general writable filesystem subtree is exposed to SentinelX;
- sensitive credentials are excluded from the file-read policy.

Explicitly excluded from structured file access include:

- `/etc/sentinelx/identity.json`;
- `/opt/k-trader/runner/.credentials`.

Current structured readable K-Trader paths are limited to:

- `/opt/k-trader/releases`;
- `/opt/k-trader/data`.

`writable_paths` is empty.

## Approved privileged operations

The hardened sudo policy preserves only the privileged operations required for routine K-Trader diagnostics and SentinelX continuity. These include controlled operations for:

- the `sentinelx-cloud-core` systemd service;
- Docker daemon status/restart;
- selected SentinelX/Docker journal inspection;
- Docker inspection/diagnostics for the K-Trader production containers;
- `docker exec` into `k-trader-ktrader-1` for approved operational diagnostics.

A control test after hardening confirmed that a generic root operation such as `sudo /usr/bin/id` is denied while approved Docker and SentinelX systemd operations continue to work.

## Operational rules

- Prefer read-only inspection before mutation.
- Do not use SentinelX to bypass GitHub pull-request, CI, or production deployment controls.
- Do not expose GitHub runner credentials, SentinelX identity credentials, API keys, private keys, or other secrets through the connector.
- Do not broaden sudo, command, service, or filesystem policy unless a concrete maintenance requirement exists.
- Keep `/etc/sentinelx/config.yaml` outside SentinelX writable paths.
- Use SSH as the recovery path if SentinelX is offline, its policy is invalid, or the agent cannot reconnect.
- Changes that affect application source, deployment manifests, or canonical project documentation should be committed to GitHub rather than edited only on the production host.

## Recovery artifacts

Hardening created operator-side backup copies before policy replacement:

- `/etc/sentinelx/config.yaml.bak.20260909T075619Z`;
- `/etc/sudoers.d/sentinelx.bak.20260909T075619Z`.

These are recovery artifacts on the VM and must not be treated as canonical project configuration.

## Relationship to production layout

`/opt/k-trader` is a deployment root, not the canonical Git working tree. Production uses immutable release directories under `/opt/k-trader/releases/<commit-sha>` and the `current` symlink.

Canonical code and documentation remain in GitHub. SentinelX is an operational access path to the deployed environment, not a source-of-truth repository.