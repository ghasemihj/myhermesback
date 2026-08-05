# Search Engine Access Status for OSINT (Curl-based)

Last verified: **August 5, 2026**

## Access Matrix

| Engine | Method | Status | Notes |
|--------|--------|--------|-------|
| **Google News RSS** | `news.google.com/rss/search?q=...` | ✅ WORKING | Primary tool. Structured XML. Supports multi-language. |
| **Brave Search (HTML)** | `search.brave.com/search?q=...&source=web` | ✅ WORKING | Best fallback. Returns real article URLs. No CAPTCHA. |
| **Wikipedia MediaWiki API** | `en.wikipedia.org/w/api.php?action=query...` | ✅ WORKING | Full article text extraction. Excellent for context. |
| **DuckDuckGo Lite** | `lite.duckduckgo.com/lite/?q=...` | ❌ BLOCKED | Returns CAPTCHA ("select all squares containing a duck"). Confirmed Aug 2026. |
| **DuckDuckGo HTML** | `html.duckduckgo.com/html/?q=...` | ❌ BLOCKED | Same CAPTCHA challenge. Do not retry. |
| **Google Direct** | `google.com/search?q=...` | ❌ BLOCKED | Returns empty results or redirect for curl. |
| **Bing** | `bing.com/search?q=...` | ⚠️ PARTIAL | Returns some URLs but minimal useful content. Unreliable. |
| **Brave Search (JSON)** | `search.brave.com/search?q=...&format=json` | ⚠️ UNCERTAIN | May work but not tested as primary method. HTML mode is proven. |

## Web Search Fallback Priority (OSINT)

When the user asks for web search / social media signals / news discovery:

1. **Google News RSS** — structured, reliable, multi-language, supports `site:` queries
2. **Brave Search HTML** — catches what Google News RSS misses; good for X/Twitter post IDs cited in articles
3. **Direct source RSS feeds** — IRNA, ISNA, BBC, Al Jazeera, gCaptain, OilPrice
4. **Telegram web scraping** — `t.me/s/<channel>` for real-time OSINT channels
5. **ISW/CTP page scraping** — `understandingwar.org` and `criticalthreats.org` daily updates contain 100+ cited source URLs
6. **Wikipedia MediaWiki API** — background context for ongoing events
7. **xurl API** — direct X/Twitter search (requires auth setup)

## What Each Engine Is Good For

| Task | Best Engine |
|------|-------------|
| Breaking news discovery | Google News RSS |
| Finding article URLs on a topic | Brave Search HTML |
| Finding X/Twitter post IDs in analyses | Brave Search HTML (finds ISW citations of X posts) |
| Finding niche social media accounts | xurl API or ISW citations (web search fails) |
| Multi-language coverage | Google News RSS (set `ceid=IR:fa`, `SA:ar`, etc.) |
| Background context | Wikipedia MediaWiki API |
| Telegram channel content | Direct `t.me/s/` scraping |
| Maritime/shipping news | gCaptain RSS + OilPrice RSS |

## Search Query Patterns for Brave Search

```bash
# General topic search
curl -s 'https://search.brave.com/search?q=Iran+Strait+of+Hormuz+incident+2026' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'

# Site-specific (find X/Twitter posts cited in articles)
curl -s 'https://search.brave.com/search?q=%22sentdefender%22+Iran+2026' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'

# Find ISW/CTP daily updates
curl -s 'https://search.brave.com/search?q=site:understandingwar.org+Iran+update+August+2026' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'

# Find specific Telegram channel mentions on the web
curl -s 'https://search.brave.com/search?q=site:t.me+Iran+war+2026' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
```

## URL Extraction Pattern

Brave Search HTML returns URLs mixed with Brave CDN/asset URLs. Filter with:

```bash
grep -oP 'https?://[^"<>]+' | \
  grep -v brave | grep -v cdn | grep -v w3.org | grep -v wikidata | \
  grep -v assets | grep -v media | grep -v static | grep -v i\.ytimg | \
  sort -u
```
