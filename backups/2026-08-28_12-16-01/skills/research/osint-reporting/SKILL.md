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

## Project Lifecycle Management

### Dependency Audits
When cleaning up or auditing an OSINT project, use the dependency audit pattern:
`references/dependency-audit-pattern.md`

Covers: Cron, Skills, Files, Sessions, Railway Variables, safe deletion order.

### Source Registry
Save source list to: `<report-directory>/sources.md`
Update when adding/removing monitoring sources.

## Common Pitfalls

1. **Stale dates**: Always run `date` before generating reports
2. **Missing sources**: Always check sources.md before claiming "all sources scanned"
3. **Translation**: Arabic/Hebrew sources must be translated to Farsi
4. **Timezone**: Always show both IRST and UTC in reports
5. **Telegram beats RSS for breaking local events**: For Hormuz/southern Iran events, scan Telegram channels (@VahidOnline, @hormozgan_today, @alonews) BEFORE RSS feeds. Telegram citizen eyewitness reports surface 30–90+ minutes before Google News RSS indexes the same story. In subagent mode, issue Telegram curl calls in the first parallel batch alongside RSS feeds.
6. **Government denial ≠ military contradiction**: Provincial governorates deny civilian impacts ("no hit reported") while IRGC outlets confirm military operations ("engagement with hostile targets"). These address different scopes (civilian damage vs military action) and are not contradictory — report both with their respective scopes labeled.
7. **Fixed dates in memory**: NEVER store a date in MEMORY.md. Always use `date` command. User corrected this 3 times before root cause was found.
8. **Background review can modify memory AND skills**: Automatic self-improvement sessions can update MEMORY.md AND patch skill files without explicit user command. To fully disable, set ALL THREE in config.yaml:
   - `agent.background_review: false` — prevents new background review sessions
   - `memory.write_approval: true` — gates memory writes behind approval
   - `skills.write_approval: true` — gates skill writes behind approval (CRITICAL: without this, skill_manage patches still go through freely)
   **PITFALL**: `agent.background_review: false` only prevents NEW sessions — existing in-session background reviews continue. `memory.write_approval` only controls MEMORY.md, not SKILL.md. The ONLY way to block autonomous skill patches is `skills.write_approval: true`. When user says "do not do self-improvement" or "don't change anything", RESPECT IT — do not let background review run.
9. **Respect explicit user commands**: If user says "فعلاً هیچ چیز را تغییر نده" (don't change anything for now), "هیچ Self-improvement اجرا نکن" (don't run self-improvement), or similar explicit prohibitions, STOP all automatic modifications. User frustration signal: "با وجود دستور صریح مبنی بر عدم اجرای Self-improvement" (despite explicit command not to run self-improvement).
