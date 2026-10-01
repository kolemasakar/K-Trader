# K-Trader own-archive research launch (bounded, read-only)

Date: 2026-10-01. Scope: K-Trader only; defer KGM. This launcher implements the owner's self-service source access without duplicating the 81-MiB archive or broadening SentinelX's host access.

## Prerequisites
Run **as the existing unprivileged `ktrader` user** in an environment with Python and Linux Landlock support, including the K-Trader container image after an approved deployment. Production container already exposes the source at:
`/data/research/phase11g/historical_expansion_v1_20260905T144500Z`.

Create a **separate, ktrader-owned results directory** before launch (not inside the source archive), via the already approved release/deployment path. Do not use production database/output directories as the research results destination. Do not modify the source archive's existing permissions.

## Example
```sh
python3 scripts/run_readonly_research.py \
  --results /data/research/isolated_results/<study_id> \
  --memory-mib 512 --cpu-seconds 30 --wall-seconds 60 \
  --self-test
```

The launcher checks paths, sets child per-process virtual-memory, CPU-time and output-file limits, applies `no_new_privs` and Linux Landlock with write allowance only for results and `/tmp`, then launches a child. Fail closed when Landlock fails. It passes `KTRADER_RESEARCH_ARCHIVE` and `KTRADER_RESEARCH_RESULTS` to the child. Store all research results outside the source, labelled with dataset SHA-256 and code/config identity.

## Security/operations boundary
- A verified one-off Landlock smoke was performed on the current K-Trader container as UID 1002: reading the archive passed; opening the original source for write was denied. Per-process RLIMIT_AS=512 MiB, RLIMIT_CPU=15 s and RLIMIT_FSIZE=32 MiB also tested. No production restarts or source mutations.
- This reusable repository launcher is **not a separate container, network sandbox, cumulative process-tree resource cgroup, or defense against deliberate malicious-user bypass**. Production container has an existing writable `/data` mount, so its other processes do not inherit these restrictions. A child can read other paths accessible to its account; protect secrets through a future separately isolated research container if that threat model changes.
- For hard container-level `:ro`, `--network none`, `--memory`, `--cpus` and `--pids-limit`, a distinct research container and bounded owner-governed startup path must be separately accepted. This repository change does not claim that step was performed.
- Per-process resource limits do not reserve RAM/CPU and do not prevent subprocess resource aggregation. Use conservative limits and schedule low priority to avoid interfering with live workloads.
- Standing owner permission to use verified research data does **not** authorize deployment changes or trading execution.
- A source-based verified dataset is internal research material, not an automatic independent out-of-sample control cohort.

Full source-version policy: `docs/VERIFIED_RESEARCH_DATASET_POLICY_2026-10-01.md`.
