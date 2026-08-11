---
name: social-signal-validation
description: "Standalone module for monitoring and validating social media signals in Gulf/Iran OSINT reports."
version: 1.0.0
---

# Social Signal Validation — ماژول رصد و اعتبارسنجی شبکه‌های اجتماعی

## Overview

This module serves as a fast-sensor layer for detecting events through social media and user-generated content (UGC). It monitors Telegram, X/Twitter, Instagram, YouTube, and other platforms to identify emerging signals — while preventing premature elevation of unverified content to confirmed status.

**Core principle:** Social media is a *detector*, not a *verifier*. Speed of discovery must be maintained without converting posts into confirmed news automatically.

**Critical principle:** "تأییدنشده" means verification status, NOT importance. An unverified signal can be Importance=حیاتی and Urgency=بسیار فوری. Never dismiss or delay reporting an important signal just because it lacks official confirmation. The system must balance two errors:
- Error 1: Delaying or hiding a critical signal due to lack of official confirmation
- Error 2: Stating a rumor or vague observation as confirmed fact
- Solution: Fast registration + clear labels + evidence explanation + continuous review

**Language:** All output is in Persian (Farsi).

**This module is standalone** — it can be invoked independently or as part of a Gulf-Kharg Watch report.

## When to Use

- User asks to monitor social media for Gulf/Iran developments
- User asks to validate a specific social media post or claim
- User asks about trending topics related to Kharg, Hormuz, or southern Iran
- User wants to check if a piece of media is old/recycled
- Report generation includes the "سیگنال‌های سریع شبکه‌های اجتماعی" section

**Do NOT use for:**
- Mass surveillance of individuals
- Doxxing or identifying private citizens
- Creating operational intelligence from social media
- Automated bulk scraping without validation

## Signal Status System (وضعیت سیگنال)

Every signal progresses through a defined status lifecycle:

| Status | Label | Definition |
|--------|-------|------------|
| S0 | دریافت‌شده | Received, not yet reviewed |
| S1 | تک‌منبعی | Single-source observation or claim |
| S2 | چندگزارشی | Multiple similar reports, insufficient independent verification |
| S3 | نسبتاً معتبر | Relatively credible media or spatial/temporal evidence |
| S4 | تأییدشده | Confirmed by official source or credible independent media |
| SX | ردشده | Rejected: old, recycled, manipulated, or wrong location |

### Three-Dimensional Signal Classification (طبقه‌بندی سه‌بعدی سیگنال)

**Every signal must be classified along THREE independent dimensions:**

#### 1. Importance (اهمیت)

| Level | Label | Definition |
|-------|-------|------------|
| پایین | Low | Minor local event, limited impact |
| متوسط | Medium | Notable event, regional significance |
| بالا | High | Significant event, national impact |
| حیاتی | Critical | Major event, potential regional/international impact |

#### 2. Urgency (فوریت)

| Level | Label | Definition |
|-------|-------|------------|
| عادی | Normal | Routine monitoring |
| نیازمند پیگیری | Needs tracking | Requires follow-up in next update |
| فوری | Urgent | Requires attention within hours |
| بسیار فوری | Very urgent | Requires immediate attention |

#### 3. Verification (اعتبارسنجی)

| Level | Label | Definition |
|-------|-------|------------|
| تأییدنشده | Unverified | No independent confirmation yet |
| دارای شواهد اولیه | Preliminary evidence | Some supporting evidence exists |
| چندمنبعی | Multi-source | Multiple independent reports |
| نسبتاً تأییدشده | Relatively confirmed | Strong evidence, pending official confirmation |
| تأییدشده | Confirmed | Official or credible independent confirmation |

**Critical rule:** A signal CAN be simultaneously Importance=حیاتی, Urgency=بسیار فوری, Verification=تأییدنشده. These are three separate variables, not a single ranking.

### Status Progression Rules

```
S0 → S1: Initial review complete
S1 → S2: Multiple similar reports identified (still one origin)
S2 → S3: Requires at least ONE of:
  - Independent media from different angle/source
  - Consistent temporal/spatial evidence
  - Verifiable journalist or local source confirmation
S3 → S4: Requires official source or credible independent media
Any → SX: Rejection criteria met (old, recycled, manipulated, wrong location)
```

**Critical rule:** S2 and below NEVER enter the "رویدادهای تأییدشده" section of reports. However, important unverified signals MUST appear in the "هشدارهای سریع" section.

