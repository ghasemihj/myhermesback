---
name: osint-news-research
description: RSS news research and multi-source verification.
---

# OSINT News Research

Investigative news search and multi-source verification. Builds source-backed briefings with original quotes, timestamps, and provenance chains.

## Core Method 1: Direct Source RSS Feeds

## Sites That Serve RSS Content (Accessible via curl)

These RSS feeds returned structured XML parseable by `ET.parse()` (or regex fallback):

| Outlet | RSS URL | Lang | Notes |
|--------|---------|------|-------|
| **IRNA English** | `https://en.irna.ir/rss` | EN | Most comprehensive Iranian official feed; includes photo items. Saba CMS. |
| **IRNA Persian** | `https://www.irna.ir/rss` | FA | Same Saba CMS structure, Persian content. |
| **ISNA English** | `https://en.isna.ir/rss` | EN | Good political/war coverage. Saba CMS. |
| **ISNA Persian** | `https://www.isna.ir/rss` | FA | ~30 items. Same Saba CMS, Persian. |
| **Khabaronline** | `https://www.khabaronline.ir/rss` | FA | Farsi; large feed (~50KB+). **Pitfall:** truncating with `head -c 50000` cuts XML mid-tag — use regex fallback parser. |
| **Khabarfoori** (khabarfoori.com) | Homepage scrape | FA | Not RSS. Headlines via curl, article links in `<a title="...">` attributes. |
| **Al Jazeera** | `https://www.aljazeera.com/xml/rss/all.xml` | EN | ~25 items. Full parse. Covers all AJ topics, not just ME. |
| **BBC Middle East** | `https://feeds.bbci.co.uk/news/world/middle_east/rss.xml` | EN | ~30 items. Excellent ME coverage. Most reliable international RSS. |
| **gCaptain** | `https://gcaptain.com/feed/` | EN | Maritime/shipping news. ~12 items. Excellent for Gulf maritime security, Hormuz traffic, tanker attacks, Red Sea shipping. **Key source for maritime angle on Iran/Gulf conflict.** |
| **OilPrice.com** | `https://oilprice.com/rss/main` | EN | Energy market news. ~15 items. Covers oil prices, OPEC, sanctions impact, Middle East energy disruption. |
| **Google News** | `https://news.google.com/rss/search?q=...` | Varies | Cross-outlet aggregator. See Core Method 2. |

Fetch: `curl -sL --max-time 30 -A 'Mozilla/5.0' '<RSS_URL>' > /tmp/news_<name>.xml`

XML item structure (consistent across Saba CMS feeds):
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

BBC and Google News use similar structure. gCaptain/OilPrice use standard RSS 2.0.

Quick triage: `grep -oP '<title>[^<]+</title>'` for headlines. Full extraction: Python regex on `<item>` blocks for all fields.

**When to use direct RSS vs Google News RSS:**
- **Direct RSS**: User asks about specific outlets, or you need a comprehensive scan of one source's coverage
- **Google News RSS**: User asks about a topic and wants cross-outlet coverage, or the topic isn't well-covered by a single outlet's RSS

**Maritime/Shipping angle:** For Gulf/Middle East conflict monitoring, always include gCaptain and OilPrice RSS feeds alongside news sources. They catch shipping disruptions, tanker attacks, oil price movements, and maritime security incidents that general news sources often miss or report late.

**Other known RSS feeds (not Saba CMS):**
- Many Iranian government ministries and agencies have RSS feeds under similar URL patterns
- International outlets: BBC, Al Jazeera have working RSS — but Reuters is often blocked (see access table)

## Core Method 2: Google News RSS

Google News RSS is the primary tool for cross-outlet topic searches. It returns structured XML with titles, dates, source names, and redirect links.

```
curl -s "https://news.google.com/rss/search?q=<QUERY>&hl=en-US&gl=US&ceid=US:en" -o /tmp/results.xml
```

Parameters: `q` (query), `hl` (language), `gl` (country), `ceid` (country:lang code like US:en, IR:fa).

### Batch Query Pattern for Comprehensive Topic Coverage

