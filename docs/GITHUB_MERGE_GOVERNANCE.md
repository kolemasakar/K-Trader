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

Auto-merge may be enabled on a PR, but it does not bypass the ruleset. It completes only after `canonical-merge-gate` succeeds on the up-to-date PR head.

## Completed transition

The repository previously required a status check named `pytest` plus one approving review. The migration was completed in two controlled stages:

1. PR #39 introduced unique Python and Docker jobs plus `canonical-merge-gate`, while retaining the legacy `tests.yml` long enough to satisfy the previous ruleset.
2. After the canonical gate was proven and the ruleset was changed to `0 approvals + canonical-merge-gate`, the legacy `.github/workflows/tests.yml` was removed by the acceptance cleanup PR.

The cleanup PR itself is the end-to-end acceptance test: it must merge without human approval and only after the canonical gate succeeds.

## Routine development path

`feature branch -> pull request -> canonical CI -> canonical-merge-gate -> auto-merge -> main`

No second-account approval is required for routine work.

## Non-goals

- No administrator bypass for routine merges.
- No bot or secondary user performing synthetic approvals.
- No weakening of CI to increase merge speed.
- No direct pushes to protected `main`.

## Emergency changes

Any future bypass capability, if introduced for break-glass recovery, must be documented separately and must not be part of the routine ChatGPT/AI development path.
