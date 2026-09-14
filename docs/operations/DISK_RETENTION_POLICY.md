# K-Trader Disk Retention Policy

Status: APPROVED REQUIREMENT
Date: 2026-09-14

## Trigger

When filesystem usage reaches or exceeds `80%`, automatic cleanup must be considered triggered.

## Cleanup target

Delete the oldest `20%` of eligible historical/temporary data, oldest first.

## Eligible data

Only data explicitly classified as disposable or reproducible may be removed, for example:

- old raw market-history exports that are reproducible from the provider;
- obsolete shadow/replay bundles superseded by later accepted artifacts;
- temporary caches and transient export artifacts;
- non-pinned intermediate research outputs.

## Protected data

The cleanup process must never automatically delete:

- production databases or live runtime state;
- source code, configuration, secrets or deployment metadata;
- canonical documentation and checkpoints;
- accepted/pinned research evidence needed for reproducibility;
- current/latest prospective capture artifacts required by active research;
- holdout data or any artifact whose retention is governed by holdout policy;
- audit trails or manifests required to prove what was previously accepted.

## Safety requirements

Before deletion, cleanup must produce an inventory/manifest containing candidate paths, timestamps and sizes. Deletion must be deterministic, oldest-first and limited to the approved eligible set. If the eligible set is smaller than the requested 20%, delete only the eligible subset and report that the target could not be fully met.

After cleanup, record pre-cleanup and post-cleanup disk usage, deleted byte count, deleted paths/count, and the cleanup manifest hash.

## Current state

At the latest pre-pause check on 2026-09-14, root filesystem usage was `18%`; therefore no cleanup action is currently required.

Implementation of the automatic monitor/cleanup mechanism must follow this policy and remain fail-closed for protected or unclassified data.
