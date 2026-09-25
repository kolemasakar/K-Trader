# Phase 11G — approved automatic checks, server-only

**Date:** 2026-09-25; **owner-approved schedule**: hourly, every four hours, final; **reminders explicitly prohibited**.

## Scope

The existing independent K-Trader Oracle Cloud epoch `epoch_20260925T114500Z_v1` is data-only. This monitor must **never** restart the recorder, backfill missed M15 cutoffs, evaluate the candidate, alter trading, open holdout, change the old 54-family ledger, or use HP-OMEN directly or indirectly.

Script: `scripts/phase11g_epoch_monitor_v1.py`, installed as a pinned separate file beside the epoch registration on server storage. One background process only. All diagnostics are server-local `checks` artifacts; **no ChatGPT automations, alerts, push messages or reminders are created**.

## Approved Kyiv / UTC schedule

- **Hourly:** every hour at `:06` Kyiv (`:06` UTC). Starts 25 Sep at 15:06 Kyiv / 12:06 UTC; 24 total checks through 26 Sep 14:06 Kyiv / 11:06 UTC. Only checks still in the future at actual activation are executed; past scheduled checks are separately logged `MISSED_BEFORE_MONITOR_ACTIVATION` and never misrepresented as contemporaneous.
- **Deep:** 25 Sep 18:51 and 22:51 Kyiv; 26 Sep 02:51, 06:51 and 10:51 Kyiv (15:51, 19:51, 23:51, 03:51 and 07:51 UTC). Five checks; validate every first-seen source-file SHA-256 and archive digest, plus all hourly continuity checks.
- **Final:** 26 Sep 14:36 Kyiv / 11:36 UTC, six minutes after the final registered cutoff (11:30 UTC) and after the maximum five-minute capture window. Checks all 96 expected cutoffs, source hashes, original pins, the completed-runner boundary and clean process exit.

The first two hourly opportunities (25 Sep 15:06 and 16:06 Kyiv) had already passed during implementation. They must be *marked missed*; a verified read-only baseline may separately inspect stored data, but cannot retroactively satisfy a missed scheduled event. The first future hourly check depends on the actual monitor start time.

## Checks

- production health `ok`, `read_only`, `data_ready=true`, `binance_usdm`; exactly one independent first-seen recorder during collection;
- all six registered frozen SHA pins: registration, recorder, legacy accepted state/ledger, harness and protocol;
- expected M15 cutoffs (only after their full five-minute first-seen window), immutable manifests and matching event-log manifest SHA-256;
- archived top-19 recorded rank 1..19 without substitution, 95 raw source files per complete cutoff, readiness/failure counts and contextual age;
- most recent four completed cutoffs' raw-source SHA-256 each hourly check; **all** source and archive hashes during five deep checks and the final audit;
- duplicate first-seen events, stale/missing data and any `FAIL_CLOSED` recorder event must fail the monitor check, with durable non-overwriting report;
- monitor failure **only logs findings**. It never stops, restarts or modifies capture.

## Safe activation and acceptance

1. Merge reviewed monitor code and focused safety tests to `research-strategy-benchmark-v1`; require passing existing Research Safety CI and Research Guards.
2. Deploy using a **separate one-shot workflow** on the already-authorized, repository-scoped K-Trader self-hosted runner. Only installed code from exact approved Git SHA may be copied to the running K-Trader Docker container's isolated epoch directory.
3. Workflow checks the approved original SHA pins, installed script SHA, server production read-only mode, exactly one running data recorder, absence of an existing monitor and absence of the checks directory, then runs `--self-test` and read-only `--baseline` and activates `--run` in detached mode. No privilege changes for SentinelX.
4. Verify a single running monitor, immutable baseline PASS, and creation of future scheduled reports. Do **not** call it fully operational until at least one *new* scheduled check is observed and hashes pass.
5. Confirm no notifications/reminders and unchanged original 54/100.

Any failure remains `FAIL_CLOSED`/not activated until investigated. **A successful GitHub Actions job alone does not prove later scheduled checks ran.** The bounded monitor is not automatically restarted if the Docker container restarts.
