# Browser Agent Skill

## Overview

The Browser Agent skill provides comprehensive web automation capabilities for the orchestrator. It handles tasks involving web browsing, data extraction, OCR, screenshots, file downloads, and web searches.

## Quick Start

### Basic Usage

```bash
# Browse a website
/browse https://example.com

# Scrape a table from a webpage
/scrape https://example.com/data table.css-selector

# Extract text from an image
/ocr /path/to/image.png

# Take a screenshot
/screenshot https://example.com

# Download a file
/download https://example.com/file.pdf

# Search the web
/search-web "python web scraping best practices"
```

### Task Structure

All browser agent tasks use this JSON structure:

```json
{
  "type": "<task_type>",
  "url": "https://example.com",
  "proxy": "protocol://host:port",
  "session": "session_name",
  "<param>": "<value>"
}
```

## Capabilities

### 1. Browse

Navigate to URLs and extract page content.

**Parameters:**
- `url` (required): Target URL
- `extract_links` (optional): Extract all links (boolean)
- `extract_images` (optional): Extract all images (boolean)
- `extract_meta` (optional): Extract meta tags (boolean)
- `proxy` (optional): Proxy configuration
- `session` (optional): Session name for persistence

**Example:**
```json
{
  "type": "browse",
  "url": "https://example.com",
  "extract_links": true,
  "extract_images": true,
  "extract_meta": true,
  "session": "my_session"
}
```

### 2. Scrape

Structured data extraction using CSS or XPath selectors.

**Parameters:**
- `url` or `html` (required): Target URL or HTML content
- `selector` (optional): CSS or XPath selector
- `selector_type` (optional): "css" or "xpath" (default: "css")
- `extract` (optional): "text", "table", "links", "images" (default: "text")
- `proxy` (optional): Proxy configuration

**Example:**
```json
{
  "type": "scrape",
  "url": "https://example.com/products",
  "selector": "table.product-table",
  "extract": "table",
  "proxy": "http://proxy:8080"
}
```

### 3. OCR

Extract text from images or PDFs using OCR.

**Parameters:**
- `file_path` or `url` (required): Source file or URL
- `lang` (optional): Language(s) for OCR (default: "eng")
- `preprocess` (optional): Image preprocessing ("threshold", "denoise", "sharpen")
- `backend` (optional): OCR backend ("auto", "tesseract", "easyocr")
- `proxy` (optional): Proxy for URL downloads

**Example:**
```json
{
  "type": "ocr",
  "url": "https://example.com/document.pdf",
  "lang": "eng+ita",
  "backend": "easyocr"
}
```

### 4. Screenshot

Capture web page screenshots.

**Parameters:**
- `url` (required): Target URL
- `output_path` (optional): Output directory (default: ./screenshots)
- `full_page` (optional): Capture full page (default: true)
- `width` (optional): Viewport width (default: 1280)
- `height` (optional): Viewport height (default: 720)

**Example:**
```json
{
  "type": "screenshot",
  "url": "https://example.com",
  "full_page": true,
  "width": 1920,
  "height": 1080
}
```

### 5. Download

Download files from URLs.

**Parameters:**
- `url` (required): File URL
- `output_dir` (optional): Output directory (default: ./downloads)
- `filename` (optional): Custom filename (default: auto-detect)
- `proxy` (optional): Proxy configuration

**Example:**
```json
{
  "type": "download",
  "url": "https://example.com/report.pdf",
  "output_dir": "/tmp",
  "filename": "report_jan2024.pdf",
  "proxy": "socks5://proxy:1080"
}
```

### 6. Search

Automated web search.

**Parameters:**
- `query` (required): Search query
- `num_results` (optional): Number of results (default: 5)
- `proxy` (optional): Proxy configuration

**Example:**
```json
{
  "type": "search",
  "query": "python web scraping libraries",
  "num_results": 10,
  "proxy": "http://proxy:8080"
}
```

### 7. Extract JSON

Extract structured JSON data from web pages.

**Parameters:**
- `url` or `html` (required): Target URL or HTML content
- `selectors` (optional): Named CSS selectors for extraction
- `proxy` (optional): Proxy configuration

**Example:**
```json
{
  "type": "extract_json",
  "url": "https://api.example.com/products",
  "selectors": {
    "name": "h1.product-title",
    "price": ".price-value",
    "description": ".product-description"
  }
}
```

## Proxy Configuration

### String Format
```json
"proxy": "socks5://user:pass@proxy.example.com:1080"
```

### Object Format
```json
"proxy": {
  "protocol": "socks5",
  "host": "proxy.example.com",
  "port": 1080,
  "username": "user",
  "password": "pass"
}
```

### Supported Protocols
- `http://`
- `https://`
- `socks4://`
- `socks5://`

