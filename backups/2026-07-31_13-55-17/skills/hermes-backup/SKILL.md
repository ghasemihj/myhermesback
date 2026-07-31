---
name: hermes-backup
description: "Backup Hermes data to GitHub on a schedule."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [backup, data, git, github, cron, disaster-recovery, hermes-home]
    related_skills: [hermes-agent, github-repo-management, github-auth]
---

# Hermes Agent Backup

Automated backup of critical Hermes data to a remote Git repository on a schedule. Designed for environments where SSH (port 22) may be blocked — uses HTTPS + Personal Access Token (PAT) exclusively.

## When to Use

- User wants scheduled backups of Hermes memory, skills, config, or sessions
- User asks to protect Hermes data from loss (cloud sync, remote backup)
- Setting up disaster recovery for a Hermes installation
- User provides a repo URL + token and asks for periodic backup

## What Gets Backed Up (Critical)

| Category | Files / Dirs | Why Critical |
|----------|-------------|--------------|
| Config | `config.yaml`, `.env` | All settings, API keys, provider configs |
| Identity | `SOUL.md`, `auth.json` | Personality definition, OAuth tokens |
| Skills | `skills/` | All installed/custom skills — the agent's procedural memory |
| Memories | `memories/` | Persistent user profile, preferences, notes |
| Databases | `state.db`, `kanban.db`, `cron/executions.db` | Session store, kanban board, cron history |
| Sessions | `sessions/` | JSONL transcripts of conversations |
| Cron | `cron/` | Scheduled job definitions and outputs |
| Hooks | `hooks/` | Event-driven hooks |
| Profiles | `profiles/` | Multi-profile configs (if any) |
| Metadata | `.skills_prompt_snapshot.json`, `channel_directory.json`, `gateway_state.json` | Runtime state worth preserving |

## What Gets Skipped (Regenerable)

- `cache/`, `audio_cache/`, `image_cache/` — temp caches
- `models_dev_cache.json`, `provider_models_cache.json`, `ollama_cloud_models_cache.json` — auto-fetched
- `logs/` — runtime logs
- `bin/` — binaries
- `gateway.pid`, `gateway.lock`, `auth.lock` — runtime locks
- `gateway-starts.log` — ephemeral

## Setup Steps

### 1. Prepare the GitHub repo

Create an empty repository (private recommended). Do NOT initialize with a README if using the script below — it creates the structure on first run.

### 2. Get a GitHub Classic PAT

Generate at https://github.com/settings/tokens with `repo` scope. The token needs write access to push.

### 3. Determine transport

**HTTPS + PAT** (default, works everywhere):
```
https://<user>:<token>@github.com/<user>/<repo>.git
```

**SSH** (only if port 22 is open):
```
git@github.com:<user>/<repo>.git
```

⚠️ **Pitfall:** Many cloud/container environments block outbound port 22. Always default to HTTPS+PAT and fall back to SSH only if confirmed working.

### 4. Deploy the backup script

The script template lives at `templates/backup.sh` in this skill directory. Copy it, edit the `REPO_URL` and `HERMES_HOME` variables, and place it at a stable path (e.g., `$HERMES_HOME/scripts/backup.sh`).

Key script features:
- Shallow clone → timestamped backup dir → copy critical files → manifest → commit & push
- Keeps last N backups (default 30) with a `latest` symlink
- Auto-cleans temp clone dir on exit (trap)
- Exits non-zero on push failure (for alerting)

### 5. Schedule via Hermes cron

```
cronjob(action='create', schedule='every 24h', name='hermes-daily-backup',
  prompt='Execute /data/.hermes/scripts/backup.sh and report the results.',
  deliver='origin')
```

Or via system crontab:
```
0 2 * * * /data/.hermes/scripts/backup.sh >> /var/log/hermes-backup.log 2>&1
```

### 6. Verify

Run the script manually once to confirm it works:
```bash
bash $HERMES_HOME/scripts/backup.sh
```

Check the remote repo to confirm the commit appeared.

## Pitfalls

1. **`rsync` not installed** — Some minimal environments (containers, stripped images) lack `rsync`. Use `cp -r` instead. The template script uses `cp -r` by default.

2. **PAT in clone URL** — The token is embedded in the git remote URL inside the temp clone dir. The script cleans up via `trap`, but be aware the token appears in `ps` output during the push. Consider using `git credential helper` for higher security.

3. **Empty `memories/` or `sessions/`** — On fresh installs these dirs may be empty. The script handles this gracefully (creates dirs, reports 0 count).

4. **Large session history** — `sessions/*.jsonl` files can grow. The script backs them up as-is. For very large histories, consider `.gitignore`-ing old session files or archiving separately.

5. **Conflicting local changes** — The script clones fresh each time (shallow) into `/tmp`. If the temp dir exists from a failed run, it's cleaned up first. No conflict risk.

6. **Push failure = non-zero exit** — The cron job will report the failure. Check token expiry and repo permissions first.

## Verification

After running the script:
1. Check the output for `BACKUP_SUCCESS` marker
2. Verify the commit appears on GitHub: `git log --oneline -3`
3. Check `manifest.json` in the backup dir for file/skill/memory counts

## Template Files

- `templates/backup.sh` — Complete backup script (copy and customize)