### Signal Lifecycle Update Cycle (چرخه به‌روزرسانی سیگنال)

Every sensitive signal must be trackable through these states:

| State | Label | Definition |
|-------|-------|------------|
| New | تازه | Just received, not yet reviewed |
| Monitoring | در حال رصد | Under active observation |
| Strengthened | تقویت‌شده | Evidence has improved since last check |
| Weakened | تضعیف‌شده | Evidence has degraded |
| Confirmed | تأییدشده | Verified by official/independent sources |
| Rejected | ردشده | Identified as false, recycled, or misplaced |
| Unresolved | حل‌نشده | Cannot confirm or deny with available evidence |

In each subsequent report, clearly state:
- Which signals were upgraded (ارتقا یافت)
- Which signals were downgraded (تضعیف شد)
- Which signals were confirmed (تأیید شد)
- Which signals were rejected (رد شد)
- Which signals remain unresolved (حل‌نشده باقی ماند)

## Required Fields for Every Signal

Each post or media item MUST be logged with these fields:

### Identity & Source
- **شناسه یکتای سیگنال** — Unique signal ID (format: `SIG-YYYYMMDD-XXXX`)
- **پلتفرم** — Platform name (Telegram, X, Instagram, YouTube, etc.)
- **نام نمایشی منبع** — Display name of source
- **شناسه حساب یا کانال** — Account or channel ID (confirmed, not guessed)
- **URL مستقیم پست** — Direct URL to the post (confirmed via access)

### Timing
- **زمان دریافت توسط Hermes** — When Hermes received the signal
- **زمان انتشار** — When the post was published
- **زمان ادعایی وقوع رویداد** — Claimed event occurrence time

### Location
- **محل ادعایی** — Claimed location from post content
- **محل قابل استنباط از شواهد** — Location inferable from visual/audio evidence

### Provenance Chain
- **نویسنده شاهد مستقیم است یا بازنشرکننده** — Is author a direct witness or reposter?
- **منبع اولیه احتمالی** — Probable original source

### Content Analysis
- **نوع محتوا** — Content type: text, image, video, audio
- **شرح دقیق آنچه واقعاً در رسانه قابل مشاهده یا شنیدن است** — Precise description of what is actually visible/audible in the media
- **ادعاهای موجود در کپشن یا توضیح نویسنده** — Claims made in caption/description
- **مواردی که از خود رسانه قابل اثبات نیست** — What cannot be proven from the media itself

### Technical Verification
- **هش فایل یا شناسه مشابهت** — File hash or similarity ID for repost detection
- **تعداد منابع ظاهری** — Apparent source count (total posts seen)
- **تعداد شاهدان مستقل واقعی** — Actual independent witness count

### Validation
- **شواهد تأییدکننده** — Confirming evidence
- **شواهد ردکننده** — Rejecting evidence
- **وضعیت** — Status: S0–SX
- **امتیاز اطمینان** — Confidence score: 0–100
- **علت امتیاز** — Score rationale
- **وضعیت نهایی بررسی** — Final review status

## Monitoring Source Categories

### Tier 1: Priority Sources (Monitor First)

| Category | Examples | Notes |
|----------|----------|-------|
| OSINT accounts | Confirmed OSINT analysts covering Iran/Gulf | Verify account identity before logging |
| Local journalists | Reporters in Bushehr, Hormozgan, Kharg area | Cross-check affiliation |
| Regional news channels | Telegram channels covering southern Iran | Many are unverified |
| Official accounts | Government, military, IRGC social media | Verify it's the real account |

### Tier 2: Secondary Sources

| Category | Examples | Notes |
|----------|----------|-------|
| Diaspora media | AvaToday, Iran International, Manoto | Check editorial stance |
| Maritime enthusiasts | Ship spotters, port watchers | Useful for shipping signals |
| Academic/research | Iran scholars, Gulf analysts | Good for context, not breaking news |

### Tier 3: Background Monitoring

| Category | Examples | Notes |
|----------|----------|-------|
| General news aggregators | Various Twitter lists, Telegram groups | High noise, low signal |
| Random user posts | Geotagged content from Gulf region | Requires heavy validation |

### Source Identification Rules

