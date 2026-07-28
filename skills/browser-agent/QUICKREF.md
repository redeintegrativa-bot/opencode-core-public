# Browser Agent Quick Reference

## Task Types

| Type | Description | Key Params |
|------|-------------|------------|
| `browse` | Navigate & extract content | `url`, `extract_links`, `extract_images`, `extract_meta` |
| `scrape` | Extract with selectors | `url`, `selector`, `selector_type`, `extract` |
| `ocr` | Extract text from images/PDFs | `file_path`/`url`, `lang`, `backend` |
| `screenshot` | Capture webpage | `url`, `full_page`, `width`, `height` |
| `download` | Download files | `url`, `output_dir`, `filename` |
| `search` | Web search | `query`, `num_results` |
| `extract_json` | Extract structured data | `url`, `selectors` |

## Common Patterns

### Basic Browse
```json
{"type": "browse", "url": "https://example.com"}
```

### Scrape Table
```json
{"type": "scrape", "url": "https://example.com/data", "selector": "table", "extract": "table"}
```

### OCR Image
```json
{"type": "ocr", "file_path": "/path/to/image.png"}
```

### Screenshot
```json
{"type": "screenshot", "url": "https://example.com", "full_page": true}
```

### Download
```json
{"type": "download", "url": "https://example.com/file.pdf"}
```

### Search
```json
{"type": "search", "query": "python scraping", "num_results": 10}
```

### Extract JSON
```json
{"type": "extract_json", "url": "https://example.com", "selectors": {"title": "h1"}}
```

## Proxy Formats

```json
// String
"proxy": "socks5://user:pass@host:port"

// Object
"proxy": {"protocol": "socks5", "host": "proxy.com", "port": 1080, "username": "user", "password": "pass"}
```

## Session Usage

```json
// Save
{"type": "browse", "url": "https://example.com/login", "session": "auth"}

// Restore
{"type": "browse", "url": "https://example.com/dashboard", "session": "auth"}
```

## Slash Commands

| Command | Usage |
|---------|-------|
| `/browse URL` | Browse website |
| `/scrape URL SELECTOR` | Scrape with selector |
| `/ocr FILE` | OCR file |
| `/screenshot URL` | Capture screenshot |
| `/download URL` | Download file |
| `/search-web QUERY` | Search web |

## Dependencies

```bash
pip install requests beautifulsoup4
pip install playwright && playwright install  # Optional
pip install pytesseract  # Optional
```

## Error Quick Fix

| Error | Fix |
|-------|-----|
| Playwright not found | `pip install playwright && playwright install` |
| OCR failed | `pip install pytesseract` or `pip install easyocr` |
| Proxy error | Check format: `protocol://[user:pass@]host:port` |
| Session lost | Re-authenticate with same session name