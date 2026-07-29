---
name: perplexity
description: Deep web research with synthesized answers and cited sources via Perplexity-style AI search. Use for complex questions, current events, technical research, and fact-checking with verifiable citations.
user-invokable: true
allowed-tools: websearch, webfetch, read, write
metadata:
  keywords: [perplexity, pesquisa profunda, deep research, web search com citacoes, pesquisa web, investigacao, fact check, fontes, cited search]
---

# Perplexity Research Skill

## Purpose

Deep research skill that mirrors Perplexity AI's approach: given a complex question, it performs multi-query web searches, synthesizes findings with citations, and returns a structured answer with sources.

Unlike generic search skills, this one:
- **Synthesizes** multiple sources into a coherent answer
- **Cites** every claim with a source URL
- **Iterates** — drills deeper into sub-questions
- **Validates** cross-references across sources

## Usage

```
/perplexity <research question>
/pesquisa <pergunta complexa>
```

Or routed automatically by the orchestrator for research-heavy tasks.

## Research Methodology

### Phase 1: Decomposition
Break the question into 3-5 sub-queries. Each targets a different angle.

### Phase 2: Parallel Search
Execute all sub-queries via `websearch` in parallel. Collect results with titles, snippets, URLs.

### Phase 3: Deep Fetch
For the most promising results, use `webfetch` to read full content. Prioritize:
- Official documentation
- Reputable technical blogs
- Published papers / articles
- Community discussions (Reddit, HN, Discord)

### Phase 4: Synthesis
Structure the answer:

```markdown
## Answer
<direct, concise answer to the original question>

## Key Findings
1. **Claim 1** — explanation [source](url)
2. **Claim 2** — explanation [source](url)
3. **Claim 3** — explanation [source](url)

## Sources
| # | Title | URL | Relevance |
|---|-------|-----|-----------|
| 1 | ... | ... | high/medium/low |

## Follow-ups
- <unanswered sub-questions>
- <suggested next queries>
```

### Phase 5: Validation
- Cross-check claims across 2+ independent sources
- Flag conflicting information
- Note publication dates (prefer < 6 months)
- Mark speculative claims as such

## Task Structure

```json
{
  "query": "What are the latest trends in AI coding assistants?",
  "depth": "standard",
  "num_sources": 5,
  "focus": "technical"
}
```

### Parameters
- `query` (required): Research question
- `depth` (optional): "quick" (1-2 searches), "standard" (3-5), "deep" (6-10) — default "standard"
- `num_sources` (optional): Min sources to cite (default 3, max 10)
- `focus` (optional): "technical", "news", "academic", "general" — default "general"

## Error Handling

| Scenario | Action |
|----------|--------|
| No results found | Broaden query, try synonyms |
| Conflicting sources | Present both sides, note disagreement |
| Outdated info (>1 year) | Flag as potentially stale, suggest fresh search |
| Paywalled content | Note paywall, find alternative source |
| Rate limited | Wait 2s, retry once |

## Orchestrator Integration

### Routing Keywords

| Keyword | Route |
|---------|-------|
| pesquisa profunda, deep research | perplexity |
| fact check, verificar, checar | perplexity |
| tendencias, trends, atualidades | perplexity |
| investigar, investigacao | perplexity |
| comparar, compare, analyze | perplexity |

### Common Patterns

**"O que está acontecendo em X?"**
→ Decompose into 3 sub-queries (news, analysis, opinions)
→ Parallel search → Synthesize → Answer with citations

**"Qual a diferenca entre X e Y?"**
→ Search for X docs, Y docs, comparison articles
→ Build comparison table → Cite each source

**"Is X verdade?"**
→ Search for evidence for and against
→ Cross-reference → Verdict with confidence level

## Dependencies

- `websearch` tool (built-in)
- `webfetch` tool (built-in)
- No external APIs required — uses native OpenCode tools

## Rules

- ALWAYS cite sources for every factual claim
- NEVER hallucinate URLs — only include sources actually fetched
- PREFER primary sources (docs, papers) over secondary (blogs, summaries)
- FLAG uncertainty when sources conflict or are weak
- RESPECT rate limits — sequential deep fetches with delays
- KEEP answers concise but thorough — 1-4 paragraphs + sources table

## Integration with Other Skills

- **browser-agent**: When websearch/webfetch insufficient, delegate browsing
- **code-review**: Research coding patterns, then review against them
- **plan**: Research feasibility before planning implementation
- **debugging**: Research error messages, known issues, solutions