1. **No guessing:** Record exact account name, ID, and URL only when confirmed through actual access.
2. **No automatic credibility:** Never declare a source "definitively credible" solely due to fame.
3. **Topic-specific evaluation:** A source's credibility in one domain does not transfer to another.
4. **Track history:** For each account, log: accuracy history, correction record, deleted claims, original source provision, recycled content incidents.

## Validation Rules

### Rule 1: Observation vs. Interpretation
**Separate "what is seen/heard" from "caption interpretation."**
- What the media actually shows ≠ what the author claims it shows
- Log both separately in the signal record

### Rule 2: Repost ≠ Independent Witness
**Multiple accounts sharing one file = one witness.**
- Count unique origins, not reposts
- Trace repost chains to the earliest accessible version

### Rule 3: Provenance Chain
**Trace repost chains to the earliest accessible version.**
- Document the chain: A → B → C → ... → Origin
- The origin is the first accessible version, not necessarily the true original

### Rule 4: Timing Discipline
**Post publication time ≠ media capture time.**
- A video posted today may have been filmed weeks ago
- Always check for temporal consistency

### Rule 5: Recycled Content Check
**Before accepting image/video, check for old or recycled content.**
- Reverse image search when possible
- Check metadata dates
- Look for anachronistic elements

### Rule 6: Environmental Evidence as Clues Only
**Environmental cues (language, signs, weather, light, architecture, coastline) are clues, not proof.**
- Use for narrowing possibilities, not definitive identification
- Multiple consistent cues strengthen the case

### Rule 7: Location Uncertainty
**Do not declare precise location without sufficient evidence.**
- " appears to be near [area]" is acceptable
- "is definitely at [coordinates]" requires strong evidence

### Rule 8: Metadata Ambiguity
**Absence of metadata ≠ fake; presence of metadata ≠ proof.**
- Metadata can be stripped, spoofed, or lost
- Use as one data point among many

### Rule 9: Engagement ≠ Credibility
**Repost count, likes, or views do not create credibility.**
- Viral content is often wrong
- Low-engagement content can be accurate

### Rule 10: Deletion Ambiguity
**Post deletion after publication ≠ proof of truth or falsehood.**
- Could be correction, legal pressure, or strategic removal
- Log the deletion but don't draw conclusions from it alone

### Rule 11: AI-Generated Content
**If signs of AI generation exist, flag as suspicious — but do not conclude without proof.**
- Look for: unnatural artifacts, inconsistent lighting, text distortions
- Flag for human review, don't auto-reject

### Rule 12: Single-Source Rule
**Single-source social media NEVER goes directly to "رویدادهای تأییدشده."**
- Must reach S3 or S4 through validation workflow

### Rule 13: S2→S3 Upgrade Requirements
**To upgrade from S2 to S3, at least ONE of:**
- Independent media from different angle or source
- Consistent temporal or spatial evidence
- Verifiable journalist or local source confirmation
**IMPORTANT:** Upgrade from S1/S2 to S3/S4 must be based on QUALITY of evidence, not merely increased repost count.

### Rule 14: S4 Upgrade Requirements
**To reach S4, requires official source or credible independent media.**

### Rule 15: Co-Source Detection (تشخیص انتشارهای هم‌منشأ)
**Multiple accounts sharing one file = one witness, not multiple.**
- Ten channels reposting one video = NOT ten independent witnesses
- Cropped versions or different logos of same video = one cluster
- One news agency quoted by multiple outlets ≠ multiple confirmations
- Accounts that only copy from one main channel belong to same cluster
- Witnesses with independent angle, time, location, or narrative = registered separately

### Rule 16: Media Analysis Rules (قواعد تحلیل تصاویر و ویدئوها)
- Existence of image/video does NOT prove the claim
- Upload time ≠ occurrence time
- Check for old/recycled content
- Check general location and time markers
- Check lighting, weather, language, signs, architecture, sounds, general context
- Register visible contradictions
- If original media inaccessible, state: "اصل فایل بررسی نشده و ارزیابی فقط بر اساس متن، thumbnail یا metadata است."

### Rule 17: Military Activity Reports (گزارش‌های فعالیت نظامی)
For reports on missile/launch/explosion/military activity:
1. Eyewitness and public image reports must be registered quickly
2. Distinguish between: "observed light/trail in sky" → "claimed launch" → "system type confirmed" → "origin" → "path" → "target"
3. Do NOT conclude missile type, precise origin, or certain target from a single light trail
4. Reports on general direction, approximate time, and approximate number ARE registrable
5. Do NOT provide precise coordinates, live operational paths, targeting data, or operational utility data
6. Origin claims at general level with clear labels only
7. If multiple independent observations from different areas exist, cluster them and analyze probable connection WITHOUT claiming certainty**