For complex topics with multiple sub-angles (e.g. "Iran/Gulf/Middle East"), run **6-10 targeted Google News RSS queries in parallel** rather than one broad query. Each query covers a specific facet:

```
Query 1: Iran Gulf military           → military operations, force posture
Query 2: Strait of Hormuz OR Kharg    → shipping disruptions, maritime security
Query 3: Israel Iran war              → Israel-Iran tensions
Query 4: Houthi Yemen Red Sea         → Red Sea shipping, Yemen conflict
Query 5: US military Gulf carrier     → US force deployments
Query 6: Iran nuclear sanctions       → nuclear program, diplomatic track
Query 7: Iran missile drone           → weapons, strikes
Query 8: Gulf state Saudi UAE Qatar   → Gulf diplomacy, state responses
Query 9: Iraq Baghdad OR Basra        → Iraq security
```

This approach yielded **272 unique items from ~440 total** in one session — far more than a single broad query. Deduplication by title similarity (first 80 chars) is essential afterward.

**Why this works:** Different outlets frame the same events with different keywords. Iran's Hormuz closure appears under "shipping," "oil," "maritime security," "strait," and "energy" — a single query misses most of these. The batch approach catches stories across all framing variants.

## Workflow

### Phase 0: Telegram Channel Monitoring (for real-time OSINT)

Telegram channels are often the fastest source for breaking news in Middle East/Persian-language contexts. Public channels have a web preview accessible via curl:

```
curl -sL "https://t.me/s/<channelname>" -H "User-Agent: Mozilla/5.0"
```

This returns HTML with all recent posts. Parse with `sed 's/<[^>]*>//g'` to strip tags, then `grep` for keywords. Each post includes view counts (social proof for importance) and reaction counts.

**Arabic Telegram channels** (e.g. @RasadAlmedan, @EabriLive) require Arabic→Persian translation after extraction. Persian Telegram channels (e.g. @alonews, @khabari_18) can be used directly.

**Known fast Telegram OSINT channels (Iran/Gulf war context):**
| Channel | Language | Focus | Notes |
|---------|----------|-------|-------|
| @alonews | Persian | War news, military, breaking | 991K subs, very fast breaking |
| @khabari_18 | Persian | Breaking war/negotiations, analysis | 1.76M subs, extremely high engagement (90K+ views on major posts) |
| @VahidOnline | Persian | Major curated news aggregator | 1.43M subs, cross-references major stories; 374K–482K views on top posts |
| @hormozgan_today | Persian | Hormozgan province local news | 16.4K subs; critical for Hormuz/Qeshm/strait ground-truth |
| @RasadAlmedan | Arabic | Field monitoring, Gaza/Palestine/Gulf | |
| @EabriLive | Arabic | Israeli/Hebrew media translation | |
| @ourwarstoday | English | Global war footage + OSINT | |
| @javanmardi77 → AVATODAY | Persian | Breaking OSINT, images, verification | **Name mismatch:** username `javanmardi77` displays as "AVATODAY" (independent journalist, Kurdish/Iranian region focused) |
| @doctordaraei | Persian | Geopolitical analysis | |

**Pitfall:** Telegram's web preview (`t.me/s/`) only shows the ~50 most recent posts. For older content, you need the Telegram client API or alternative archives.

### Telegram HTML Structured Extraction (advanced)

Simple `sed` tag-stripping loses structured fields. For reliable extraction of post metadata, use this Python approach:

1. **Split by message boundaries:** `re.split(r'<div class="tgme_widget_message_wrap', html_content)`
2. **Per-message block, extract with regex:**
   - Post ID: `data-post="([^"]+)"`
   - Datetime: `datetime="([^"]+)"`
   - Views: `tgme_widget_message_views[^>]*>([^<]*)`
   - Text: `tgme_widget_message_text[^>]*dir="auto">(.*?)</div>\s*<div class="tgme_widget_message_footer` (then strip inner HTML tags, decode entities)
   - Media type: presence of `tgme_widget_message_video` (video with duration), `message_grouped` (multi-media album), or `tgme_widget_message_photo`
   - Reactions: `<b>([^<]+)</b>([\d.,]*K?)</span>` — captures emoji + count pairs
