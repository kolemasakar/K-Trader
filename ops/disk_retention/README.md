# K-Trader Disk Retention — Dry-Run v1

Status: **DRY-RUN ONLY / FAIL-CLOSED**

This implementation follows `docs/operations/DISK_RETENTION_POLICY.md` but deliberately contains **no deletion/apply mode**. It only measures disk usage, builds a deterministic oldest-first cleanup plan from an explicit allowlist, and writes a hashed manifest.

## Safety model

- trigger defaults to `80%` filesystem usage;
- target defaults to oldest `20%` of explicitly eligible bytes;
- candidates must resolve below `/data/research`;
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
- `disk-retention.example.json` — fail-closed example configuration;
- `ktrader-disk-retention.service` — hardened oneshot service;
- `ktrader-disk-retention.timer` — hourly timer.

## Validation before installation

Run manually from the repository or an immutable checkout:

```bash
python ops/disk_retention/ktrader_disk_retention.py \
  --config ops/disk_retention/disk-retention.example.json \
  --manifest-dir /tmp/k-trader-retention-validation
```

At normal disk usage below `80%`, expected status is:

`BELOW_TRIGGER_NO_ACTION`

For planner-only testing below the threshold, `--force-plan` is allowed. It still cannot delete data.

## Host installation

Installation requires a bounded root action because the target paths are `/usr/local/sbin`, `/etc/k-trader`, and `/etc/systemd/system`.

Recommended installation mapping:

- planner → `/usr/local/sbin/ktrader-disk-retention`, mode `0755`, owner `root:root`;
- reviewed config → `/etc/k-trader/disk-retention.json`, mode `0644`, owner `root:root`;
- service/timer → `/etc/systemd/system/`, mode `0644`, owner `root:root`.

Then run `systemctl daemon-reload` and enable `ktrader-disk-retention.timer` only after manual dry-run output is reviewed.

The current SentinelX policy intentionally does not grant arbitrary root file installation. Do not broaden general sudo or Docker privileges merely to install this helper; use a bounded owner-side installation action.

## Future apply mode

A destructive/apply mode is **not part of v1**. It requires a separate version, validation against dry-run manifests, explicit approval of the eligible allowlist, and preservation of pre/post cleanup audit evidence.
