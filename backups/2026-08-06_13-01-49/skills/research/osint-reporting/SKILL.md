---
name: osint-reporting
description: "OSINT reports: date/time, sources, Telegram patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [osint, reporting, date-handling, source-tracking, telegram]
    related_skills: [gulf-kharg-watch]
---

# OSINT Reporting — Workflow Rules

## ⚠️ CRITICAL: Date/Time Handling

**NEVER store fixed date/time in memory for reports.**

Memory is for persistent facts only. Timestamps become stale immediately.

### Mandatory Steps Before Every Report

1. Run `date` command to get actual system time
2. Display both Jalali and Gregorian dates in report header
3. Use the **actual** system time, not any cached/stored value

### Correct Pattern
```bash
date -u "+UTC: %Y-%m-%d %H:%M:%S"
TZ="Asia/Tehran" date "+تهران: %Y-%m-%d %H:%M:%S %A"
```

### Incorrect Pattern (NEVER do this)
```
# WRONG: Storing fixed date in memory
Current date: Tue 4 Aug 2026 = 13 Mordad 1405 IRST
```

### Jalali Date Calculation (when jdatetime unavailable)
- Farvardin 1 = March 21
- Each month: 31/31/31/31/31/31/30/30/30/30/30/29 (leap: 30)
- Example: August 5 = 14 Mordad 1405

## Source Management

### Persistent Source Registry
Save source list to: `<report-directory>/sources.md`

Format:
```markdown
| # | منبع | نوع | زبان | توضیح |
|---|------|------|------|-------|
| ۱ | name | type | lang | notes |
```

### Adding New Sources
1. Verify channel/source exists and is active
2. Add to sources.md
3. Include in next report's source table
4. Note language (original → translation target)

## Telegram Channel Scanning

### Standard Scan Pattern
```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
  sed 's/<[^>]*>//g' | sed '/^[[:space:]]*$/d' | \
  grep -i '<keywords>' | head -N
```

### Source Registries
- Main: `gulf-kharg-watch/references/telegram-source-registry.md`
- Sources list: `gulf-kharg-watch/sources.md`

## Common Pitfalls

1. **Stale dates**: Always run `date` before generating reports
2. **Missing sources**: Always check sources.md before claiming "all sources scanned"
3. **Translation**: Arabic/Hebrew sources must be translated to Farsi
4. **Timezone**: Always show both IRST and UTC in reports
