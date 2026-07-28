# DeFi Providers

DeFi data providers extracted from the AI Operating System (AIOS).

These providers follow the `BaseDefiProvider` ABC pattern defined in `base_provider.py`, which provides:

- **`ProviderResponse`** — Normalized response dataclass with raw data, warnings, and cache status
- **`BaseDefiProvider`** — Abstract base class with built-in caching, forced refresh, and availability checks
- Abstract methods: `get_name()`, `fetch_data()`, `parse_data()`

## Providers

| Provider | File | Description |
|----------|------|-------------|
| CoinGecko | `coingecko_provider.py` | CoinGecko API data |
| DeFiLlama | `defillama_provider.py` | DeFiLlama protocol/TVL data |
| DexScreener | `dexscreener_provider.py` | DEX pair and token data |

## Usage

```python
from opencode_core.providers.base_provider import BaseDefiProvider, ProviderResponse
from opencode_core.providers.defillama_provider import DefiLlamaProvider

provider = DefiLlamaProvider()
response: ProviderResponse = provider.get_data()
print(response.normalized)
```

Forced refresh (bypasses cache):

```python
response = provider.get_data(force_refresh=True)
```

## Adding a New Provider

1. Create a new file `your_provider.py`
2. Subclass `BaseDefiProvider`
3. Implement `get_name()`, `fetch_data()`, and `parse_data()`
4. Import and use as shown above
