# K-Trader Disk Retention — Dry-Run v1

Status: **DRY-RUN ONLY / FAIL-CLOSED**

This implementation follows `docs/operations/DISK_RETENTION_POLICY.md` and deliberately contains **no deletion/apply mode**. It measures disk usage, builds a deterministic oldest-first cleanup plan from an explicit allowlist, and writes a hashed manifest.

## Safety model

- trigger defaults to `80%` filesystem usage;
- target defaults to oldest `20%` of explicitly eligible bytes;
- candidates must resolve below the configured `--allowed-base`;
- symlink candidates and symlinks inside a candidate fail closed;
- overlapping candidates fail closed;
- any path containing `holdout` is protected;
- configured protected paths/globs are excluded;
- the newest path for configured prospective globs may be protected automatically;
- no path is eligible unless it matches `eligible_globs`;
- the shipped example config has `eligible_globs=[]`;
- the planner never deletes files.

## Files

- `ktrader_disk_retention.py` — dry-run planner;
- `disk-retention.example.json` — fail-closed generic example configuration;
- `disk-retention.production.k-trader-prod-vnic.json` — reviewed production dry-run allowlist for `k-trader-prod-vnic`;
- `ktrader-disk-retention.service` — hardened production-host oneshot service;
- `ktrader-disk-retention.timer` — hourly timer.

## Production data path

The running container exposes `/data` from the host bind mount `/opt/k-trader/data`. Therefore the host-side planner must use:

`/opt/k-trader/data/research`

as its allowed base. The service unit passes this path explicitly and grants it read-only access.

The production dry-run configuration currently makes eligible only direct symbol bundle directories below two explicitly superseded/reproducible historical datasets:

- `historical_expansion_v1_20260905T144500Z/bundles/*`;
- `historical_robustness_v1_20260905T144500Z/bundles/*`.

Results, summaries, funding artifacts, `strategy_benchmark_v1`, all prospective/shadow captures, prospective-control data, profile research data, pre-pause evidence and anything matching `holdout` remain outside the eligible set or are explicitly protected.

## Validation before installation

Generic fail-closed validation from a repository checkout:

```bash
python ops/disk_retention/ktrader_disk_retention.py \
  --config ops/disk_retention/disk-retention.example.json \
  --manifest-dir /tmp/k-trader-retention-validation
```

At normal disk usage below `80%`, expected status is:

`BELOW_TRIGGER_NO_ACTION`

For planner-only testing below the threshold, `--force-plan` is allowed. It still cannot delete data.

The production-equivalent configuration was validated against the mounted research tree on 2026-09-16: disk usage was about `19%`, `38` eligible symbol-bundle candidates were discovered, and an oldest-first forced plan selected `20` candidates totaling about `97 MB`. No deletion occurred.

## Host installation

Installation requires a bounded owner/root action because the targets are `/usr/local/sbin`, `/etc/k-trader`, and `/etc/systemd/system`.

Install mapping:

- planner → `/usr/local/sbin/ktrader-disk-retention`, mode `0755`, owner `root:root`;
- `disk-retention.production.k-trader-prod-vnic.json` → `/etc/k-trader/disk-retention.json`, mode `0644`, owner `root:root`;
- service/timer → `/etc/systemd/system/`, mode `0644`, owner `root:root`.

After copying, run `systemctl daemon-reload`, execute the oneshot manually once, inspect its manifest under `/var/lib/k-trader-disk-retention`, and only then enable `ktrader-disk-retention.timer`.

The current SentinelX policy intentionally does not grant arbitrary root file installation. Do **not** broaden general sudo or Docker privileges merely to install this helper; use a bounded owner-side installation action.

## Future apply mode

A destructive/apply mode is **not part of v1**. It requires a separate version, validation against dry-run manifests, explicit approval of the eligible allowlist, and preservation of pre/post cleanup audit evidence.
