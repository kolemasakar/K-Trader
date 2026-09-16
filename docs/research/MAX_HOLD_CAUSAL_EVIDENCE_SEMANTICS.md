# Max-Hold Causal Evidence Semantics

Status: **CLARIFIED / NO STRATEGY CHANGE**

Date: 2026-09-16

## Frozen v2.2 execution semantics

The frozen v2.2 backtest holds a position through `MAX_HOLD_BARS = 32` M15 bars.

After the 32nd held bar is processed, the harness sets `pending_exit=True` and executes `TIME_EXIT` at the **open of the next M15 bar**.

Therefore accepted TIME_EXIT records report `hold_bars=33` when counting the entry-indexed bar sequence used by the implementation. This is consistent with the frozen harness and does not mean the configured holding horizon was increased.

## Prospective resolver semantics

Prospective evidence uses closed-bar-only bundles.

The resolver can only confirm the next-bar open used for TIME_EXIT after that next bar itself is present in a closed-bar bundle. Therefore TIME_EXIT evidence becomes resolvable one M15 evidence interval after the actual frozen-harness exit timestamp.

Example:

- entry `08:00Z`;
- frozen 32-bar holding completes through the `15:45Z` bar;
- strategy TIME_EXIT price/time = `16:00Z` next-bar open;
- closed-bar prospective resolver confirms that exit at an as-of cutoff of `16:15Z` or later.

For entry `08:15Z`:

- strategy TIME_EXIT price/time = `16:15Z`;
- prospective closed-bar confirmation becomes available at `16:30Z` or later.

## Interpretation

This is an **evidence-lag**, not an extra trading hold.

Do not describe the prospective confirmation cutoff as the strategy's exit timestamp.

Always distinguish:

- `strategy_exit_time` — next-bar open after the 32 held bars;
- `earliest_closed_bar_evidence_cutoff` — first as-of where the resolver can causally verify that next-bar open using the closed-bar bundle.

## Validation

At as-of `2026-09-16T16:15:00Z`:

- SUIUSDT SHORT entry `08:00Z` resolved `TIME_EXIT` with exit time `16:00Z`, `hold_bars=33`;
- XRPUSDT SHORT entry `08:00Z` resolved `TIME_EXIT` with exit time `16:00Z`, `hold_bars=33`;
- ADAUSDT/DOGEUSDT entries `08:15Z` remained unresolved because their strategy TIME_EXIT is `16:15Z` and closed-bar confirmation requires the later `16:30Z` cutoff.

No RR, stop, target, max-hold setting or frozen-v2.2 rule changed.
