# K-Trader Host Boundary: HP-OMEN Prohibited

**Effective:** 2026-09-25  
**Status:** MANDATORY / until a separate explicit instruction from the project owner  
**Applies to:** K-Trader development, research, runtime, integrations, acceptance, documentation workflows and any automated agent.

## Hard exclusion

**Do not use HP-OMEN in any K-Trader task until the owner separately and explicitly authorizes its use.** This includes direct access and indirect use through connectors, SSH tunnels, relays, APIs, scripts, shared files, research jobs or another project.

In particular:

- do not connect to, run commands on, restart, inspect, or reboot HP-OMEN for K-Trader;
- do not use it for CI, exact-SHA tests, collection, datasets, historical/prospective studies, backups, storage, artifact recovery, monitoring or deployment;
- do not acquire market context through a route backed by HP-OMEN, including the previously documented K_AI/MT4 read-only integration;
- do not treat HP-OMEN ACL incidents, DPAPI credentials, Windows Startup, watchdogs or local runtime as K-Trader maintenance backlog;
- do not propose HP-OMEN as a fallback if approved K-Trader resources are unavailable.

The K_AI Trading System is a separate project. Its machine-level operational history does not authorize K-Trader to use its host, service, credentials or data.

## Allowed K-Trader execution boundary

- Use approved K-Trader-controlled GitHub repositories, review/PR workflows and independently reachable Oracle Cloud/server resources.
- The existing Oracle production service may be checked read-only over its approved management channel; maintain its `read_only` trading boundary.
- Phase 11G research may use only verified, already-approved server-local research data and tools, with unchanged causal/provenance constraints.
- If any task requires HP-OMEN or a host whose independence cannot be verified, mark that step **BLOCKED / NO EXECUTION**. Do not silently substitute another machine or mixed data source.
- Do not stop, remove or reconfigure pre-existing HP-OMEN-related integration as part of this documentation-only restriction; simply exclude it from K-Trader operations until separately instructed.

## Research and production governance retained

- Phase 11G remains active until its documented closure gate is met.
- Frozen candidate, harness/protocol hashes, resolver v1.3, ledger v1.2, preregistered cutoff, untouched holdout and evidence tiers remain unchanged.
- Phase 12, trading, production risk-policy selection and integration cutover remain unauthorized.
- Do not infer that an API's health implies an HP-OMEN-backed route may be used.

## Lifting this restriction

Only a **new explicit user instruction** may authorize HP-OMEN for K-Trader. Before any future use, record the permitted purpose, execution surface, time/scope and data boundary in a reviewed documentation change. Silence or prior cross-project access is not consent.

Historical material predating this policy is context only where it conflicts with the current prohibition.
