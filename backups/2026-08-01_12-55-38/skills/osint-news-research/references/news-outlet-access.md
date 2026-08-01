# News Outlet Access Patterns

Patterns observed during automated news research (July 2026). These are NOT permanent tool capabilities — they reflect current anti-bot measures that change over time.

## Sites That Block Automated Access (Cloudflare/JS Challenge)

These sites serve a JS challenge page instead of article content when accessed via curl:

| Outlet | Status | Notes |
|--------|--------|-------|
| Axios | Cloudflare | Full JS challenge page |
| WSJ (wsj.com) | Cloudflare | Requires JS, serves minimal error |
| NYT (nytimes.com) | Cloudflare | Serves tiny redirect page |
| WaPo (washingtonpost.com) | Cloudflare | JS challenge |
| **Reuters (reuters.com)** | **Cloudflare CAPTCHA** | **Returns ~773-byte JS challenge with `captcha-delivery.com`. Tested Jul 2026. Use Google News RSS for Reuters content.** |
| JPost (jpost.com) | Cloudflare | 117KB challenge page |
| Fortune | Cloudflare | JS challenge |
| Forth.News | Vercel Security | JS checkpoint |
| Times of Israel | Cloudflare | Full captcha page |
| **AP News (apnews.com)** | **Fully JS-rendered SPA** | **No article data in static HTML. Hub pages (e.g. `/hub/middle-east`) return only the page shell. No RSS feed at hub URLs. Must use Google News RSS to get AP stories.** |
| CBS News (cbsnews.com) | Returns empty (0 bytes) | May require cookies/JS |
| Townhall | Returns minimal page | JS challenge |
| Breitbart | Returns minimal page | JS challenge |
| The Hill (thehill.com) | px-captcha | Returns CAPTCHA challenge page |
| Yahoo News (yahoo.com) | Returns generic shell | No article content in HTML |
| UPI (upi.com) | Returns generic shell | No article content in HTML |
| Daily Sabah (dailysabah.com) | Returns generic shell | No article content in HTML |
| OilPrice.com | Returns boilerplate only | Article text in JS-loaded components |
| Washington Examiner | Returns empty/404 | Article pages not accessible |
| Times of Oman | Returns empty | Article pages not accessible |
| CNN liveblog | 404 on dated URLs | URL pattern changes daily |

## Sites That Serve Content (Accessible via curl)

These sites served full HTML article content that could be extracted:

| Outlet | Accessible | Notes |
|--------|-----------|-------|
| **Al Jazeera** (aljazeera.com) | ✅ **Article pages + index pages** | Regular `/news/YYYY/MM/DD/` URLs return full `<p>` content. **Liveblog pages do NOT** (return JS shell only). Index pages (`/where/iran/`) expose article card links/titles/dates in HTML. Most reliable for Middle East conflict coverage. |
| **Iran International** (iraninternational.com) | ✅ **Full articles** | Next.js but server-rendered. Full `<p>` content extractable from article pages. Excellent for Iran-specific analysis. Also extractable: `og:title`, `og:description` from any page. |
| Middle East Monitor (middleeastmonitor.com) | ✅ Full HTML | Article text extractable via regex |
| NewsNation | ✅ | Article content accessible |
| **IRNA English** (en.irna.ir) | ✅ **RSS feed** | `https://en.irna.ir/rss` — full XML with title, link, pubDate, description, category, enclosure. Saba Enterprise CMS. |
| **ISNA English** (en.isna.ir) | ✅ **RSS feed** | `https://en.isna.ir/rss` — same Saba CMS structure as IRNA. |
| **Khabaronline** (khabaronline.ir) | ✅ **RSS feed** | `https://www.khabaronline.ir/rss` — Farsi content. Same Saba CMS structure. |
| **Shana** (shana.ir) | ✅ **Partial** | Iranian oil ministry news. Homepage headline cards extractable via `<a href="/news/...">` + `<h2>/<h3>` patterns. JS-heavy — not all content loads in curl. |

## Working Extraction Pattern

```python
import re

with open('/tmp/article.html') as f:
    html = f.read()

# Strip scripts and styles
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'&#x27;', "'", text)
text = re.sub(r'&quot;', '"', text)
text = re.sub(r'&nbsp;', ' ', text)
text = re.sub(r'\s+', ' ', text).strip()

# Find article content by searching for keywords
for kw in ['energy', 'Trump said', 'White House', 'sources']:
    idx = text.lower().find(kw.lower())
    if idx > 0:
        print(text[max(0,idx-200):idx+1000])
```

