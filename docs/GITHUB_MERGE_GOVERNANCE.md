# K-Trader GitHub Merge Governance

Updated: 2026-09-09

## Objective

K-Trader uses pull requests and deterministic CI as the canonical merge authority. Routine merges must not depend on ceremonial approval by a second account controlled by the same operator.

## Target policy

Every change to `main` must:

1. arrive through a pull request;
2. be evaluated against the latest `main` (`strict` status-check policy);
3. pass the canonical CI gate;
4. use squash merge and preserve linear history;
5. remain protected from deletion and non-fast-forward updates.

Routine human approval count is zero after the canonical gate is proven and made required.

## Canonical CI gate

The required merge authority is the check named:

`canonical-merge-gate`

It succeeds only if all mandatory jobs succeed:

- `pytest-py312`
- `pytest-py314`
- `docker-amd64`
- `docker-arm64`

The gate uses `if: always()` and explicitly asserts that every dependency result is `success`. Therefore failed, cancelled, or skipped mandatory jobs make the canonical gate fail closed.

## Transition sequence

The repository originally required a status check named `pytest` plus one approving review. During bootstrap of the new governance model, `.github/workflows/tests.yml` remains temporarily present so the existing `pytest` requirement can still be satisfied while the new canonical gate is introduced and validated.

After the foundation PR is merged and the canonical gate is observed succeeding on `main`, the repository ruleset should change atomically from:

- required approvals: `1`
- required status check: `pytest`

to:

- required approvals: `0`
- required status check: `canonical-merge-gate`

After that ruleset change, a follow-up cleanup PR removes the transitional `.github/workflows/tests.yml`. That cleanup PR must be auto-merged without human approval only after `canonical-merge-gate` succeeds, proving the target governance path end to end.

## Non-goals

- No administrator bypass for routine merges.
- No bot or secondary user performing synthetic approvals.
- No weakening of CI to increase merge speed.
- No direct pushes to protected `main`.

## Emergency changes

Any future bypass capability, if introduced for break-glass recovery, must be documented separately and must not be part of the routine ChatGPT/AI development path.