3. **Text cleaning pipeline:** Replace `<br>` → `\n`, strip `<blockquote>`, `<tg-emoji>`, `<i class="emoji">`, `<a>` (preserving href as `[url]`), then all remaining tags, then `html.unescape()`.
4. **Output format:** Sort by datetime descending, group by channel, include views + reactions as engagement proxy.

This approach is reliable for all public Telegram channels and produces structured data suitable for OSINT analysis, filtering, and cross-referencing.

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

## User Source Preferences (Iran/Gulf OSINT)

The user has defined a specific priority source list for Iran/Gulf situational awareness monitoring:

| # | Source | Type | Language | Role |
|---|--------|------|----------|------|
| 1 | **khabarfoori.com** (خبرفوری) | Website | Persian | Breaking Iran-domestic news |
| 2 | **axios.com** | Website | English | US political/strategic analysis |
| 3 | **Barak Ravid** (Axios reporter) | Journalist | English/Hebrew | Israeli-US diplomatic intelligence |
| 4 | **Mike Allen** (Axios co-founder) | Journalist | English | "Behind the Curtain" — insider political analysis |
| 5 | **tasnimnews.ir** (تسنیم) | News agency | Persian | IRGC/military-aligned reporting |
| 6 | **@alonews** | Telegram | Persian | War news, fast breaking |
| 7 | **@RasadAlmedan** | Telegram | Arabic→Persian | Field monitoring |
| 8 | **@EabriLive** | Telegram | Arabic→Persian | Israeli media translation |
| 9 | **@sentdefender** (OSINTdefender) | X/Twitter | English | Military OSINT |
| 10 | **@ourwarstoday** | Telegram | English→Persian | Global war coverage |

**Translation rule:** Arabic and English sources must be translated to Persian (Farsi) in all reports. Persian sources used directly.

## Common Pitfalls