## Iranian State Media RSS Extraction Pattern

All three Saba Enterprise CMS feeds (IRNA, ISNA, Khabaronline) share identical XML structure. Two-pass approach:

**Pass 1 — Quick triage (headline scan):**
```bash
cat /tmp/news_irna.txt | grep -oP '<title>[^<]+</title>'
```

**Pass 2 — Full structured extraction:**
```python
import re
with open('/tmp/news_irna.txt') as f:
    content = f.read()
items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
for i, item in enumerate(items[:10]):
    title = re.search(r'<title>([^<]+)</title>', item)
    link = re.search(r'<link>([^<]+)</link>', item)
    date = re.search(r'<pubDate>([^<]+)</pubDate>', item)
    desc = re.search(r'<description>([^<]+)</description>', item)
    print(f"{i+1}. [{date.group(1) if date else ''}] {title.group(1) if title else ''}")
    print(f"   URL: {link.group(1) if link else ''}")
    print(f"   Desc: {desc.group(1)[:200] if desc else ''}")
```

## Al Jazeera Index Page Extraction Pattern

Extract article cards from Al Jazeera section/index pages (e.g. `/where/iran/`, `/news/middle-east/`):

**Title + URL:**
```python
articles = re.findall(r'article-card__link" href="([^"]+)"[^>]*><h2[^>]*><span>([^<]+)</span>', content)
```

**Dates (screen-reader text):**
```python
dates = re.findall(r'Screen-reader-text">Published On ([^<]+)', content)
```

**Full extraction loop:**
```python
for i, (url, title) in enumerate(articles):
    date = dates[i] if i < len(dates) else 'unknown'
    print(f'{i+1}. [{date}] {title}')
    print(f'   URL: https://www.aljazeera.com{url}')
```

## Google News RSS — Additional Patterns

### Language/country codes that work
| Code | Language/Region | Notes |
|------|----------------|-------|
| `US:en` | English (US) | Most results |
| `IR:fa` | Persian (Iran) | May be geo-restricted from non-Iran IPs |
| `GB:en` | English (UK) | Good for BBC, Guardian, Reuters |
| `TR:tr` | Turkish | Anadolu, Daily Sabah coverage |
| `IL:en` | English (Israel) | Times of Israel, Jerusalem Post |

### Multi-query strategy for breaking news
Run 3-5 parallel RSS searches covering different angles:
```
q=<main topic>
q=<specific outlet> + <topic>
q=<key quote or official name>
q=<opposing perspective>
q=<related country or region>
```
This catches stories that use different headline framing for the same event.

## Wikipedia API — Full Article Extraction

For ongoing wars/conflicts, Wikipedia's article is often the single best source of consolidated, sourced information. The MediaWiki API returns clean plaintext:

```bash
curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=2026_Iran_war&prop=extracts&explaintext=true&format=json" \
  -H "User-Agent: HermesBot/1.0"
```

Then use Python to search within the text for specific keywords:
```python
import json
data = json.loads(response)
for page in data['query']['pages'].values():
    text = page.get('extract', '')
    # Search for specific topics within the article
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'energy' in line.lower() or 'power plant' in line.lower():
            print('\n'.join(lines[max(0,i-1):i+3]))
```

This approach found complete timeline of the 2026 Iran war including all energy infrastructure strikes, diplomatic events, and casualty data in a single API call.

## Reliable Fallback Chain

1. **Google News RSS descriptions** — always works, gives headline + snippet + source
2. **Al Jazeera article pages** — most reliable for Middle East breaking news, full `<p>` content
3. **Iran International article pages** — excellent for Iran-specific analysis, full content
4. **`og:description` meta tag extraction** — works on many sites even when body is blocked. Gives 200–500 word summary:
   ```python
   ogdesc = re.findall(r'content="([^"]+)"[^>]*property="og:description"', html)
   ogtitle = re.findall(r'content="([^"]+)"[^>]*property="og:title"', html)
   ```
5. **Wikipedia MediaWiki API** — for comprehensive background on ongoing events
6. **Middle East Monitor** — often reprints major stories, full HTML accessible
7. **Anadolu Agency** — often carries the same story (article pages now blocked, but homepage may have snippets)
8. **Wayback Machine** — may have snapshots of recently published articles
9. **Brave Search** — secondary search engine with structured results
