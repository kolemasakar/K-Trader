# K-Trader Checkpoint — 2026-09-16 19:00Z Ledger v1.2 Recovery

Status: **ACCEPTED / READY TO CONTINUE**

## Accepted boundary

- research branch: `research-strategy-benchmark-v1`
- frozen strategy: `candidate_rule_set_v2_2`
- accepted cutoff: `2026-09-16T19:00:00Z`
- resolver: `v1.3`
- ledger: `v1.2`, first-seen event payload immutable
- prereg boundary: `2026-09-16T13:00:00Z`
- holdout: false / not authorized
- production action: false
- Phase 11G: ACTIVE
- Phase 12: NOT ACTIVE

## 19:00Z execution history

The first pipeline v2 execution at `19:00Z` produced valid capture and funding artifacts but resolver v1.3 failed closed on a VTHOUSDT prior-stop identity mismatch.

The failure was accepted as an infrastructure causality defect in ledger v1.1, not as a strategy or resolver defect. Ledger v1.1 replaced first-seen duplicate payloads with later recomputations.

Ledger v1.2 was validated, staged from the exact repository source, and rebuilt. The valid 19:00Z capture/funding artifacts were then reused and downstream processing resumed without recapturing the cutoff.

Recovery result: **PASS**.

Detailed acceptance:

`docs/research/PROSPECTIVE_LEDGER_V1_2_ACCEPTANCE_2026-09-16.md`

## Accepted sample state

- eligible observations `61`
- unique primary families `47`
- resolved primary families `47`
- unresolved primary families `0`
- wins `13`
- losses `34`
- win rate `27.65957446808511%`
- expectancy `-0.5989123384630131R`
- confirmation families `3`
- confirmation resolved `3`
- current open families `0`
- evidence tier `DIAGNOSTIC_30_49_RESOLVED_FAMILIES`

No sample-count or outcome change was caused by the ledger migration.

## Capture / funding

Run root:

`/data/research/phase11g/v2_2_shadow_20260916T190000Z`

Capture:

- status `VALID_SHADOW_CAPTURE`
- panel `19/19`
- eligible setups `49`
- event count `298`
- signal bars evaluated `6574`
- bundle export summary SHA256 `562c5a0ac8f90c60892e1833ddaa79326aba621a17bd44b108a79dc789ecb1d7`
- event file SHA256 `dcd5785a52429e1ad595ff81819d43ee272700f919a317e86f101074c7779978`
- shadow summary SHA256 `2629c5b901a989b8b9e3ff7cf80ce9463a7def5d590fa48ce44817fbf4b45b0f`

Funding:

- symbols `19`
- summary SHA256 `8da69589ff966f0fdc4dfb9872df4f964215d333fa68941fdbe43268cccb127d`

## Ledger v1.2

Canonical ledger:

`/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_ledger`

State:

- schema `ktrader.candidate_v2_2.prospective_shadow.ledger.v1_2`
- first-seen payload immutable `true`
- deduplicated events `393`
- eligible setups `61`
- unique eligible families `47`
- raw duplicate occurrences `5991`
- conflicting duplicate occurrences `5991`
- conflicting event keys `391`
- ledger event-set SHA256 `de631c72a5cd932b3d7e3df66671d702296dfbbf30514bacc50df9dee2f9edc6`
- ledger summary SHA256 `03eebcd4b09e37e9b42a2ed6d9b3dd4840bcfe7c948c726550f23f2cf3234dce`
- ledger events SHA256 `2644a7781735aa9b5f2e48e858afbcbe6e54f139d2e682f6270bb4c61eeda210`

## Resolver continuity

19:00Z outcomes summary SHA256:

`fc028d68af827487691aa5acb348fe986b324ba53abd6805ee117e4a1ac3d2c2`

Continuity:

- prior terminal reuse `61`
- path revalidated `51`
- source-window expired `10`
- max entry delta `0.0`
- max stop delta `3.809370596741246e-10`

## Evidence / risk / state

- evidence SHA256 `2feada24deeb6909c327c06acee2f814d7298868594e29e3bd845aa26b4da5af`
- portfolio-risk SHA256 `6403fb04638444d28d0e194624bc756f3ce04ea4418d1356e19315cb41d44f05`
- current open families `0`
- state manifest `/data/research/phase11g/strategy_benchmark_v1/combined_rules/current_state_manifests/20260916T190000Z.json`
- state manifest SHA256 `18d9ea1956f9035951c008c06cae0ca363c39fdc89599e1fa37a4c020cc4a077`
- state-source verification `5/5 PASS`, `0` mismatches

Recovery manifest SHA256:

`f796ecdd2d3456ae6ca727179c12b15e25dbf78bebc21fd3e5a2a29a934a57a4`

## Production invariant

Latest post-recovery verification:

- host `k-trader-prod-vnic`
- deployed SHA `81b79b281a4cc330b7c11058d202e0d74fb6d70e`
- health `ok`
- mode `read_only`
- `data_ready=true`
- provider `binance_usdm`
- scanner remains known `DEGRADED` fail-closed/history-readiness state
- no deploy, restart or trading action

## Phase 11G closure

Path A remains incomplete:

- resolved families `47/100`
- shortfall `53`
- confirmation `3/3` resolved, still underpowered

Path B has not been selected.

## Resume instructions

Next causal cycle must use:

`PRIOR_OUTCOMES=/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3/20260916T190000Z`

Only run at a fully closed M15 cutoff. Preserve frozen v2.2, resolver v1.3 guards, ledger v1.2 first-seen immutability, prereg boundary, holdout false and production read-only state.