# K-Trader GitHub Merge Governance

Updated: 2026-09-09
Status: ACTIVE / CANONICAL MERGE GATE ENFORCED

## Objective

K-Trader uses pull requests and deterministic CI as the canonical merge authority. Routine merges do not depend on ceremonial approval by a second account controlled by the same operator.

## Canonical policy

Every change to `main` must:

1. arrive through a pull request;
2. be evaluated against the latest `main` (`strict` status-check policy);
3. pass the canonical CI gate;
4. use squash merge and preserve linear history;
5. remain protected from deletion and non-fast-forward updates.

Routine human approval count is zero.

## Canonical CI gate

The required merge authority is the GitHub Actions check named:

`canonical-merge-gate`

It succeeds only if all mandatory jobs succeed:

- `pytest-py312`
- `pytest-py314`
- `docker-amd64`
- `docker-arm64`

The gate uses `if: always()` and explicitly asserts that every dependency result is `success`. Therefore failed, cancelled, or skipped mandatory jobs make the canonical gate fail closed.

## Repository ruleset

The active `main` ruleset requires:

- pull requests before merging;
- required approving reviews: `0`;
- required status check: `canonical-merge-gate`;
- strict up-to-date status checks;
- squash merge only;
- linear history;
- deletion protection;
- non-fast-forward / force-push protection.

## Merge execution

The ruleset and `canonical-merge-gate` are the merge authority. The mechanism that performs the final squash is secondary.

Preferred path:

`feature branch -> pull request -> canonical CI -> canonical-merge-gate -> native auto-merge -> main`

Deterministic fallback:

`feature branch -> pull request -> canonical CI -> canonical-merge-gate -> connector-triggered squash merge -> main`

The connector-triggered merge must:

- run only after `canonical-merge-gate` is `success`;
- use squash merge;
- pin the expected PR head SHA;
- rely on GitHub to enforce the active ruleset;
- never use an administrator or ruleset bypass for routine work.

A connector merge request is therefore not a substitute for CI. If a required rule is not satisfied, GitHub must reject the merge.

## Completed transition

The repository previously required a status check named `pytest` plus one approving review. The migration was completed in controlled stages:

1. PR #39 introduced unique Python and Docker jobs plus `canonical-merge-gate`, while retaining the legacy `tests.yml` long enough to satisfy the previous ruleset.
2. The `main` ruleset was changed to `0 approvals + canonical-merge-gate`, with strict up-to-date checks retained.
3. PR #40 removed the transitional `.github/workflows/tests.yml` with no requested reviewer and no approving review.
4. On PR #40, native auto-squash was enabled and the canonical gate succeeded. GitHub reported the PR as clean and mergeable but did not complete native auto-merge within the observed acceptance interval. The connector then issued a squash merge pinned to the exact head SHA after the gate was green; GitHub accepted it under the active ruleset.

This proves the operational requirement: routine development no longer depends on the `Lingvorm` approval workaround, while the canonical CI gate remains mandatory.

## Routine development path

For every routine PR:

1. create/update a feature branch;
2. open a PR to `main`;
3. wait for `canonical-merge-gate`;
4. if the gate fails, do not merge;
5. if the gate succeeds, prefer native auto-merge;
6. if native auto-merge does not complete despite an enabled auto-merge state and a clean, up-to-date PR, use connector-triggered squash merge pinned to the expected head SHA.

No second-account approval is required for routine work.

## Non-goals

- No administrator bypass for routine merges.
- No bot or secondary user performing synthetic approvals.
- No weakening of CI to increase merge speed.
- No direct pushes to protected `main`.

## Emergency changes

Any future bypass capability, if introduced for break-glass recovery, must be documented separately and must not be part of the routine ChatGPT/AI development path.
