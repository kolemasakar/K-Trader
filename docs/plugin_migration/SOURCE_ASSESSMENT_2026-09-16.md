# OpenAI Custom GPT Retirement → Plugin Migration: K-Trader Assessment

Date: 2026-09-16

Status: **VERIFIED EXTERNAL PRODUCT CHANGE / K-TRADER ARCHITECTURE ADJUSTED**

## Verified points

OpenAI currently states that:

- custom GPTs are planned for retirement across ChatGPT plans;
- affected Enterprise retirement is planned for `2026-12-11`;
- Enterprise migration experience is targeted for `2026-09-17`;
- new Custom GPT creation is planned to end for affected Enterprise workspaces on `2026-09-25`;
- exact rollout/timing may vary by account/workspace/plan;
- replacement Plugins combine reusable skills with connected apps/integrations;
- Custom Actions require separate migration work and should not be assumed to transfer automatically;
- migrated replacement Plugin access/sharing must be reviewed separately.

Official references reviewed:

- OpenAI Help: GPTs in ChatGPT;
- OpenAI Help: Custom GPT retirement and migration FAQ;
- OpenAI Help: Plugins in ChatGPT and Codex;
- OpenAI ChatGPT Release Notes, 2026-09-11 entry.

Project-source input also reviewed:

`kolemasakar/AI_general/docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md`

Its main architectural conclusion is consistent with the official material.

## K-Trader consequence

The canonical K-Trader backend is **not deprecated** by this product change.

The affected component is the ChatGPT-facing wrapper:

`Custom GPT instructions + Custom Action schema`

Long-term target is now:

`Plugin skill + app/connector/MCP integration -> existing read-only K-Trader backend`

## Immediate decisions

- keep existing Custom GPT working until replacement acceptance;
- classify `custom_gpt/` as legacy compatibility assets;
- stop treating new Custom Action work as the strategic integration target;
- keep API semantics generic/read-only;
- extract behavioral instructions into a skill draft;
- specify a connector/MCP integration contract;
- create a regression suite for semantic parity and permissions;
- do not assume old GPT sharing/public access transfers to the Plugin.

## No strategy impact

This product migration does not change:

- frozen candidate v2.2;
- prospective evidence;
- portfolio-risk findings;
- holdout state;
- production trading authorization;
- external `K_Investigation_Forecast` research boundary.
