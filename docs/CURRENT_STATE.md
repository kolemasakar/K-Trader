# K-Trader Current State

Updated: 2026-09-07

Canonical operational checkpoint:

`docs/checkpoints/2026-09-07_PHASE11G_FIRST_PRODUCTION_CHAIN.md`

Prior transition snapshot:

`docs/checkpoints/2026-09-07_PROJECT_STATE_PHASE11_HANDOFF.md`

Current phase boundary:

- Phase 10: COMPLETE / product accepted for the current single-provider read-only v1 scope;
- Phase 11A–11G: repository-side implementation VERIFIED;
- Phase 11F production accumulation: VERIFIED on real provider-recorded captures;
- first Phase 11G physical production evidence chain: COMPLETE / VERIFIED / CATALOGUED;
- active work: continued Phase 11 operational/research accumulation and additional coherent study chains;
- Phase 12: future multi-provider expansion, not active.

Accepted code/runtime baseline before this documentation-only checkpoint:

- main/code SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- Deploy Production #7 run `34139956047`: SUCCESS;
- deployed production SHA: `b75b1e3d74b5834e7c404555caa6bdf34f87fe12`;
- production provider: `binance_usdm`;
- runtime: healthy, read-only, `data_ready=true`.

First canonical Phase 11G production catalogue entry:

- symbol: `SUIUSDT`;
- archive SHA: `3c830d8410b913aa4b39afd8cb5be57e96a18b4a1ae4d46fa709fc11f70ccdda`;
- cohort SHA: `c63b90a1905149462e1eb31a842fff7c5f15290a7f4963107d7c8c4cf2273686`;
- bundle SHA: `c0112c0d3688cddb86cabc54ae1c9da05e04ff2cef63f395b438448e3070d344`;
- study ID: `ebfd16b0b9059c5bd51f948d4c1b0086f4a2966a610e58dd7a6fb0d8ee474f5e`;
- provenance SHA: `08ba2378253dfa744ffbfc2fc74cae2ab6ff02264a9b60e6170d1992f6297c35`;
- catalogue entry ID: `f056dadd63c2283c07b0b2aa37b3bb2236d15e916d6fa3cf5a11fc71b38b814a`;
- catalogue SHA: `749c3aa20d02788b1c75b48e3325d854d7182f5b0729fea39dcf888af367b864`;
- tradable signals: `0`;
- outcome sample: `null` by contract;
- `estimated_probability`: null/N/A.

The final catalogue was reloaded with `verify_artifacts=True`; all physical artifacts and cross-links passed canonical verification.

This checkpoint branch is documentation-only. After it is merged, repository HEAD may be newer than the deployed runtime SHA without implying an undeployed runtime behavior change.

For exact recovery details and next work, read the canonical operational checkpoint above.