### Rule 15: Account Evaluation Scope
**Evaluate accounts topic-by-topic.**
- Credibility in military analysis ≠ credibility in civilian casualties
- Credibility in one region ≠ credibility in another

### Rule 16: Account History Tracking
**For each account, maintain a record of:**
- Accuracy history (correct claims vs. incorrect)
- Correction record (do they issue corrections?)
- Deleted claims (do they delete wrong posts?)
- Original source provision (do they credit sources?)
- Recycled content incidents

### Rule 17: No Operational Intelligence
**Never publish live coordinates of forces, vessels, or defense systems.**
- Never provide targeting-useful information
- This applies to social media analysis just as to formal reports

### Rule 18: Privacy Protection
**Reports must not reveal precise locations of private individuals or witnesses.**
- General area is acceptable (e.g., "southern coast")
- Specific addresses or identifiable locations are not

### Rule 19: Identity Minimization
**Minimize or summarize unnecessary witness identity information.**
- Use "a local resident" not names
- Use "a truck driver" not "Mohammad from Bushehr"

### Rule 20: Purpose Limitation
**Final output is for situational awareness and public safety only.**
- No commercial use
- No targeting
- No individual identification

## Media Processing Rules

### Storage Environment (CRITICAL)

- **Persistent volume:** `/data` mounted on `/dev/zd1152` (ext4)
- **Temp paths:** `/tmp`, `/var/tmp` on overlay — NOT part of persistent volume capacity
- **Never use overlay free space as Hermes capacity**

### Before Download (mandatory checklist)

1. **Check `/data` free space:** `df -h /data`
   - If <100 MB free OR usage ≥90%: 🔴 **Critical** — all media processing halted, no cache/transcript/temp on `/data`, essential logs only
   - If <200 MB but ≥100 MB free OR usage ≥80% but <90%: ⚠️ **Warning** — no media downloads, text/URL/metadata/transcript only
   - If ≥200 MB free AND usage <80%: ✅ **Normal** — proceed if ≥150 MB remains after estimated processing
2. **Check file size from HTTP headers**
3. **Max direct download: 20 MB** — valid ONLY if `/data` is in Normal status AND ≥150 MB remains after
4. **For video:** Estimate required space as 3× input file size
5. **For audio/transcript:** Account for intermediate files in capacity calculation
6. **For files >20 MB:** Use metadata, thumbnail, description, online transcript, or low-res version only
7. **Decision rule:** If multiple conditions are met simultaneously, the **most severe** status applies

**Critical note:** 150 MB is NOT a status threshold. It is the **minimum reserve** that must remain on `/data` after any processing completes. If the estimate shows <150 MB would remain, do not start the processing.

### During Processing

7. **Temp location:** Prefer `/tmp/hermes-media-tmp/` — NOT inside `/data`
8. **For video:** Extract only key frames (3-5 frames max)
9. **For audio:** Extract transcript if available, or brief metadata
10. **Log space consumed before and after processing**

### After Processing (mandatory report)

11. **Delete:** original file, temporary frames, extracted audio, cache entries
12. **Retain ONLY:** URL, hash, essential metadata, observation summary, review result
13. **If cleanup fails:** Halt next media processing. Report file path and size (no sensitive content)
14. **No permanent media archive on `/data`**
15. **Report the following:**
    - Free space on `/data` (before and after)
    - Usage percentage on `/data` (before and after)
    - Free space on temp path
    - Size of temp files created
    - Cleanup result (success/failure)

### Capacity Rules Summary

| Rule | Value | Notes |
|------|-------|-------|
| Max download size | 20 MB | Only if `/data` is Normal AND ≥150 MB remains after |
| Video space estimate | 3× input size | Minimum |
| Temp path | `/tmp/hermes-media-tmp/` | Outside `/data` |
| Min reserve after processing | 150 MB | On `/data` — NOT a status threshold |
| Normal threshold | ≥200 MB free AND <80% usage | Media processing allowed |
| Warning threshold | <200 MB but ≥100 MB free, OR ≥80% but <90% usage | No media downloads |
| Critical threshold | <100 MB free OR ≥90% usage | All media processing halted |

## Social Signal Intensity Index (شاخص شدت سیگنال اجتماعی)

