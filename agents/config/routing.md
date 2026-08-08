---
name: Agent Routing Configuration
description: Routing configuration for agent selection including keyword mapping, model selection rules, and agent fallback patterns
version: 12.0
---

# ROUTING TABLE V12.0

> **Ultima modifica:** 26 Febbraio 2026
> **Versione:** 12.0 DEEP AUDIT

---

## KEYWORD → AGENT MAPPING

### L1 Expert Agents

| Keyword | Agent | Model | Level |
|---------|-------|-------|-------|
| GUI, PyQt5, Qt, widget, dialog, layout, UI | gui-super-expert.md | inherit | L1 |
| database, SQL, SQLite, PostgreSQL, schema, migration | database_expert.md | inherit | L1 |
| security, encryption, auth, JWT, OWASP, hash | security_unified_expert.md | inherit | L1 |
| API, REST, webhook, integration, client, server | integration_expert.md | inherit | L1 |
| test, debug, QA, performance, profiling | tester_expert.md | inherit | L1 |
| MQL, MQL5, EA, MetaTrader, OnTimer, OnTick | mql_expert.md | inherit | L1 |
| trading, risk, position, TP, SL, strategy | trading_strategy_expert.md | inherit | L1 |
| architettura, design, pattern, microservizi | architect_expert.md | opus | L1 |
| DevOps, deploy, CI/CD, Docker, build | devops_expert.md | haiku | L1 |
| Python, JavaScript, C#, coding, refactor | languages_expert.md | inherit | L1 |
| AI, LLM, GPT, embedding, model | ai_integration_expert.md | inherit | L1 |
| Claude, Haiku, Sonnet, Opus, token | claude_systems_expert.md | inherit | L1 |
| mobile, iOS, Android, Swift, Kotlin, Flutter | mobile_expert.md | inherit | L1 |
| n8n, automation, workflow, trigger | n8n_expert.md | inherit | L1 |
| OAuth, OIDC, social login, Google, Facebook | social_identity_expert.md | inherit | L1 |
| MCP, plugin, tool discovery, model context protocol | mcp_integration_expert.md | inherit | L1 |
| playwright, browser, e2e, selenium, automation web | browser_automation_expert.md | inherit | L1 |
| stripe, paypal, payment, checkout, subscription | payment_integration_expert.md | inherit | L1 |
| slack, discord, notification, alert, messaging | notification_expert.md | inherit | L1 |
| offensive security, pentest, exploit, red team | offensive_security_expert.md | inherit | L1 |
| reverse engineer, binary, disassemble, IDA, Ghidra | reverse_engineering_expert.md | inherit | L1 |
| decompile, .ex4, .ex5, EA protection | mql_decompilation_expert.md | inherit | L1 |
| gestão de projeto, roadmap, cronograma, microaportes, reunião, PM | project_manager_expert.md | inherit | L1 |
| estratégia, market fit, posicionamento, oferta, segmentação, público-alvo | strategy_expert.md | inherit | L1 |
| marketing, mídia, tráfego, funil, webinar, anúncio, Meta Ads, criativos, CPL, CAC | marketing_expert.md | inherit | L1 |
| vendas, CRM, pipeline, WhatsApp, fechamento, qualificação, atribuição, SLA | sales_crm_expert.md | inherit | L1 |
| conteúdo, copy, landing page, anúncio, Instagram, carrossel, CTA, storytelling | content_copy_expert.md | inherit | L1 |

### MCP & Ferramentas Externas

| Keyword | Rota |
|---------|------|
| MCP, servidor MCP, tool discovery, modelo context protocol | mcp_integration_expert |
| busca web, web search, web-reader, fetch URL | mcp_integration_expert (ou websearch) |
| clang, LSP, code intelligence | languages_expert |
| swift, LSP iOS | mobile_expert |

> Nota: servidores MCP externos e LSP só são roteados se configurados no `opencode.jsonc` (runtime). Sem a config, as keywords acima caem nos agentes L1 correspondentes.

### L2 Sub-Agent Mapping

| L2 Agent | Parent L1 | Keyword Trigger |
|----------|-----------|-----------------|
| gui-layout-specialist | gui-super-expert | layout, sizing, splitter |
| db-query-optimizer | database_expert | query, index, optimize |
| security-auth-specialist | security_unified_expert | auth, JWT, session |
| api-endpoint-builder | integration_expert | endpoint, route |
| test-unit-specialist | tester_expert | unit test, mock, pytest |
| mql-optimization | mql_expert | optimize EA, memory |
| trading-risk-calculator | trading_strategy_expert | risk, position size |
| mobile-ui-specialist | mobile_expert | mobile UI, responsive |
| n8n-workflow-builder | n8n_expert | workflow builder |
| claude-prompt-optimizer | claude_systems_expert | prompt optimize |
| architect-design-specialist | architect_expert | system design, patterns |
| devops-pipeline-specialist | devops_expert | pipeline, CI/CD |
| languages-refactor-specialist | languages_expert | refactor, clean code |
| ai-model-specialist | ai_integration_expert | LLM integration, RAG |
| social-oauth-specialist | social_identity_expert | OAuth flow, social login |

### L0 Core Agents

| Keyword | Agent | Model | Use Case |
|---------|-------|-------|----------|
| cerca, trova, esplora | core/analyzer.md | haiku | File search, exploration |
| implementa, fix, codifica | core/coder.md | inherit | Coding, implementation |
| review, valida, quality | core/reviewer.md | inherit | Code review |
| documenta, scrivi, README | core/documenter.md | haiku | Documentation |
| coordina, resource, token | core/system_coordinator.md | haiku | Resource management |

---

## DOMAIN PATTERN FALLBACK

| Pattern | Fallback Agent |
|---------|----------------|
| gui-* / ui-* / widget-* | gui-super-expert |
| db-* / data-* / sql-* | database_expert |
| security-* / auth-* / jwt-* | security_unified_expert |
| api-* / rest-* / integration-* | integration_expert |
| test-* / qa-* / debug-* | tester_expert |
| mql-* / ea-* / mt5-* | mql_expert |
| trading-* / risk-* | trading_strategy_expert |
| mobile-* / ios-* / android-* | mobile_expert |
| n8n-* / workflow-* / automation-* | n8n_expert |
| claude-* / prompt-* / ai-* | claude_systems_expert |
| arch-* / design-* | architect_expert |
| devops-* / deploy-* / ci-* | devops_expert |
| pm-* / roadmap-* / project-* | project_manager_expert |
| strategy-* / market-* / positioning-* | strategy_expert |
| marketing-* / media-* / funnel-* / campaign-* | marketing_expert |
| sales-* / crm-* / whatsapp-* / pipeline-* | sales_crm_expert |
| content-* / copy-* / cta-* / landing-* | content_copy_expert |

---

## MODEL SELECTION RULES

| Model | Use Case | Examples |
|-------|----------|----------|
| **haiku** | Mechanical tasks, no reasoning | File reads, search, DevOps, documentation |
| **inherit** | Problem-solving (default) | Coding, APIs, database, security, testing |
| **opus** | Architecture decisions | System design, strategic decisions |

**Note:** `inherit` = omit model parameter in Task tool (inherits from parent, typically Opus 4.6). Using `sonnet` directly causes 404 errors.
