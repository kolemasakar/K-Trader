# K-Trader Phase 11G — Two-Chain Dataset Expansion Checkpoint

Date: 2026-09-07

Status: COMPLETE / VERIFIED / CATALOGUED / HANDOFF-READY.

## Purpose

This checkpoint records the project state after the second independent provider-recorded Phase 11G production evidence chain was materialized, replayed, registered and verified on the production host.

It is a documentation/recovery checkpoint. It does not change Trading Engine setup discovery, RR, ATR-used, VSA/Trap, scoring, grading, signal eligibility, provider semantics, Action behavior or read-only runtime behavior.

## Repository and production baseline

- repository: `kolemasakar/K-Trader`;
- default branch: `main`;
- repository HEAD before this documentation checkpoint: `40cee9b17aa74ad45be1894d566ddb79f8a81ef4`;
- that commit is the docs-only squash merge of PR #30, recording the first Phase 11G production evidence chain;
- post-merge Tests run `34144783877`: PASS;
- post-merge CI run `34144783943`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS;
- deployed production runtime SHA remains `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- Deploy Production #7 run `34139956047`: SUCCESS;
- production provider: `binance_usdm`;
- production remains read-only;
- no production redeploy is required for documentation-only checkpoint commits.

Repository HEAD may therefore be newer than `/opt/k-trader/DEPLOYED_SHA` without implying an undeployed runtime behavior change.

## Persistent research layout

Immutable prospective Phase 11F source captures:

`/data/research/universe`

Phase 11G materialized research root:

`/data/research/phase11g`

Current catalogue:

`/data/research/phase11g/catalogue.json`

Raw Phase 11F source captures are never modified by Phase 11G materialization.

## Strict context policy

The accepted policy remains:

- `max_context_age_seconds = 300`;
- replay setup interval: 5 minutes;
- no historical liquidity rank/context is fabricated;
- freshness is not widened merely to manufacture longer eligible windows.

Read-only eligibility scan after additional accumulation reported:

- source capture files: `749` at scan time;
- invalid files: `0`;
- provider: `binance_usdm`;
- selected universe config: quote `USDT`, price limit enabled, max price `3`, max candidates `50`;
- selected unique snapshots: `749`;
- symbols seen: `90`;
- eligible symbols under the strict 300-second policy: `45`;
- eligible non-SUI symbols: `44`;
- required coherent cutoffs per candidate window: `16`;
- longest valid strict window observed for the selected candidates: `16` cutoffs / `1.25` hours.

The common accepted replay window is:

- context archive first selected capture: `2026-09-05T14:40:13.613625Z`;
- context archive last selected capture: `2026-09-05T15:59:13.890630Z`;
- replay start: `2026-09-05T14:45:00Z`;
- replay end: `2026-09-05T16:00:00Z`;
- maximum observed context age: `286.386` seconds.

## Deep-history candidate selection

The highest-ranked non-SUI eligibility candidate was `MARSCOINUSDT`, but canonical MTF preflight failed closed:

- requested daily history: `300` bars;
- collected within 100 pages: `4` bars;
- result: insufficient deep history; no chain was materialized or catalogued.

The next candidate `XRPUSDT` passed provider-recorded MTF preflight exactly:

- `1d=300`;
- `4h=300`;
- `1h=300`;
- `15m=300`;
- `5m=400`;
- `as_of=2026-09-05T18:15:00Z`;
- preflight bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`.

## Canonical chain #1 — SUIUSDT

Materialized root:

`/data/research/phase11g/binance_usdm/SUIUSDT/20260905T144500Z_160000Z`

Canonical identities:

- provider: `binance_usdm`;
- symbol: `SUIUSDT`;
- universe archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- MTF bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- replay study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- analyzed cutoffs: `15`;
- skipped insufficient history: `0`;
- skipped missing context: `0`;
- unique tradable signals: `0`;
- binary resolved outcomes: `0`;
- outcome sample: `null`;
- `estimated_probability=null`.

## Canonical chain #2 — XRPUSDT

Materialized root:

`/data/research/phase11g/binance_usdm/XRPUSDT/20260905T144500Z_160000Z`

Universe archive:

- selected snapshots: `16`;
- first capture: `2026-09-05T14:40:13.613625Z`;
- last capture: `2026-09-05T15:59:13.890630Z`;
- universe archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`.

The archive SHA intentionally matches the SUI chain because both studies select the exact same immutable provider/config/time-window captures.

XRP-specific cohort:

- symbol: `XRPUSDT`;
- snapshot count: `16`;
- strict maximum context age: `300` seconds;
- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`.

MTF bundle:

- `as_of=2026-09-05T18:15:00Z`;
- candle counts: `1d=300`, `4h=300`, `1h=300`, `15m=300`, `5m=400`;
- bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`.

The physically materialized bundle reproduced the read-only preflight SHA exactly.

Full-engine replay:

- `step_bars=1`;
- `horizon_bars=None`;
- `start=2026-09-05T14:45:00Z`;
- `end=2026-09-05T16:00:00Z`;
- analyzed cutoffs: `15`;
- skipped insufficient history: `0`;
- skipped missing context: `0`;
- unique tradable signals: `0`;
- outcome counts: `{}`;
- binary resolved count: `0`;
- `estimated_probability=null`;
- study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- provenance SHA: `6397ce7c1786d1ebb5d1e11f297995c3b3c68abb2a44476a29c994164bfcff65`.

No outcome sample was created because no tradable/binary-resolved outcomes exist.

## Two-entry catalogue state

After XRP registration:

- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- SUI entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- XRP entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- current catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- both outcome-sample references: `null`.

The previous one-entry catalogue SHA `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864` remains valid only as the historical first-chain checkpoint identity. It is not the current two-entry catalogue identity.

## Final integrity gate

The two-entry catalogue was loaded with:

`load_dataset_catalogue(..., verify_artifacts=True)`

Result:

- status: PASS;
- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`.

The successful canonical loader verification means referenced physical artifacts and required cross-links passed the catalogue contract for both entries.

## Current accepted state

Phase 11G production research status is now:

`TWO CANONICAL CHAINS / COMPLETE / VERIFIED / CATALOGUED`

This validates repeatability across two symbols, but it does not yet provide a tradable-outcome sample. Both accepted studies naturally produced zero tradable signals in the selected strict window.

No probability semantics have been introduced. Setup Score remains deterministic and `estimated_probability` remains null/N/A.

## Immediate next work after handoff

Do not manually materialize dozens of zero-signal chains one by one.

The next research task is a read-only batch signal-discovery preflight across eligible symbols/windows:

1. preserve `max_context_age_seconds=300`;
2. require provider-recorded canonical MTF depth (`1d/4h/1h/15m=300`, `5m=400` for the current study protocol);
3. run full-engine replay in memory before writing artifacts;
4. rank candidates by naturally occurring `unique_tradable_signals` and resolved outcomes;
5. materialize/register only useful coherent chains;
6. create immutable WIN/LOSS outcome samples only where binary-resolved outcomes actually exist;
7. always finish registration with `verify_artifacts=True`.

Phase 12 multi-provider expansion remains future work and must not begin implicitly from Phase 11 dataset accumulation.
