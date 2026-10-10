# Gerchik book-based digital level rating v0.1 — 2026-10-04

Status: IMPLEMENTED / UNCALIBRATED RESEARCH RATING. Owner explicitly instructed creating a digital rating and performing verification steps 1–7. This instruction authorizes the initial rating now; it does not establish a profitable Level Strength v2 or production trading gate.

## Primary source and reconciliation

Provided book: Alexander Gerchik, Kurs aktivnogo treydera, PDF 282 pages, supplied filename «Курс активного трейдера (Александр Герчик) (2).pdf». PDF pages 56–66 and 207–213 were reread for this change. Source claims are paraphrased here; no full book text is published.

- Pages 57–59,207–209: trend-break significance; meaningful new extreme distinguishes a major reversal from a temporary correction. First technical pullbacks are also discussed (p58), so an ordinary pivot is not a complete structural classifier. Mirror and historical are comparable; mirror can exceed trend-break in context.
- Pages 64–65: additional touches, near misses, false breakouts, subsequent new extrema, long rejection wicks, and round prices strengthen. Page65 describes roughly20% round-price strengthening: preserve it as an author estimate, not empirically verified precision.
- Pages 61,211: anomalous formation bars and long-wick/small-body evidence. Current owner rule disables ATR for level formation; the source's non-ATR average-bar alternative needs an explicit window before its detector is enabled.
- Page60 says >=3 consecutive limit touches, while p209 says >=2 adjacent D1 bars. Current project retains >=3; this discrepancy is recorded rather than silently changing the active classifier.
- Page207 gives selection priority to distance from a critical point, then maximum touches. Distance is a separate relevance/selection criterion, not part of this strength score. The reference point remains an explicit strategy input.
- The 2026-09-28 owner amendment explicitly allows overlapping D1/W1 intervals as reinforcing cross-TF evidence. Keep distinct records/provenance and exact-record deduplication; physical overlap does not disqualify confirmation. This corrects the preceding chat summary's over-restrictive wording.

## Explicit engineering scale

All coefficients, caps and grade thresholds below are project choices, not Gerchik's published scoring formula. They are preregistered here without tuning to outcomes. A low-base type can outrank a high-base type through genuine strengthening, consistent with p64.

| Component | Points | Source grounding |
|---|---:|---|
| One primary type | TREND_BREAK30; MIRROR25; HISTORICAL25; LIMIT20; CONSOLIDATION15; PARANORMAL_BAR10; GAP5 | Qualitative hierarchy p56–63,207–213; mirror/history equality and contextual exceptions |
| Subsequent exact touches | 5 each, cap30 (6) | p64; maximum touches p207 |
| Subsequent near misses | 1 each, cap5 | p64; explicit separate tolerance |
| Subsequent false breakouts | 5 each, cap15 (3) | p64–65,207,209 |
| Subsequent reviewed meaningful new extreme | 10 at most | p65; reviewed prior swing reference required |
| Rejection wick | 5 × maximum relevant wick/range, cap5 | p61,65,211; longer wick/shorter body |
| Reviewed D1/W1 reinforcement | 5 at most | Project HTF-confirmation mandate; not a numeric coefficient from book |

Let raw = sum of components. With an explicitly documented round-price grid, apply author-estimate engineering bonus 0.20×raw for an exact round-grid level. Final score = min(100, raw+bonus), rounded half-up to2 decimals. No grid supplied means no bonus, round_assessed=false; this is a conservative incomplete-feature rating, not proof the price is non-round. A universal quarter-dollar grid is not silently imposed on crypto/Forex. Supplied grid step/offset are integer ticks with provenance.

Grades: 0–39.99 WEAK;40–59.99 MODERATE;60–79.99 STRONG;80–100 VERY_STRONG. Grades are research descriptions and never trading admission or success probabilities. Future calibration may revise weights/thresholds; such versions must preserve source provenance and untouched validation.

## Executable evidence and chronology

