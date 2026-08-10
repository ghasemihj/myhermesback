# Dependency Audit Pattern for OSINT Projects

## When to Use

User asks to audit, clean up, or remove an OSINT monitoring project (skill, cron, data).

## Audit Checklist

### 1. Cron Dependencies
```bash
# List all cron jobs
cronjob(action='list')
# Search for references
grep -r "<project-name>" /data/.hermes/cron/
```

### 2. Skill Dependencies
```bash
# Find skill files
find /data/.hermes/skills -name "*<project>*" -type f
# Search for references in other skills
grep -r "<project-name>" /data/.hermes/skills/
```

### 3. File/Config Dependencies
```bash
# Search config files
grep -r "<project-name>" /data/.hermes/config.yaml /data/.hermes/.env /data/.hermes/auth.json
# Search memory
grep -r "<project-name>" /data/.hermes/memories/
# Search reports directory
find /data/.hermes/reports -name "*<project>*"
```

### 4. Session Dependencies
```
session_search(query="<project-name> OR <exchange-name>", limit=5)
```

### 5. Railway Variable References
```bash
grep -ri "<EXCHANGE>_API" /data/.hermes/.env /data/.hermes/config.yaml
# Note: Variable NAMES only, never values
```

## Safe Deletion Order

1. **Disable cron first** (pause, don't delete)
2. **Delete cron** (after confirmation)
3. **Delete skill files** (after confirmation)
4. **Delete data/reports** (after confirmation)
5. **Update MEMORY.md** (remove stale references)

## Config Verification After Changes

After modifying config.yaml settings (e.g., disabling self-improvement):

### Verify settings in config file
```bash
cat /data/.hermes/config.yaml | grep -A 5 "agent:\|memory:"
```

### Verify runtime status
```bash
hermes memory status
hermes config check
```

### Check if restart is needed
- Config file changes: **Yes** — Gateway must be restarted
- Runtime changes: **No** — Take effect immediately
- To restart: User must run `hermes gateway restart` from separate terminal

## What NOT to Delete

- Sessions (historical record)
- Railway Variables (may be needed for other projects)
- Other skills that reference the project (check umbrella skills)
- MEMORY.md entries about other topics

## User Preferences (Jason)

- Always show before/after status for each deletion
- Confirm each step before proceeding
- Never delete without explicit user command
- Report disk usage after cleanup
- Show remaining cron jobs after deletion
- **Respect explicit prohibitions**: If user says "do not change anything" or "don't run self-improvement", STOP all automatic modifications

## MEMORY.md Cleanup Pattern

When cleaning up stale references in MEMORY.md:

### Step 1: Identify all references
```bash
grep -n -i "<project-name>\|<exchange>\|<job-id>" /data/.hermes/memories/MEMORY.md
```

### Step 2: Show Before/After for each line
- Line number + current content
- Proposed replacement (keep non-crypto parts, remove crypto parts)

### Step 3: Get user approval before ANY changes

### Step 4: Apply changes (only after explicit approval)

### Example
```
Line 9 — Before:
User has Windows laptop... crypto-portfolio project removed (skill + cron) — reports dir still exists.

Line 9 — After:
User has Windows laptop...
```

## Example Audit Output

```
| # | بررسی | نتیجه |
|---|-------|-------|
| ۱ | Skill directory | ❌ وجود ندارد |
| ۲ | Reports directory | ✅ سالم |
| ۳ | Cron jobs | ✅ بدون تغییر |
| ۴ | MEMORY.md | ⚠️ نیاز به اصلاح |
```
