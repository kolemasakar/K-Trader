# Self-service isolated K-Trader research archive access

Owner authorization: 2026-10-01. No KGM dependencies and no HP-OMEN.

## Purpose and boundaries
K-Trader owns its Phase 11G historical archive and may independently repeat research on an approved SHA-256-pinned internal dataset without requesting per-study K_Sentinel approval. SentinelX stays a bounded, separate diagnostic path; **the research job runs as the already-existing host user `ktrader` through the repository-scoped self-hosted K-Trader runner**. No new filesystem ACL or SentinelX sudo permission is needed.

This creates a narrow exception to the prior **production-runner manual-deploy-only** usage policy: an additional *trusted-main-only, bounded research-verification workflow* is authorized. Do not run any research code from pull_request, fork, arbitrary refs, configurable shell expressions, or actions with credentials persisted. The existing production deploy and its approvals are unchanged. Audit other research workflows independently before admitting them to this privileged host runner.

## Fixed source version and outputs
- Host source: `/opt/k-trader/data/research/phase11g/historical_expansion_v1_20260905T144500Z`.
- Container view: `/archive` with enforced Docker bind `readonly`.
- Exact approved version digest: `b7c030bdd71a93a8733574e285b05a8093f23f5efcecd9a4edc5fdde8f914aa6`.
- Provenance: `binance_usdm`, `as_of=2026-09-05T14:45:00Z`, 19 symbol bundles.
- Separate host results: `/opt/k-trader/data/research_results/verified_dataset/<GitHub run ID>/verification.json`.
- No source copying; no archive write, production application modification or production container restart. Inputs and file SHA-256 remain inspectable in the result manifest.

## Self-service entry point
GitHub Actions → **Verified Research Archive (isolated)** → Run workflow on **main**.

First activation is the initial marker `ops/research_requests/2026-10-01_initial_archive_access`, which triggers once when this feature is merged to main. Later manual `workflow_dispatch` runs verify exactly the same approved source version. The job is serialized with `k-trader-production` to prevent overlap with production deployments. A change of source bytes or archive version requires a separately reviewed manifest/digest update; not per-research permission.

The workflow deliberately runs no user-selected command. To add new research methods, provide reviewed source scripts with fixed entry points and documented results, and enforce the same read-only archive and resource-limited sandbox. K-Trader may reuse the accepted version freely once its self-service job passes.

## Security and resource requirements
The verification container:
- uses the already-deployed local K-Trader image; does not pull/build a new image or access paid infrastructure;
- has `--network none`, an immutable root, all Linux capabilities dropped, `no-new-privileges` and an explicit non-root UID:GID;
- bind-mounts *only* the exact archive as read-only, the exact verified script as read-only, and a separate writable result directory;
- is limited to half a CPU, 512 MiB memory/swap, 64 PIDs, 64 MiB temporary RAM and a 10-minute workflow timeout;
- confirms the enforced RO source mount by attempting to open a source manifest for writing without truncation (failure is mandatory);
- verifies per-file SHA-256, deterministic tree digest, symbol count and closed candle counts, then saves a manifest outside the archive.

The existing `ktrader` host user is already in the `docker` group. This is a high-trust deployment identity, **not** a new unprivileged Linux account or an independent security principal. Container isolation bounds *this job's* filesystem access and resource use, but does not deprivilege the host runner itself. Do not run untrusted PR code on that runner.

## Scientific status
`VERIFIED RESEARCH DATASET` refers only to the approved digest/provenance/access version. It is internal development data, not automatically an independent final holdout. Output artifacts must remain separate; no execution or trading-model validation is implied.

## Validation gates
1. Hosted CI + code review must pass before merging this workflow to main.
2. Initial trusted-main one-shot verification workflow must pass on the self-hosted K-Trader runner.
3. Confirm `verification.json` and unaffected production container health.
4. Until step 2 passes, status is `SELF_SERVICE_CONFIGURED / ISOLATED_RUNTIME_PENDING`, not `ISOLATED_RUNTIME_ACCEPTED`.
