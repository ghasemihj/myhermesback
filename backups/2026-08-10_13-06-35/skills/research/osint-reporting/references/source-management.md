# Source Management for OSINT Reports

## Problem

Sources were mentioned in reports but never saved to a persistent file.
User asked: "این منابع را در کجا ذخیره کرده ای" (Where did you save these sources?)
Answer: Nowhere — only in chat text.

## Solution

Save source registry to: `<report-directory>/sources.md`

## Source Registry Format

```markdown
# فهرست منابع پایش — Iran/Gulf OSINT
# تاریخ ایجاد: ۱۴ مرداد ۱۴۰۵ / ۵ آگوست ۲۰۲۶

| # | منبع | نوع | زبان | منطقه | توضیح |
|---|------|------|------|-------|-------|
| ۱ | khabarfoori.com | 🇮🇷 سایت | فارسی | ایران | اخبار لحظه‌ای |
| ۲ | axios.com | 🇺🇸 سایت | انگلیسی | آمریکا | تحلیل سیاسی |
| ... | ... | ... | ... | ... | ... |

---
## منابع فرعی
- @javanmardi77 (تلگرام)
- Rudaw (رسانه‌ای کردی)
- Bloomberg (رسانه‌ای)
```

## Adding a New Source

### Step 1: Verify the source exists
```bash
curl -sL "https://t.me/s/<channel>" -H "User-Agent: Mozilla/5.0" 2>/dev/null | head -5
```

### Step 2: Add to sources.md

### Step 3: Include in next report's source table

### Step 4: Note translation requirements
- Arabic → Farsi
- Hebrew → Farsi
- English → Farsi

## Source Classification

| Type | Persian | Example |
|------|---------|---------|
| Official government | بیانیه رسمی | White House, IRGC |
| Wire service | خبرگزاری | Reuters, AP, IRNA |
| Local media | رسانه محلی | Khabarfoori, Rudaw |
| Social media (verified) | شبکه اجتماعی تأییدشده | @alonews, @EabriLive |
| Think tank | اندیشکده | CSIS, IISS |

## Confidence Scoring

| Range | Label | Meaning |
|-------|-------|---------|
| 80-100 | High | Multiple confirmations |
| 50-79 | Moderate | Some corroboration |
| 20-49 | Low | Single source |
| 0-19 | Very Low | Anonymous/rumor |
