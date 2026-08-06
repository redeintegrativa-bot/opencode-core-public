---
name: firecrawl
description: Web scraping and crawling powered by Firecrawl (API or self-hosted) — extract LLM-ready markdown, structured data with schemas, crawl entire sites, and search the web. Use when a task needs reliable page-to-content conversion, multi-page crawls, or schema-based extraction that plain requests/Playwright can't handle.
user-invokable: true
allowed-tools: Read, Grep, Glob, Bash
metadata:
  keywords: [firecrawl, scrape, crawl, markdown, extraction, llm, web-scrape, site-crawl]
---

# Firecrawl Skill

## Purpose

Firecrawl converts web pages and entire sites into clean, LLM-ready markdown or structured JSON. It handles JavaScript-rendered pages, anti-bot measures, and complex extraction that raw `requests` or ad-hoc Playwright scripts struggle with.

## Core Principle

Firecrawl's job is **content conversion**: page → markdown, page → schema JSON, site → crawl dataset, or query → search results. If the task is "give me the content of this page/site in a consumable format", reach for Firecrawl before writing a bespoke scraper.

## When to Activate

- User asks to scrape a page or site into clean text/markdown
- Need structured JSON from a page via a JSON schema (not CSS selectors)
- Site-wide extraction (crawl) with limits, paths, or max pages
- Web search where results must come back as clean content, not raw HTML
- The target page is JS-heavy or protected; Playwright/requests scraping failed or would be slow

## Setup

**Option A — Firecrawl Cloud (recommended for one-off use):**
```bash
export FIRECRAWL_API_KEY="fc-..."
export FIRECRAWL_API_URL="https://api.firecrawl.dev"
```

**Option B — Self-hosted (open source, Docker):**
```bash
git clone https://github.com/mendableai/firecrawl.git
cd firecrawl && cp .env.example .env   # set PORT, and API keys for LLM features
docker compose up                       # default endpoint: http://localhost:3002
export FIRECRAWL_API_URL="http://localhost:3002"
```

**Python SDK:**
```bash
pip install firecrawl-py
```

## Usage Patterns

### 1. Scrape a page to markdown

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-...", api_url="https://api.firecrawl.dev")

scraped = app.scrape_url(
    "https://example.com",
    params={
        "formats": ["markdown", "html"],
        "onlyMainContent": True,
    },
)
markdown = scraped.get("markdown")
```

### 2. Structured extraction with a schema

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "string"},
                },
            },
        },
    },
}

data = app.scrape_url(
    "https://store.example.com/products",
    params={"formats": ["json"], "jsonOptions": {"schema": schema}},
)["json"]
```

### 3. Crawl an entire site

```python
crawl = app.crawl_url(
    "https://docs.example.com",
    params={
        "limit": 50,
        "maxDepth": 3,
        "includePaths": ["/docs/*"],
        "excludePaths": ["/docs/changelog*"],
    },
    wait_until_done=True,
)
docs = crawl.get("data", [])
```

### 4. Search the web (Firecrawl Search)

```python
results = app.search("best free markdown editors", limit=5)
for r in results.get("data", []):
    print(r.get("title"), "->", r.get("url"))
    print(r.get("markdown", "")[:500])
```

### 5. Map a site's URL structure

```python
site_map = app.map_url("https://example.com")
urls = site_map.get("links", [])
```

## Anti-patterns

- ❌ Writing a custom scraper when the goal is just "content in markdown" — Firecrawl does this in one call
- ❌ Scraping one page with Firecrawl when a static HTML file is already local — just Read it
- ❌ Storing the API key in code — always use env vars; `.env` is gitignored
- ❌ Forgetting `onlyMainContent: True` for blog/article pages — keeps navigation junk out
- ❌ Ignoring the `statusCode` / `error` field in responses — Firecrawl returns structured errors, not exceptions

## Rules

- ALWAYS keep `FIRECRAWL_API_KEY` out of code and out of git (env var only)
- RESPECT robots.txt and site ToS; respect `includePaths`/`excludePaths` and `limit` on crawls
- NEVER scrape protected or gated content without authorization
- VALIDATE schema output before passing structured data downstream
- FALL BACK to `browser-agent` or `webapp-testing` (Playwright) for interactive flows — Firecrawl is read-only content conversion, not a browser automation agent

## Integration with Other Skills

- **browser-agent**: fallback/alternative for JS-heavy interactive scraping
- **webapp-testing**: use Playwright when the target is a local dev server, not a live URL
- **claude-api**: send Firecrawl markdown into the model context for summarization/extraction
- **pdf**: OCR + Firecrawl for hybrid document/content pipelines

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad/missing key | Verify `FIRECRAWL_API_KEY` |
| 500 from self-hosted | Missing LLM provider keys | Set them in `.env`, restart |
| Empty markdown | JS wall or 404 | Try `formats: ["html"]`, check `statusCode` |
| Crawl slow | Too many pages | Lower `limit`, narrow `includePaths` |
