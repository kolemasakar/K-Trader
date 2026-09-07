# K-Trader Current State

Updated: 2026-09-07

Canonical operational checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_TWO_CHAIN_DATASET_CHECKPOINT.md`

Prior production-chain checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md`

Prior transition snapshot:

`docs/checkpoints/2026-09-07_PROJECT_STATE_PHASE11_HANDOFF.md`

Current phase boundary:

- Phase 10: COMPLETE / product accepted for the current single-provider read-only v1 scope;
- Phase 11A–11G: repository-side implementation VERIFIED;
- Phase 11F production accumulation: VERIFIED on real provider-recorded captures and still accumulating;
- Phase 11G physical production evidence: TWO canonical chains COMPLETE / VERIFIED / CATALOGUED;
- current catalogue entry count: `2`;
- active work: read-only batch signal/outcome discovery across eligible provider-recorded study candidates, followed by selective canonical materialization;
- Phase 12: future multi-provider expansion, not active.

Repository/documentation baseline before this new documentation-only checkpoint:

- `main` SHA: `40cee9b17aa74ad45be1894d566ddb79f8a81ef4`;
- post-merge Tests run `34144783877`: PASS;
- post-merge CI run `34144783943`: pytest PASS, Docker amd64 PASS, Docker arm64 PASS.

Accepted production runtime baseline:

- deployed production SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- Deploy Production #7 run `34139956047`: SUCCESS;
- production provider: `binance_usdm`;
- runtime: healthy, read-only, `data_ready=true`;
- no redeploy is required for documentation-only commits.

Strict Phase 11G context/replay policy remains:

- `max_context_age_seconds=300`;
- no historical rank/context fabrication;
- no freshness widening merely to manufacture eligible history;
- outcome samples are created only when real binary WIN/LOSS outcomes exist;
- `estimated_probability` remains null/N/A.

Current canonical Phase 11G catalogue:

- path: `/data/research/phase11g/catalogue.json`;
- schema: `ktrader.dataset_catalogue.v1`;
- entry count: `2`;
- current catalogue SHA: `057ff750966d2bc5043fffd7fdc37583dd0133480452c131b51f84109d2fb4b6`;
- final reload with `verify_artifacts=True`: PASS.

## Entry 1 — SUIUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z` inclusive;
- archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- unique tradable signals: `0`;
- outcome sample: `null`.

## Entry 2 — XRPUSDT

- provider: `binance_usdm`;
- replay window: `2026-09-05T14:45:00Z` through `2026-09-05T16:00:00Z` inclusive;
- archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `f417e64f9c2a31916564037709554971035adbb14054a3f83b2b76261e2ee58c`;
- bundle SHA: `8b276ab7d8ffa5614c38759a7fbccdf3fdf27c855e4460b04f8e4693b8b090af`;
- study ID: `886d2a5c136af427657d005655d3b654b046dd9ede19b922390bb403fbe60c80`;
- provenance SHA: `6397ce7c1786d1ebb5d1e11f297995c3b3c68abb2a44476a29c994164bfcff65`;
- catalogue entry ID: `4788384b5268ae8062eaa1a225de8d54cbd12e59e17ea3905d702ed5545a8eef`;
- unique tradable signals: `0`;
- outcome sample: `null`.

Read-only eligibility scan found `45` eligible symbols under the strict 300-second context policy (`44` excluding SUI). `MARSCOINUSDT` was the highest-ranked next candidate but failed canonical deep-history preflight because only 4 daily bars were available versus the required 300; `XRPUSDT` then passed full MTF preflight and became the second accepted chain.

The successful two-entry catalogue reload with `verify_artifacts=True` confirms the physical-artifact and cross-link contract for both registered chains.

This checkpoint branch is documentation-only. After it is merged, repository HEAD may again be newer than the deployed runtime SHA without implying an undeployed runtime behavior change.

For exact recovery details and next work, read the canonical operational checkpoint above.
