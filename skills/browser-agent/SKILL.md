---
name: browser-agent
description: Browser automation agent for web browsing, scraping, OCR, screenshots, downloading, and JSON extraction with proxy and session support. Use when tasks involve web content, data extraction, or browser automation.
user-invokable: true
allowed-tools: Read, Grep, Glob, Task
metadata:
  keywords: [browser, web, scrape, ocr, screenshot, download, search, extract, proxy, session, automation]
---

# Browser Agent Skill

## Purpose

The Browser Agent provides comprehensive web automation capabilities including:
- **Browse**: Navigate to URLs and extract page content (text, links, images, metadata)
- **Scrape**: Structured data extraction using CSS/XPath selectors
- **OCR**: Extract text from images and PDFs using multiple OCR backends
- **Screenshot**: Capture full-page or viewport screenshots
- **Download**: Download files from URLs with proxy support
- **Search**: Automated web search (Google, DuckDuckGo)
- **Extract JSON**: Extract structured JSON data from web pages

## Capabilities

| Capability | Description | Requires |
|------------|-------------|----------|
| browse | Navigate URLs, extract content | Playwright (optional) |
| scrape | CSS/XPath selector extraction | Playwright or requests |
| ocr | Text extraction from images/PDFs | OCR backend (Tesseract, EasyOCR, etc.) |
| screenshot | Capture web page screenshots | Playwright |
| download | Download files from URLs | requests |
| search | Web search automation | Playwright or requests |
| extract_json | Structured JSON extraction | Playwright or requests |

## Task Structure

All tasks follow this JSON structure:

```json
{
  "type": "<task_type>",
  "url": "https://example.com",
  "proxy": "protocol://host:port:username:password",
  "session": "session_name",
  "<additional_params>": "<value>"
}
```

## Task Types & Parameters

### 1. Browse

Navigate to URL and extract content.

```json
{
  "type": "browse",
  "url": "https://example.com",
  "extract_links": true,
  "extract_images": true,
  "extract_meta": true,
  "proxy": "socks5://proxy:1080",
  "session": "my_session"
}
```

**Parameters:**
- `url` (required): Target URL
- `extract_links` (optional): Extract all links (default: false)
- `extract_images` (optional): Extract all images (default: false)
- `extract_meta` (optional): Extract meta tags (default: false)
- `proxy` (optional): Proxy configuration
- `session` (optional): Session name for persistence

**Output:**
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "html_length": 12345,
  "text": "Extracted text content...",
  "links": [{"text": "Link Text", "url": "/path"}],
  "images": [{"src": "/image.png", "alt": "Alt text"}],
  "meta": {"description": "...", "keywords": "..."}
}
```

### 2. Scrape

Structured data extraction with selectors.

```json
{
  "type": "scrape",
  "url": "https://example.com/data",
  "selector": "table.data-table",
  "selector_type": "css",
  "extract": "table",
  "proxy": "http://proxy:8080"
}
```

**Parameters:**
- `url` or `html` (required): Target URL or HTML content
- `selector` (optional): CSS or XPath selector
- `selector_type` (optional): "css" or "xpath" (default: "css")
- `extract` (optional): "text", "table", "links", "images" (default: "text")
- `proxy` (optional): Proxy configuration

**Output:**
```json
{
  "url": "https://example.com/data",
  "data": "Extracted content or structured data"
}
```

### 3. OCR

Extract text from images or PDFs.

```json
{
  "type": "ocr",
  "file_path": "/path/to/image.png",
  "lang": "eng",
  "preprocess": "threshold",
  "backend": "tesseract"
}
```

Or from URL:
```json
{
  "type": "ocr",
  "url": "https://example.com/document.pdf",
  "lang": "eng+ita",
  "backend": "easyocr"
}
```

**Parameters:**
- `file_path` or `url` (required): Source file or URL
- `lang` (optional): Language(s) for OCR (default: "eng")
- `preprocess` (optional): Image preprocessing mode ("threshold", "denoise", "sharpen")
- `backend` (optional): OCR backend ("auto", "tesseract", "easyocr")
- `proxy` (optional): Proxy for URL downloads

**Output:**
```json
{
  "text": "Extracted text...",
  "confidence": 0.95,
  "source_file": "/path/to/file"
}
```

### 4. Screenshot

Capture web page screenshot.

```json
{
  "type": "screenshot",
  "url": "https://example.com",
  "output_path": "/path/to/screenshots",
  "full_page": true,
  "width": 1920,
  "height": 1080
}
```

**Parameters:**
- `url` (required): Target URL
- `output_path` (optional): Output directory (default: ./screenshots)
- `full_page` (optional): Capture full page (default: true)
- `width` (optional): Viewport width (default: 1280)
- `height` (optional): Viewport height (default: 720)

**Output:**
```json
{
  "url": "https://example.com",
  "file_path": "/path/to/screenshots/screenshot_1234567890.png",
  "full_page": true
}
```

### 5. Download

Download file from URL.

```json
{
  "type": "download",
  "url": "https://example.com/file.pdf",
  "output_dir": "/path/to/downloads",
  "filename": "document.pdf",
  "proxy": "socks5://proxy:1080"
}
```

**Parameters:**
- `url` (required): File URL
- `output_dir` (optional): Output directory (default: ./downloads)
- `filename` (optional): Custom filename (default: auto-detect)
- `proxy` (optional): Proxy configuration

**Output:**
```json
{
  "url": "https://example.com/file.pdf",
  "file_path": "/path/to/downloads/document.pdf",
  "file_size": 1234567,
  "content_type": "application/pdf"
}
```

### 6. Search

Automated web search.

```json
{
  "type": "search",
  "query": "python web scraping best practices",
  "num_results": 10,
  "proxy": "http://proxy:8080"
}
```

**Parameters:**
- `query` (required): Search query
- `num_results` (optional): Number of results (default: 5)
- `proxy` (optional): Proxy configuration

**Output:**
```json
{
  "query": "python web scraping best practices",
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com/article",
      "snippet": "Brief description..."
    }
  ]
}
```

### 7. Extract JSON

Extract structured JSON data from web pages.

```json
{
  "type": "extract_json",
  "url": "https://api.example.com/data",
  "selectors": {
    "title": "h1.main-title",
    "items": ".product-item",
    "price": ".price-value"
  }
}
```

**Parameters:**
- `url` or `html` (required): Target URL or HTML content
- `selectors` (optional): Named CSS selectors for extraction
- `proxy` (optional): Proxy configuration

**Output:**
```json
{
  "url": "https://api.example.com/data",
  "structured_data": {...},
  "extracted": {
    "title": "Extracted Title",
    "items": ["item1", "item2"],
    "price": "$29.99"
  }
}
```

## Proxy Configuration

Proxies support multiple formats:

```json
// String format
"proxy": "socks5://user:pass@proxy.example.com:1080"

