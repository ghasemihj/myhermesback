# Date/Time Handling Patterns for OSINT Reports

## The Problem (What Went Wrong)

Agent stored a FIXED date in memory:
```
Current date: Tue 4 Aug 2026 = 13 Mordad 1405 IRST
```

Then used this stale value in EVERY subsequent report, even hours later when the actual date had changed.

User corrected THREE TIMES before agent fixed the root cause.

## Root Cause

Memory is for PERSISTENT facts. Timestamps are EPHEMERAL.
Storing a date in memory = creating a stale value that gets reused indefinitely.

## The Fix

### Step 1: Always run `date` before generating any report
```bash
date -u "+UTC: %Y-%m-%d %H:%M:%S"
TZ="Asia/Tehran" date "+%Y-%m-%d %H:%M:%S %A"
```

### Step 2: Calculate Jalali date manually (jdatetime often unavailable)
```
Farvardin 1 = March 21
Months: 31/31/31/31/31/31/30/30/30/30/30/29 (leap year: last = 30)

Example: August 5, 2026
- Farvardin: Mar 21 - Apr 20 (31 days)
- Ordibehesht: Apr 21 - May 21 (31 days)
- Khordad: May 22 - Jun 21 (31 days)
- Tir: Jun 22 - Jul 22 (31 days)
- Mordad starts: Jul 23
- Aug 5 - Jul 23 = 13 days + 1 = 14 Mordad
Result: 14 Mordad 1405
```

### Step 3: Display in report header
```
📅 چهارشنبه ۱۴ مرداد ۱۴۰۵
📆 Wednesday 5 August 2026
🕐 ۰۳:۲۵ به وقت ایران (IRST)
🌍 ۲۳:۵۵ UTC
```

## Memory Rule

NEVER add entries like:
- "Current date: ..."
- "Today is ..."
- "Date: 2026-..."

ONLY use `date` command output.

## User Feedback

User said: "چرا با اینکه هر بار می گویم تاریخ و ساعت را درست کن و درست می کنی باز هم در گزارش های بعدی تاریخ و ساعت را اشتباه گزارش می کنی؟"

Translation: "Why do you keep getting the date/time wrong in reports even after I correct you each time?"

This was a FRUSTRATION signal — the user had to correct the same error 3 times.