### Proxy Features
- Automatic rotation on failure
- Success/failure tracking
- Protocol-specific configuration

## Session Management

Sessions persist browser state (cookies, localStorage) across requests.

### Save Session
```json
{
  "type": "browse",
  "url": "https://example.com/login",
  "session": "user_session"
}
```

### Restore Session
```json
{
  "type": "browse",
  "url": "https://example.com/dashboard",
  "session": "user_session"
}
```

### Session Features
- Cookie persistence
- Playwright state restoration
- Automatic expiration
- Storage in project sessions directory

## Orchestrator Integration

### Routing Keywords

The browser agent is routed via these keywords:

| Keywords |
|----------|
| browse, browsing, webpage, website |
| scrape, scraping, extraction, parse |
| ocr, text extraction, image to text, pdf |
| screenshot, capture, screen grab |
| download, fetch file, retrieve file |
| search, web search, google, duckduckgo |
| extract json, structured data, json extraction |
| proxy, socks, http proxy |
| session, cookies, persistence |

### Slash Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/browse` | Browse a website | `/browse https://example.com` |
| `/scrape` | Scrape data from webpage | `/scrape https://example.com table` |
| `/ocr` | Extract text from image/PDF | `/ocr /path/to/file.png` |
| `/screenshot` | Capture screenshot | `/screenshot https://example.com` |
| `/download` | Download file | `/download https://example.com/file.pdf` |
| `/search-web` | Search the web | `/search-web "query"` |

## Multi-step Workflows

### Login and Extract Data
```json
// Step 1: Login
{
  "type": "browse",
  "url": "https://example.com/login",
  "session": "auth"
}

// Step 2: Access protected page
{
  "type": "scrape",
  "url": "https://example.com/dashboard",
  "session": "auth",
  "selector": ".data-table",
  "extract": "table"
}
```

### Scrape with Proxy and Session
```json
// Step 1: Initialize session via proxy
{
  "type": "browse",
  "url": "https://example.com/login",
  "proxy": "socks5://proxy:1080",
  "session": "proxy_session"
}

// Step 2: Scrape with same session
{
  "type": "scrape",
  "url": "https://example.com/data",
  "proxy": "socks5://proxy:1080",
  "session": "proxy_session",
  "selector": ".content"
}
```

## Dependencies

### Required
```bash
pip install requests beautifulsoup4
```

### Optional (Recommended)
```bash
# For JS-rendered pages and screenshots
pip install playwright
playwright install

# For OCR
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

## Best Practices

1. **Respect robots.txt** - Check before scraping
2. **Add delays** - Avoid rate limiting
3. **Use sessions** - For login-required content
4. **Rotate proxies** - For large-scale scraping
5. **Validate data** - Check extracted content
6. **Clean up** - Remove temporary files after OCR
7. **Handle errors** - Implement retry logic

## Examples

### E-commerce Price Monitoring
```json
{
  "type": "scrape",
  "url": "https://shop.example.com/products",
  "selector": ".product-card",
  "extract": "table",
  "proxy": "socks5://proxy:1080",
  "session": "shop_session"
}
```

### Document OCR Pipeline
```json
// Download PDF
{
  "type": "download",
  "url": "https://example.com/invoice.pdf",
  "output_dir": "/tmp/invoices"
}

// Extract text
{
  "type": "ocr",
  "file_path": "/tmp/invoices/invoice.pdf",
  "lang": "eng",
  "backend": "tesseract"
}
```

### Competitor Analysis
```json
// Take screenshots
{
  "type": "screenshot",
  "url": "https://competitor.com",
  "full_page": true,
  "output_path": "./screenshots/competitor"
}

// Extract data
{
  "type": "extract_json",
  "url": "https://competitor.com/products",
  "selectors": {
    "products": ".product-item",
    "prices": ".price"
  }
}
```

## Integration with Other Skills

- **code-review**: Review extracted code snippets
- **plan**: Plan multi-step scraping workflows
- **testing-strategy**: Test scraping selectors
- **debugging**: Debug extraction failures
- **security-scan**: Check for vulnerabilities in scraped data

## Troubleshooting

### Playwright Issues
```bash
# Reinstall browsers
playwright install --force

# Check browser path
playwright install --dry-run
```

### OCR Issues
```bash
# Test Tesseract
tesseract --version

# Check language packs
tesseract --list-langs

# Test EasyOCR
python -c "import easyocr; print('OK')"
```

### Proxy Issues
```bash
# Test proxy manually
curl -x socks5://proxy:1080 https://example.com

# Check proxy authentication
curl -x user:pass@proxy:8080 https://example.com
```

## Contributing

When adding new capabilities:
1. Update the SKILL.md documentation
2. Add task templates to task-templates.json
3. Update the orchestrator routing table
4. Add examples to this README
5. Test with various scenarios

## License

Part of the AI Operating System project.