// Object format
"proxy": {
  "protocol": "socks5",
  "host": "proxy.example.com",
  "port": 1080,
  "username": "user",
  "password": "pass"
}

// Supported protocols
- http://
- https://
- socks4://
- socks5://
```

**Proxy Features:**
- Automatic proxy rotation on failure
- Success/failure tracking
- Protocol-specific configuration for Playwright and requests

## Session Management

Sessions persist browser state (cookies, localStorage) across requests.

```json
// Save session
{
  "type": "browse",
  "url": "https://example.com/login",
  "session": "user_session"
}

// Restore session
{
  "type": "browse",
  "url": "https://example.com/dashboard",
  "session": "user_session"
}
```

**Session Features:**
- Cookie persistence
- Playwright state restoration
- Automatic expiration
- Storage in project sessions directory

## Orchestrator Integration

### Routing Keywords

Add these keywords to the orchestrator routing table:

| Keyword | Agent | Model |
|---------|-------|-------|
| browse, browsing, webpage, website | Browser Agent | inherit |
| scrape, scraping, extraction, parse | Browser Agent | inherit |
| ocr, text extraction, image to text | Browser Agent | inherit |
| screenshot, capture, screen grab | Browser Agent | inherit |
| download, fetch file, retrieve file | Browser Agent | inherit |
| search, web search, google, duckduckgo | Browser Agent | inherit |
| extract json, structured data, json extraction | Browser Agent | inherit |
| proxy, socks, http proxy | Browser Agent | inherit |
| session, cookies, persistence | Browser Agent | inherit |

### Usage Examples

**Basic Web Scraping:**
```
User: "Scrape product data from https://shop.example.com/products"
-> Route to Browser Agent
-> Task: {type: "scrape", url: "...", selector: ".product", extract: "table"}
```

**OCR on PDF:**
```
User: "Extract text from this invoice PDF"
-> Route to Browser Agent
-> Task: {type: "ocr", url: "https://example.com/invoice.pdf", lang: "eng"}
```

**Screenshot with Proxy:**
```
User: "Take screenshot of competitor site via proxy"
-> Route to Browser Agent
-> Task: {type: "screenshot", url: "...", proxy: "socks5://..."}
```

**Multi-step with Sessions:**
```
User: "Login to dashboard and extract data"
-> Route to Browser Agent
-> Step 1: {type: "browse", url: "/login", session: "dash"}
-> Step 2: {type: "scrape", url: "/dashboard", session: "dash"}
```

## Dependencies

**Required:**
- Python 3.8+
- requests
- beautifulsoup4

**Optional (recommended):**
- playwright (for JS-rendered pages, screenshots)
- tesseract-ocr or easyocr (for OCR)
- Pillow (for image preprocessing)

**Installation:**
```bash
pip install requests beautifulsoup4
pip install playwright && playwright install
pip install pytesseract  # or easyocr
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Playwright not available | Not installed | `pip install playwright && playwright install` |
| OCR backend failed | Missing dependencies | Install tesseract or easyocr |
| Proxy connection failed | Invalid proxy | Check proxy configuration |
| Session not found | Session expired | Create new session |
| Rate limited | Too many requests | Add delays, use proxy rotation |

## Integration with Other Skills

- **code-review**: Review extracted code snippets
- **plan**: Plan multi-step scraping workflows
- **testing-strategy**: Test scraping selectors
- **debugging**: Debug extraction failures

## Rules

- NEVER scrape protected content without authorization
- ALWAYS respect robots.txt unless explicitly authorized
- USE sessions for login-required content
- ROTATE proxies for large-scale scraping
- ADD delays between requests to avoid rate limiting
- VALIDATE extracted data before processing
- CLEAN UP temporary files after OCR processing

## Troubleshooting

**Playwright won't initialize:**
```bash
playwright install chromium
```

**OCR returns empty text:**
- Check image quality
- Try different preprocessing mode
- Verify language support

**Proxy not working:**
- Test proxy manually first
- Check protocol support (socks5 requires specific setup)
- Verify authentication credentials

**Session not persisting:**
- Check sessions directory permissions
- Verify session name consistency
- Clear expired sessions