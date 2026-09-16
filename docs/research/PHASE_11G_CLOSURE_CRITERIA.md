# Phase 11G Closure Criteria

Status: **ACTIVE CLOSURE CONTRACT**

Phase 11G remains active until one of the defined closure paths is explicitly accepted. These criteria do not automatically promote any strategy or open holdout.

## 1. Infrastructure/evidence gates — mandatory for any closure

All of the following must be true:

- production health is operational under the accepted read-only boundary;
- frozen harness and protocol hashes are pinned and reproducible;
- prospective capture is causal and closed-bar only;
- family semantics are deterministic and versioned;
- current resolver version has accepted parity against prior immutable outcomes;
- provenance/evidence tracker reports PASS;
- discovery/confirmation boundary is preserved;
- holdout remains untouched unless a later explicitly approved phase says otherwise;
- production action remains false;
- fail-closed orchestration and recovery procedure are documented/tested;
- no unresolved critical infrastructure blocker remains.

## 2. Portfolio/economic diagnostics — mandatory

Before closure, the final Phase 11G report must include:

- fees/funding/slippage treatment;
- BASE and available stress economics;
- symbol concentration;
- same-side/concurrent exposure;
- correlation-cluster exposure;
- path-quality / MFE-MAE summary;
- known regime dependence;
- known data limitations.

These diagnostics may reject a candidate but cannot by themselves authorize a production risk configuration.

## 3. Evidence-tier accounting

Current governance remains:

- `<30` resolved primary families: observation only;
- `30–49`: diagnostics;
- `50–99`: hypotheses/ablation proposals only;
- `>=100`: a versioned recalibration proposal may be considered, still requiring fresh OOS/prospective evidence and explicit promotion.

Historical trades never count toward these prospective thresholds.

## 4. Closure Path A — evidence-complete benchmark

Phase 11G may close as an evidence-complete benchmark when:

- at least `100` resolved primary prospective families exist;
- the final accepted resolver/provenance state is reproducible;
- preregistered hypotheses have either reached their minimum sample requirements or are explicitly marked underpowered/inconclusive;
- a final benchmark report records performance, regime dependence and failure modes;
- no in-place retuning is applied to frozen v2.2.

Result may be positive, negative or inconclusive. `100` is an evidence/governance milestone, not a profitability guarantee.

## 5. Closure Path B — explicit candidate termination

Phase 11G may also close before 100 resolved families if the user explicitly decides that continuing v2.2 prospective collection has insufficient value.

Required output:

- archive frozen v2.2 as a negative/inconclusive benchmark;
- preserve all accepted prospective artifacts;
- state the exact resolved-family count at termination;
- record why collection stopped;
- do not reinterpret the terminated sample as a successful strategy.

This path avoids forcing unnecessary data collection for a candidate that has already served its benchmarking purpose.

## 6. Closure does not equal production promotion

Closing Phase 11G does **not** automatically:

- open holdout;
- enable Phase 12;
- authorize trading;
- choose portfolio risk caps;
- change RR/max-hold/filters;
- integrate results from `K_Investigation_Forecast`.

Any next phase requires a separate explicit transition checkpoint.

## 7. Current open items

At the time this contract was introduced, remaining Phase 11G work includes:

- continue causal prospective resolution;
- accumulate post-prereg confirmation evidence;
- keep portfolio-risk diagnostics current;
- use the fail-closed evidence-aware pipeline;
- produce a final closure report when Path A or Path B is explicitly accepted.
