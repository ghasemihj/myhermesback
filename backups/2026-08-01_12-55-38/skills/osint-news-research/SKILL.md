---
name: osint-news-research
description: RSS news research and multi-source verification.
---

# OSINT News Research

Investigative news search and multi-source verification. Builds source-backed briefings with original quotes, timestamps, and provenance chains.

## Core Method 1: Direct Source RSS Feeds

When the user provides specific RSS feed URLs (or you know them), fetch and parse them directly. This gives you the outlet's own editorial ordering, full descriptions, and exact pubDates — no Google News intermediary or redirect links.

**Iranian state media RSS feeds (all use Saba Enterprise CMS — identical XML structure):**

| Outlet | RSS URL | Language | Notes |
|--------|---------|----------|-------|
| IRNA English | `https://en.irna.ir/rss` | EN | Most comprehensive; includes photo items |
| ISNA English | `https://en.isna.ir/rss` | EN | Good political/war coverage |
| Khabaronline | `https://www.khabaronline.ir/rss` | FA | Farsi; requires translation step |

Fetch: `curl -sL --max-time 30 -A 'Mozilla/5.0' '<RSS_URL>' > /tmp/news_<name>.txt`

XML item structure (consistent across all three):
```xml
<item>
  <title>Headline text</title>
  <link>https://...</link>
  <pubDate>Sat, 01 Aug 2026 07:26:34 GMT</pubDate>
  <description>200-char summary</description>
  <category domain="...">Section</category>
  <enclosure url="..." length="..." type="image/jpeg" />
</item>
```

Quick triage: `grep -oP '<title>[^<]+</title>'` for headlines. Full extraction: Python regex on `<item>` blocks for all fields.

**When to use direct RSS vs Google News RSS:**
- **Direct RSS**: User asks about specific outlets, or you need a comprehensive scan of one source's coverage
- **Google News RSS**: User asks about a topic and wants cross-outlet coverage, or the topic isn't well-covered by a single outlet's RSS

**Other known RSS feeds (not Saba CMS):**
- Many Iranian government ministries and agencies have RSS feeds under similar URL patterns
- International outlets: BBC, Al Jazeera, Reuters all have RSS — but Reuters is often blocked (see access table)

## Core Method 2: Google News RSS

Google News RSS is the primary tool for cross-outlet topic searches. It returns structured XML with titles, dates, source names, and redirect links.

```
curl -s "https://news.google.com/rss/search?q=<QUERY>&hl=en-US&gl=US&ceid=US:en" -o /tmp/results.xml
```

Parameters: `q` (query), `hl` (language), `gl` (country), `ceid` (country:lang code like US:en, IR:fa).

## Workflow

### Phase 1: Broad Discovery (3-5 parallel searches in one turn)
1. Main topic query
2. Specific outlet queries
3. Quote searches
4. Language variants
5. Related angle queries

### Phase 2: Source Verification
- Primary source (who broke it first, timestamp)
- Secondary sources (who confirmed)
- Official statements (exact quotes)

Sort by pubDate to find the original vs. citations.

### Phase 3: HTML Index Page Extraction (for non-RSS sources)

When scraping a news section/index page (not individual articles), extract article cards:

**Al Jazeera index pages** (`/where/iran/`, `/news/middle-east/`, etc.):
```
# Title + URL pattern:
grep -oP 'article-card__link" href="([^"]+)"[^>]*><h2[^>]*><span>([^<]+)' 
# Date pattern:
grep -oP 'Published On ([^<]+)'
```

The HTML structure nests `<a class="article-card__link">` → `<h2 class="article-card__title"><span>TITLE</span></a>` with dates in `<span class="screen-reader-text">Published On DATE</span>`.

**Shana (Iranian oil ministry news — shana.ir):**
Partially accessible via curl. Headlines extractable via `<a href="/news/...">TITLE</a>` patterns, but the site is JS-heavy so not all content loads. The homepage shows headline cards — parse `<h2>`, `<h3>` tags and `<a>` links with `/news/` in the href.

**AP News (apnews.com):**
Fully JavaScript-rendered SPA. **No article data in static HTML** — curl returns only the shell with no headline content. No RSS feed at the standard hub URL. Must use Google News RSS or other aggregator to get AP Middle East coverage.

### Phase 4: Article Content Extraction
Fallback chain for blocked sites (ordered by reliability, tested July–Aug 2026):
1. **Al Jazeera article pages** — regular `/news/YYYY/MM/DD/` URLs return full `<p>` content via curl. Liveblog pages do NOT (JS-rendered shell only). Most reliable for Middle East coverage.
2. **Iran International** — article pages return full `<p>` content (Next.js but server-rendered). Excellent for Iran-specific stories.
3. **`og:description` meta tag extraction** — when full article body is blocked, extract `<meta property="og:description" content="...">`. Gives 200–500 word summary. Works on most sites including some that block body content.
4. **RSS description snippets** — always available from Google News RSS `<description>` field. Strip HTML tags, gives ~200 chars.
5. **Wikipedia MediaWiki API** — for background context on ongoing events (see Supplementary Tools below).
6. **Wayback Machine snapshots** — may have recent snapshots of blocked articles.

