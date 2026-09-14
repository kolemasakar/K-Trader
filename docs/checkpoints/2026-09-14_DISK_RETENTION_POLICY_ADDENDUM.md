# K-Trader — Disk Retention Policy Addendum

Date: 2026-09-14
Status: APPROVED REQUIREMENT

Operational correction:

- trigger cleanup when filesystem usage reaches `80%`;
- delete the oldest `20%` of eligible historical/temporary data, oldest first;
- never automatically delete production DB/runtime state, source/config, canonical docs/checkpoints, pinned accepted evidence, active/latest research artifacts, holdout data, or audit manifests;
- cleanup must be fail-closed for unclassified data and must record a deletion manifest plus before/after disk usage.

Canonical policy: `docs/operations/DISK_RETENTION_POLICY.md`.

Latest observed root filesystem usage before this policy was added: `18%`; no cleanup is currently required.