1. **Cloudflare/CAPTCHA blocking** — Axios, WSJ, NYT, WaPo, JPost, **Reuters** all block. Reuters returns a Cloudflare JS challenge page (~773 bytes). Use secondary sources or Google News RSS for Reuters content.
2. **Fully JS-rendered sites** — **AP News** (apnews.com) renders all article content via JavaScript; curl returns an empty shell. No RSS feed at hub URLs. Always use an aggregator (Google News RSS) to get AP stories. Also blocked: UPI, Yahoo News, Daily Sabah (all return shells with no article content).
3. **Empty RSS feeds** — Some language combos return empty XML. Check file size.
4. **Security scanner flags `curl | python3`** — `curl ... | python3 -c` pipelines get flagged by the security scanner with `[HIGH] Pipe to interpreter` warnings. They still work (auto-approved by smart approval in most sessions), but add latency and noise. Two workarounds: (a) use `curl -o /tmp/file.html` then parse separately, or (b) accept the flag if speed matters more than clean logs. In subagent/cron mode the flag still auto-approves.
5. **Duplicate results** — Same story under different headlines. Sort by pubDate.
6. **Heredoc issues** — Write extraction scripts via write_file, run via terminal.
7. **`execute_code` blocked in subagent/cron mode** — When running as a subagent (or in cron), `execute_code` is blocked by the security sandbox. Do NOT attempt batched Python+curl pipelines via execute_code in these contexts. Instead, make multiple parallel `terminal()` calls with individual `curl` commands. This works fine — terminal() is not blocked in subagent mode. Plan your queries upfront and issue them as parallel terminal() calls in one assistant turn.
8. **RSS `head -c` truncation is fine for triage** — When scanning many RSS feeds, pipe through `head -c 10000` or similar to get just the first 20-30 items. Full XML is often 100KB+. You don't need to parse every `<item>` — the first page of results sorted by relevance gives you the key stories. Parse the XML in a follow-up call only if you need specific fields.
9. **Google News RSS lag for real-time events** — Google News RSS can lag 30–60+ minutes behind real-time breaking news. Very fresh stories (< 30 min old) may not appear in RSS results at all. For time-critical monitoring, supplement RSS with direct site scraping (if accessible) and accept that the feed shows a slightly delayed picture. When the RSS returns empty for a query that should have results, the event is likely too recent to be indexed — try broader queries or different language params.
10. **Social media screenshot verification** — When users share screenshots of official alerts (embassy warnings, military alerts, government notices), always verify whether they are NEW or STANDING advisories. Example: US State Department "Worldwide Caution" is a permanent standing notice displayed on ALL embassy websites — it is NOT an emergency evacuation order. Before reporting as breaking news, check: (a) is the notice date-stamped? (b) does the text contain specific new language? (c) do multiple independent sources confirm the same alert? Misidentifying standing advisories as breaking news erodes credibility.
11. **Multi-language parallel search pattern** — For Middle East/conflict OSINT, always search in 4+ languages simultaneously in one turn: English (`US:en`), Arabic (`SA:ar`), Persian (`IR:fa`), Turkish (`TR:tr`). Different outlets break stories in different languages first. Arabic Gulf media (Al Arabiya, Al Mayadeen) often report Kuwait/Gulf events before English wire services. Turkish outlets (Anadolu, Yeni Safak) are fast on Turkey-adjacent stories. Persian outlets (Fars, Tasnim, Khabarfoori) break Iran-domestic events first.
12. **Progressive source building** — In real-time monitoring sessions, users often add sources incrementally (e.g. "add source 6, add source 7..."). Each new source should be immediately checked and results integrated into the ongoing report. Don't wait for the full list — check each source as it's added and report findings. Save the complete source list to memory for future sessions.
13. **Real-time monitoring posture** — When user requests 100% vigilance on a developing crisis, structure reports as: (a) NEW developments only (not repeats), (b) timestamp of last scan, (c) explicit "no new developments" if nothing changed, (d) always end with "ready for next scan." This prevents the user from thinking nothing is happening when you're actually waiting for new data.
14. **Multi-Telegram channel cross-verification** — When multiple Telegram channels report the same event, note the timestamps to find the original source. Arabic channels often break Gulf events first; Persian channels break Iran-domestic events first; English OSINT channels aggregate and verify. Cross-reference view counts as a rough proxy for story significance.
15. **Embassy alert screenshot context** — When users share images of multiple embassy security alerts simultaneously (e.g., Jordan, Iraq, Bahrain, Qatar, Saudi Arabia, Egypt), note that "Worldwide Caution" appears on ALL embassy sites as a standing notice. The significant items are country-specific "SECURITY ALERT" banners which are separate from and newer than the standing notice. Report the distinction clearly.

16. **`terminal()` does not support shell `&` backgrounding** — Commands with `&` at the end are blocked by the security scanner in `terminal()`. You cannot run multiple curl commands in parallel within a single terminal() call. Instead: (a) issue multiple separate `terminal()` calls in one assistant turn (they run concurrently), or (b) write a script file first, then run it. Do NOT use `&` in terminal commands.

17. **RSS feed truncation with `head -c` can break XML parsing** — When piping large RSS feeds through `head -c 50000`, you may truncate mid-tag (e.g., Khabar Online's feed exceeds 50KB). This causes `ET.parse()` to fail with a parse error. Fix: use regex-based fallback parsing (`re.findall(r'<item>(.*?)</item>', content, re.DOTALL)`) instead of XML parsing. The regex approach handles truncated XML gracefully.

18. **Safety4Sea returns HTML not RSS at `/feed/`** — Despite the URL pattern, `safety4sea.com/feed/` returns a full HTML page (possibly due to WAF/redirect). Not usable as RSS. Use Google News RSS with `site:safety4sea.com` instead.

19. **MarineTraffic is JS-only** — `marinetraffic.com` returns a minimal HTML shell with no vessel/traffic data. No useful content via curl. For maritime traffic data, use gCaptain RSS or UNCTAD shipping data instead.

20. **OilPrice.com homepage blocked but RSS works** — Per the access table, OilPrice.com homepage returns boilerplate. However, `oilprice.com/rss/main` returns a valid RSS feed with full item descriptions. Always use the RSS endpoint, not the website.

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