### Phase 5: Quote Extraction
Search for patterns: `Trump said`, `White House`, `sources said`, etc.

## Common Pitfalls

1. **Cloudflare/CAPTCHA blocking** — Axios, WSJ, NYT, WaPo, JPost, **Reuters** all block. Reuters returns a Cloudflare JS challenge page (~773 bytes). Use secondary sources or Google News RSS for Reuters content.
2. **Fully JS-rendered sites** — **AP News** (apnews.com) renders all article content via JavaScript; curl returns an empty shell. No RSS feed at hub URLs. Always use an aggregator (Google News RSS) to get AP stories. Also blocked: UPI, Yahoo News, Daily Sabah (all return shells with no article content).
3. **Empty RSS feeds** — Some language combos return empty XML. Check file size.
4. **Security scanner flags `curl | python3`** — `curl ... | python3 -c` pipelines get flagged by the security scanner with `[HIGH] Pipe to interpreter` warnings. They still work (auto-approved by smart approval in most sessions), but add latency and noise. Two workarounds: (a) use `curl -o /tmp/file.html` then parse separately, or (b) accept the flag if speed matters more than clean logs. In subagent/cron mode the flag still auto-approves.
5. **Duplicate results** — Same story under different headlines. Sort by pubDate.
6. **Heredoc issues** — Write extraction scripts via write_file, run via terminal.
7. **`execute_code` blocked in subagent/cron mode** — When running as a subagent (or in cron), `execute_code` is blocked by the security sandbox. Do NOT attempt batched Python+curl pipelines via execute_code in these contexts. Instead, make multiple parallel `terminal()` calls with individual `curl` commands. This works fine — terminal() is not blocked in subagent mode. Plan your queries upfront and issue them as parallel terminal() calls in one assistant turn.
8. **RSS `head -c` truncation is fine for triage** — When scanning many RSS feeds, pipe through `head -c 10000` or similar to get just the first 20-30 items. Full XML is often 100KB+. You don't need to parse every `<item>` — the first page of results sorted by relevance gives you the key stories. Parse the XML in a follow-up call only if you need specific fields.

## Supplementary Search Tools

### Wikipedia MediaWiki API
For ongoing conflicts/events, Wikipedia often has the most comprehensive, continuously-updated article. Use the MediaWiki API to extract full text (far more than curl scraping the HTML page):

```
curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=<ARTICLE>&prop=extracts&explaintext=true&format=json" -H "User-Agent: HermesBot/1.0"
```

Parse with Python to search for specific keywords/topics within the article. This is especially valuable for:
- Ongoing wars and conflicts (e.g., `2026_Iran_war`)
- Geopolitical events with Wikipedia infoboxes
- Historical context and timeline reconstruction

### Brave Search (secondary engine)
Returns structured JSON with search results, news, videos, and knowledge graph infoboxes:

```
curl -sL "https://search.brave.com/search?q=<QUERY>&format=json" -H "User-Agent: Mozilla/5.0"
```

Useful for: knowledge graph data, finding article URLs, getting overview of a topic when Google News is insufficient.

## Parallel Subagent Pattern

For complex OSINT tasks, dispatch 2-3 subagents simultaneously to cover different research angles:

| Subagent | Research angle | Example queries |
|----------|---------------|-----------------|
| **Military/OSINT** | Force movements, satellite imagery, deployments | carrier groups, bomber deployments, OPSEC indicators |
| **Diplomatic/Political** | Statements, negotiations, sanctions | official quotes, UN votes, ceasefire talks |
| **Economic/Market** | Oil prices, shipping, supply chains | Brent crude, Hormuz traffic, energy market |

Each subagent should:
- Use Google News RSS for discovery
- Write findings to a structured file
- Return a summary with source chain

## Intelligence Briefing Format

For geopolitical/OSINT briefings, use this structure:

1. **Threat level banner** — color-coded (green/yellow/orange/red) with one-line summary
2. **Timeline** — chronological event log with exact UTC timestamps, sorted newest-first within each section
3. **Source verification table** — claim, source, timestamp, confidence. For breaking stories, cite 3+ independent sources to establish credibility
4. **Force comparison table** — capabilities, deployments, losses (if relevant)
5. **Diplomatic/political developments** — statements, negotiations, sanctions
6. **Economic/market impact** — oil prices, shipping disruptions, sanctions effects
7. **Scenario analysis** — probability-weighted outcomes
8. **Key indicators** — early warning signs, both positive and negative

Use tables liberally. User expects structured, tabular output with exact timestamps. For breaking news briefings where information is still emerging, group by topic (military, diplomatic, economic) rather than strict chronology.

## Output Format
1. Source chain with timestamps
2. Exact quotes with attribution
3. Claims verification table
4. Background context
5. Caveats