`gerchik_level_strength_v0_1.rate()` consumes an externally reviewed CONFIRMED Formation, exact-tick D1/W1 SourceBars, reviewed Proofs and explicit Policy. Pattern review is a required trusted-workflow declaration; this module does not authenticate a reviewer or independently detect all seven formations. Shape/price/chronology checks cannot replace that review.

Formation price must match its referenced High/Low; source close <= formation <= pattern review <= known_at. Candidate/unavailable/invalid levels have score=null. Historical invalidation/state must be supplied correctly as-of by upstream; the tool does not invent price-crossing invalidation thresholds.

Subsequent contact bars start after known_at, close before proof availability, and are reviewed before cutoff. TOUCH requires exact tick contact and close on defended side; NEAR_MISS requires positive nonpenetrating distance within its separate explicit tolerance and returned close. FALSE_BREAKOUT either penetrates and returns on one completed bar, or supplies a unique contiguous multi-bar witness window: first opens on original side, pre-return bars close outside, final bar closes back. OHLC does not infer intrabar execution order.

NEW_EXTREME requires a reviewed causal prior swing-price reference known before its source bar and a surpassed high/low in the reaction direction. CROSS_TF needs a different source timeframe and a matching High/Low within supplied contextual luft; overlapping intervals are allowed. Full pair ambiguity/matching is handled by the existing ledger cross-TF adapter, not inferred by the rating alone.

Formation source is not counted as another strengthening event. Exact duplicate IDs and same-bar/same-kind copies are rejected. A bar has one contact-class contribution, with false-break>touch>near priority. Wick quality is a separate descriptor; cross-TF reinforcement is a separate capped dimension and does not claim statistical independence. No ATR, volume-based actor inference, time decay, outcomes or gradient enter the score. False-break multi-bar and new-extreme structure still need independent qualitative review.

## Verification steps1–7

Full machine-readable status: `GERCHIK_LEVEL_VERIFICATION_1_7_2026-10-04.json`. Fresh source integrity evidence: `GERCHIK_LEVEL_INPUT_REAUDIT_2026-10-04.json`.

| Step | Executed | Remaining |
|---|---|---|
|1 data | Read-only fresh42/42hash audit;447489bars;0gaps/invalidOHLC;51 complete derived W1 per symbol | Tick/calendar/percentage-anchor metadata not verified |
|2 provenance | Synthetic source High/Low/review/identity integration tests | Real independently reviewed current ledger unavailable |
|3 type | Reread source, reconcile7labels and contradictory details; reject unreviewed rating input | Full automatic structural/pattern qualification and real labels |
|4 chronology | Source/review/known-at/as-of tests; verify21 real panels contain no future closes | Real reviewed-level replay |
|5 D1/W1 | Integration tests: overlapping source intervals, inclusive luft, pending review excluded, no midpoint/primary reassignment | Real-symbol metadata and reviewed pairs |
|6 evidence | Rating components, caps, round-grid, duplicate/future rejection and immutable primary tests | Real strength history/calibration |
|7 independent review | Prepare21 unlabelled real panels from7symbols, fixed indices80/180/280,45D1+up to8closedW1, no score/outcome selection | Independent labels and truly untouched control |

The source archive contains no named Gerchik/review/tick/exchange-info candidate files in the checked cohort; this is a scoped availability check, not proof no relevant material exists anywhere. Prepared panels are retrospective evidence from the already inspected year, NOT a new independent holdout. Reviewer/tick fields remain null; no self-approval fabricated.

17 new strength/integration methods plus60 prior cases:77 local Python3.12 tests passed. Source data only read; weekly/panel results calculated in memory and saved as research artifacts. Previous pattern commit208bd632 CI37202744225 succeeded; new-change CI checked after publication. PR94 stays draft/unmerged; no production activation or orders. The output is an implemented auditable scale and partial real-data verification, not completed scientific acceptance of all seven steps.
