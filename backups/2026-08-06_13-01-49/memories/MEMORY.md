Skill creation runtime cap: 60-char description max (not 1024). Always ≤57 chars, trigger-first.
§
Hermes environment: /data is the ONLY persistent volume — 434MB ext4 on /dev/zd1152. Current usage ~10%. /tmp and /var/tmp are on overlay (1.5TB) — NEVER use overlay free space as Hermes capacity. All storage decisions must be based on `df -h /data` only. User insists overlay numbers must never be reported or used as Hermes capacity.
§
User has Hermes backup cron job (job_id: 3e09c61e5067, name: hermes-daily-backup) pushing to GitHub repo ghasemihj/myhermesback via HTTPS. Backup script at /data/.hermes/scripts/backup.sh runs every 24h. User explicitly said "هیچ Cron job، automation، background task نساز" — do NOT create cron jobs or automation unless explicitly requested.
§
NEVER store fixed date/time in memory for reports. ALWAYS run `date` command before generating any report. Memory is for persistent facts only, not timestamps.
§
Ourbit Exchange API (user-owned Skill: crypto-portfolio-watch, Cron: ba737d8a9800). Spot: api.ourbit.com, HMAC query string. Futures: futures.ourbit.com, HMAC headers (different auth!). Docs: ourbitdevelop.github.io (spot_v3_en, contract_en). Working: myTrades, openOrders, allOrders, Futures history_orders, order_deals. /api/v3/account denied (700007). Futures docs limited (2 endpoints, no positions/balance). Data: /data/.hermes/reports/crypto-portfolio-watch/. Cron model: MyMIMOhermes1. pages_received bug fixed (was page-1=0). Report: always show quality/endpoints/timestamps. umbrella skill: exchange-api-monitoring
§
Sources list for Gulf/Iran OSINT: saved at /data/.hermes/reports/gulf-kharg-watch/sources.md (12 primary + 15 secondary). Update this file when sources change. User has 12 monitored sources: khabarfoori.com, axios.com, Barak Ravid, Mike Allen, tasnimnews.ir, @alonews, @RasadAlmedan (AR→FA), @EabriLive (HE→FA), @sentdefender, @ourwarstoday, @marklevinshow, @alibk3 (AR→FA OSINT).
§
osint-reporting skill created: date/time handling, source management, Telegram scanning patterns. References: date-handling-patterns.md, telegram-scanning-patterns.md, source-management.md