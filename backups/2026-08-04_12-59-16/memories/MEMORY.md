Skill creation runtime cap: 60-char description max (not 1024). Always ≤57 chars, trigger-first.
§
Hermes environment: /data is the ONLY persistent volume — 434MB ext4 on /dev/zd1152. Current usage ~10%. /tmp and /var/tmp are on overlay (1.5TB) — NEVER use overlay free space as Hermes capacity. All storage decisions must be based on `df -h /data` only. User insists overlay numbers must never be reported or used as Hermes capacity.
§
User has Hermes backup cron job (job_id: 3e09c61e5067, name: hermes-daily-backup) pushing to GitHub repo ghasemihj/myhermesback via HTTPS. Backup script at /data/.hermes/scripts/backup.sh runs every 24h. User explicitly said "هیچ Cron job، automation، background task نساز" — do NOT create cron jobs or automation unless explicitly requested.
§
Current date: Tue 4 Aug 2026 = 13 Mordad 1405 IRST. Time: 16:15 IRST = 12:45 UTC. Use for all reports.
§
Ourbit Exchange API (user-owned Skill: crypto-portfolio-watch, Cron: ba737d8a9800). Spot: api.ourbit.com, HMAC query string. Futures: futures.ourbit.com, HMAC headers (different auth!). Docs: ourbitdevelop.github.io (spot_v3_en, contract_en). Working: myTrades, openOrders, allOrders, Futures history_orders, order_deals. /api/v3/account denied (700007). Futures docs limited (2 endpoints, no positions/balance). Data: /data/.hermes/reports/crypto-portfolio-watch/. Cron model: MyMIMOhermes1. pages_received bug fixed (was page-1=0). Report: always show quality/endpoints/timestamps. umbrella skill: exchange-api-monitoring
§
User's 11-source OSINT list for Iran/Gulf war: (1) khabarfoori.com (FA), (2) axios.com (EN), (3) Barak Ravid (EN/HE), (4) Mike Allen (EN), (5) tasnimnews.ir (FA/IRGC), (6) @alonews (TG, FA), (7) @RasadAlmedan (TG, AR→FA), (8) @EabriLive (TG, HE→FA), (9) @sentdefender (X, EN→FA), (10) @ourwarstoday (TG, EN→FA), (11) @marklevinshow (X, Fox News, EN→FA). Non-Farsi sources always translated. User demands 100% vigilance. Key TG: @javanmardi77, @doctordaraei, @khabari_18.