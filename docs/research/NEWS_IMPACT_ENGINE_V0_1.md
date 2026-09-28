# News Impact Engine v0.1 — research-only

## Scope and non-goals
Isolated deterministic Python library at src/ktrader/news_impact.py. Does not fetch news, subscribe to KGM, execute trades, modify RiskManager or production, infer direction or assign profitability probabilities. Independent historical testing is explicitly NOT approved.

## Flow
KGM / official economic calendars / free public sources → external read-only adapter (future work) → normalized NewsEvent → dedup/version → source freshness/provenance → explicit instrument exposure mapping → deterministic impact → evidence snapshot → separate approved risk-gate integration.

KGM is a potential upstream **context provider**, not a trading authority. Its connector/API, response schema, authentication and live availability must be verified in KGM repository before implementation; no assumed endpoint. Zero-paid-service default; do not use TinyFish paid balance. Public news collection must respect provider terms and licensing. No full-text redistribution.

## Implemented schema
NewsEvent: source, source_id, published_at, received_at, headline, assets, event_type, severity (0–3), confidence (0–1), evidence_urls, optional scheduled_at, revision. Strict UTC aware as-of. Identity SHA256(source|source_id|revision). Adapter must resolve assets from event exposure; the library does not guess mappings.

Impact: symbol, action NO_CHANGE/REVIEW/DEFER_NEW_ENTRY/UNKNOWN, event_ids, reasons, as_of. DEFER_NEW_ENTRY is **advisory** until explicitly approved risk-gate integration. Missing entire feed => UNKNOWN, never "safe". Low-confidence relevant news => UNKNOWN. Severity 3 with sufficient confidence => DEFER_NEW_ENTRY; severity 2 => REVIEW. These are *policy prototypes*, not calibrated market-risk probabilities.

## Planned KGM adapter contract
Required provenance: original source URL and publisher, publication time, KGM ingestion time, KGM evidence/claim ID, confidence methodology, source revision/correction, language, entity mappings, embargo/expiry. Deduplicate syndication (multiple outlets repeating same original claim), keep original and revision lineage. Separate official scheduled economic releases from breaking geopolitical news; handle pre-release calendar windows and post-release revisions independently. Macro mapping: FX quote/base currency, crypto benchmarks, equity ticker/sector/market, geopolitical jurisdiction, sanctions, exchange operating status. No automatic wildcard tagging based only on LLM opinion.

## Safety and observability
- UNKNOWN on missing feed, mapping uncertainty, stale provider status; operational policy must distinguish "no relevant events" from "no data".
- No lookahead: both published_at and received_at must be <= as_of. Late corrections apply only after receipt.
- Human review for consequential severity and ambiguity. No position changes from headlines.
- Append-only event/evidence logs and provider health metrics; replay with exact data-as-known.
- News severity and confidence are classification inputs, not empirically calibrated probabilities.
- Free-provider outages cannot silently disable existing risk controls.

## Limitations / pending acceptance
Prototype does not yet implement scheduled-event windows, provider polling, source corroboration, symbol mapping, provider-health TTL, persistence, KGM handshake or integration into live signal pipeline. Do not describe these as implemented. The current NO_CHANGE result with unrelated events does not establish feed completeness; adapter/health contract must address this before production.

## Acceptance gates before any deployment
KGM interface audit; signed-off source/exposure taxonomy; calendar/revision and time-window tests; quality/provenance checks; incident fail-closed policy; deterministic replay; independent historical evaluation **only after separate user approval**; explicit live integration authorization.