| Level | Persian | Definition |
|-------|---------|------------|
| 🟢 Normal | عادی | Baseline activity for region/time |
| 🟡 Limited Increase | افزایش محدود | Slight uptick, within normal variance |
| 🟠 Noticeable Increase | افزایش محسوس | Clear increase above baseline |
| 🔴 Unusual Spike | جهش غیرعادی | Significant spike, requires investigation |

### Intensity Calculation Rules
1. **Aggregate reposts** of a single piece of content
2. **Separate independent witness count** from post count
3. **Compare against baseline** for same region and time of day
4. **Identify cause of increase:** real event, viral repost, rumor, or unknown

## Signal Record Template

Use this template for every signal logged:

```markdown
### سیگنال [SIG-YYYYMMDD-XXXX]

**شناسه:** SIG-YYYYMMDD-XXXX
**پلتفرم:** [Telegram/X/Instagram/YouTube/Other]
**منبع:** [نام نمایشی] | [شناسه حساب] | [URL]
**زمان دریافت:** [YYYY-MM-DD HH:MM UTC]
**زمان انتشار:** [YYYY-MM-DD HH:MM UTC]
**زمان ادعایی وقوع:** [YYYY-MM-DD HH:MM UTC یا نامشخص]
**محل ادعایی:** [مکان ادعا شده]
**محل قابل استنباط:** [مکان قابل استنتاج از شواهد]
**نوع شاهد:** [شاهد مستقیم / بازنشرکننده]
**منبع اولیه احتمالی:** [URL یا شناسه منبع اصلی]

**نوع محتوا:** [متن/تصویر/ویدئو/صوت]

**مشاهده واقعی:**
[آنچه واقعاً در رسانه قابل مشاهده یا شنیدن است]

**ادعاهای کپشن:**
[آنچه نویسنده ادعا کرده]

**موارد غیرقابل اثبات:**
[مواردی که از خود رسانه قابل اثبات نیست]

**هش/شناسه مشابهت:** [هش فایل یا شناسه]
**تعداد منابع ظاهری:** [تعداد]
**تعداد شاهدان مستقل واقعی:** [تعداد]

**شواهد تأییدکننده:** [لیست]
**شواهد ردکننده:** [لیست]

**وضعیت:** [S0/S1/S2/S3/S4/SX]
**امتیاز اطمینان:** [0-100]
**علت امتیاز:** [توضیح]
**وضعیت نهایی:** [توضیح]
```

## Integration with Main Report

When generating a Gulf-Kharg Watch report, the social signal section should be placed after the main analysis sections. See `references/report-template.md` for the exact placement and sub-section structure.

The social signal section answers: "What are people on social media saying, and how much of it is credible?"

## Urgent Alert Criteria (معیارهای هشدار فوری)

A signal MUST appear in the "هشدارهای سریع و سیگنال‌های حساس" section if it meets ANY of:

1. Simultaneous observation by multiple independent witnesses
2. Fresh image/video with checkable time/location markers
3. Report of explosion, launch, attack, or widespread disruption
4. Potential link to critical infrastructure
5. Sudden disruption in flights, ports, internet, power, or communications
6. Local emergency notice
7. Sudden change in official positions
8. Simultaneous increase in reports from multiple regions
9. Potential national or regional impact

**The system must balance two errors:**

Error 1: Delaying or hiding a critical signal due to lack of official confirmation.
Error 2: Stating a rumor or vague observation as confirmed fact.

Solution: Fast registration + clear labels + evidence explanation + continuous review.

## Required Fields for Fast Alert Signals

For each signal in the "هشدارهای سریع" section, record:

- Signal ID, short title
- First seen time, last update time
- General area, platform, account/source, direct URL
- Direct witness or repost
- Detailed description of observation or claim
- Evidence type: text, image, video, audio, multiple witnesses, other public data
- Was original media viewed? Or only caption/thumbnail?
- Number of publications, number of truly independent origins
- Importance (پایین/متوسط/بالا/حیاتی)
- Urgency (عادی/نیازمند پیگیری/فوری/بسیار فوری)
- Verification (تأییدنشده/شواهد اولیه/چندمنبعی/نسبتاً تأییدشده/تأییدشده)
- Signal status S0–S4 or SX
- Supporting evidence, contradicting evidence, alternative explanations
- Probable impact, next analytical step, suggested review time
