# Internal D1 archive continuity preflight — 2026-10-01

Status: READ-ONLY SOURCE PREFLIGHT PASS; ATR5 AND LEVEL HISTORICAL AUDIT STILL PENDING.

Source: production-mounted, unchanged archive `/data/research/phase11g/historical_expansion_v1_20260905T144500Z/bundles/*/1d.jsonl`. Read-only `sudo docker exec ... python -c` enumerated the 19 source files and parsed the manifest plus every candle record. This preflight did not run the research-branch Gerchik ATR5/level audit script, which is not packaged in the currently deployed main image; do not claim historical ATR5 or level validation from this source check.

Results: **19/19** D1 files had zero missing UTC-day transitions, zero unfinished/invalid high-low bars, and a manifest candle count equal to the actual candle count. All end 2026-09-04 UTC. 15 instruments have 500 candles from 2025-04-23; exceptions: AKEUSDT 344 (from 2025-09-26), METUSDT 329 (from 2025-10-11), PUMPUSDT 422 (from 2025-07-10), USELESSUSDT 386 (from 2025-08-15). Source manifests retain per-file content SHA256. This check does not establish exchange completeness beyond the supplied archive, full multi-timeframe availability, level quality or strategy profitability.

CI: commit `38d31763654a730373fcd63c0151b041d66026c4`, run `36913419486`, SUCCESS. Includes rolling ATR5 tests and D1 pivot prefix-stability tests. The test suite covers current implementation behavior but does not establish that its candidate-inclusive reference formula matches the owner's intended sequential replacement and recalculation. Keep that semantic review explicit.

Next gate: review ATR5 reference semantics and exact anomaly-replacement sequence with deterministic worked examples. Only after this is resolved, make the validated research code available to a bounded Landlock child without merging/deploying experimental research as production code. Run actual per-symbol causal ATR5 + D1/W1 level historical audit against existing archive, write only to isolated results, record exact code SHA, manifest/source hashes, per-symbol coverage and exclusions. Keep PR #94 draft, no production configuration changes or live orders.
