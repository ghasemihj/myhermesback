Skill creation runtime cap: 60-char description max (not 1024). Always ≤57 chars, trigger-first.
§
Hermes environment: /data is the ONLY persistent volume — 434MB ext4 on /dev/zd1152. Current usage ~10%. /tmp and /var/tmp are on overlay (1.5TB) — NEVER use overlay free space as Hermes capacity. All storage decisions must be based on `df -h /data` only. User insists overlay numbers must never be reported or used as Hermes capacity.
§
User has Hermes backup cron job (job_id: 3e09c61e5067, name: hermes-daily-backup) pushing to GitHub repo ghasemihj/myhermesback via HTTPS. Backup script at /data/.hermes/scripts/backup.sh runs every 24h. User explicitly said "هیچ Cron job، automation، background task نساز" — do NOT create cron jobs or automation unless explicitly requested.
§
NEVER store fixed date/time in memory. ALWAYS run `date` before reports. User frustrated by recurring date errors — corrected multiple times. Date format: Jalali + Gregorian + day + IRST time.
§
User has Windows laptop, cannot SSH to server (port 22 blocked). Server IP: 162.220.232.28. Server restart requires manual action from another terminal or hosting panel.
§
Sources list for Gulf/Iran OSINT: saved at /data/.hermes/reports/gulf-kharg-watch/sources.md (12 primary + 15 secondary). 12 monitored: khabarfoori.com, axios.com, Barak Ravid, Mike Allen, tasnimnews.ir, @alonews, @RasadAlmedan (AR→FA), @EabriLive (HE→FA), @sentdefender, @ourwarstoday, @marklevinshow, @alibk3 (AR→FA OSINT).
§
skills.write_approval: true — all skill writes require explicit user approval. memory.write_approval: must be "true" not "always" (valid: true/false/on/yes/1/approve/enabled). agent.background_review: false only stops NEW bg-reviews, not active sessions. Railway Variables deletable from Railway Dashboard only. crypto-portfolio-watch fully decommissioned 2026-08-08.
§
User operates with strict guardrails: always audit before acting, never delete without explicit confirmation, always show Before/After before changes, always verify after operations. Prefers step-by-step execution with checkpoints over batch operations.