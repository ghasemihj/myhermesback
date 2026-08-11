#!/bin/bash
# Hermes Agent Backup Script
# Backs up critical Hermes data to GitHub repository
# Runs on schedule via cron
#
# Usage: bash backup.sh
# Requires: git, HERMES_HOME env var or ~/.hermes default
#
# Before first run, set REPO_URL below or export as env var.

set -euo pipefail

# ─── Configuration ───
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO_URL="${BACKUP_REPO_URL:-https://USER:TOKEN@github.com/USER/REPO.git}"
CLONE_DIR="/tmp/hermes-backup-repo"
BACKUP_DATE=$(date +%Y-%m-%d_%H-%M-%S)

# ─── Colors for output ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BACKUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Cleanup function ───
cleanup() {
    rm -rf "$CLONE_DIR" 2>/dev/null || true
}
trap cleanup EXIT

# ─── Step 1: Clone or pull repo ───
log "Cloning backup repository..."
cleanup
if ! git clone --depth 1 "$REPO_URL" "$CLONE_DIR" 2>/dev/null; then
    err "Failed to clone repository. Check access token and repo URL."
    exit 1
fi
cd "$CLONE_DIR"

# ─── Step 2: Create backup directory structure ───
BACKUP_DIR="$CLONE_DIR/backups/$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

# ─── Step 3: Backup critical files ───
log "Backing up configuration files..."
cp "$HERMES_HOME/config.yaml" "$BACKUP_DIR/" 2>/dev/null || warn "config.yaml not found"
cp "$HERMES_HOME/.env" "$BACKUP_DIR/" 2>/dev/null || warn ".env not found"
cp "$HERMES_HOME/SOUL.md" "$BACKUP_DIR/" 2>/dev/null || warn "SOUL.md not found"
cp "$HERMES_HOME/.skills_prompt_snapshot.json" "$BACKUP_DIR/" 2>/dev/null || warn "skills snapshot not found"
cp "$HERMES_HOME/auth.json" "$BACKUP_DIR/" 2>/dev/null || warn "auth.json not found"
cp "$HERMES_HOME/channel_directory.json" "$BACKUP_DIR/" 2>/dev/null || warn "channel_directory.json not found"
cp "$HERMES_HOME/gateway_state.json" "$BACKUP_DIR/" 2>/dev/null || warn "gateway_state.json not found"

# ─── Step 4: Backup databases ───
log "Backing up databases..."
mkdir -p "$BACKUP_DIR/databases"
cp "$HERMES_HOME/state.db" "$BACKUP_DIR/databases/" 2>/dev/null || warn "state.db not found"
cp "$HERMES_HOME/kanban.db" "$BACKUP_DIR/databases/" 2>/dev/null || warn "kanban.db not found"
cp "$HERMES_HOME/cron/executions.db" "$BACKUP_DIR/databases/" 2>/dev/null || warn "cron/executions.db not found"

# ─── Step 5: Backup skills ───
log "Backing up skills..."
if [ -d "$HERMES_HOME/skills" ]; then
    cp -r "$HERMES_HOME/skills/" "$BACKUP_DIR/skills/"
    rm -f "$BACKUP_DIR/skills/.usage.json" "$BACKUP_DIR/skills/.usage.json.lock" "$BACKUP_DIR/skills/.bundled_manifest" 2>/dev/null || true
    log "Skills backed up: $(find "$BACKUP_DIR/skills" -name "SKILL.md" | wc -l) skills found"
else
    warn "No skills directory found"
fi

# ─── Step 6: Backup memories ───
log "Backing up memories..."
if [ -d "$HERMES_HOME/memories" ]; then
    cp -r "$HERMES_HOME/memories/" "$BACKUP_DIR/memories/"
else
    mkdir -p "$BACKUP_DIR/memories"
    warn "No memories directory found"
fi

# ─── Step 7: Backup sessions (JSONL transcripts) ───
log "Backing up sessions..."
if [ -d "$HERMES_HOME/sessions" ]; then
    cp -r "$HERMES_HOME/sessions/" "$BACKUP_DIR/sessions/"
else
    mkdir -p "$BACKUP_DIR/sessions"
    warn "No sessions directory found"
fi

# ─── Step 8: Backup cron jobs ───
log "Backing up cron configuration..."
if [ -d "$HERMES_HOME/cron" ]; then
    cp -r "$HERMES_HOME/cron/" "$BACKUP_DIR/cron/"
fi

# ─── Step 9: Backup hooks ───
log "Backing up hooks..."
if [ -d "$HERMES_HOME/hooks" ]; then
    cp -r "$HERMES_HOME/hooks/" "$BACKUP_DIR/hooks/"
fi

# ─── Step 10: Backup profiles (if any) ───
log "Backing up profiles..."
if [ -d "$HERMES_HOME/profiles" ]; then
    cp -r "$HERMES_HOME/profiles/" "$BACKUP_DIR/profiles/"
else
    mkdir -p "$BACKUP_DIR/profiles"
fi

# ─── Step 11: Create manifest ───
log "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.json" << EOF
{
    "backup_date": "$BACKUP_DATE",
    "hostname": "$(hostname)",
    "hermes_home": "$HERMES_HOME",
    "git_version": "$(git --version)",
    "backup_size": "$(du -sh "$BACKUP_DIR" | cut -f1)",
    "files_count": $(find "$BACKUP_DIR" -type f | wc -l),
    "skills_count": $(find "$BACKUP_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l),
    "memories_count": $(find "$BACKUP_DIR/memories" -type f 2>/dev/null | wc -l),
    "sessions_count": $(find "$BACKUP_DIR/sessions" -name "*.jsonl" 2>/dev/null | wc -l)
}
EOF

# ─── Step 12: Update latest symlink ───
cd "$CLONE_DIR/backups"
rm -f latest
ln -sf "$BACKUP_DATE" latest
cd "$CLONE_DIR"

# ─── Step 13: Clean old backups (keep last 30) ───
log "Cleaning old backups (keeping last 30)..."
cd "$CLONE_DIR/backups"
ls -dt */ 2>/dev/null | tail -n +31 | xargs rm -rf 2>/dev/null || true
cd "$CLONE_DIR"

# ─── Step 14: Commit and push ───
log "Committing backup..."
git config user.email "hermes-backup@local"
git config user.name "Hermes Backup"
git add -A
if git diff --cached --quiet; then
    log "No changes to commit"
else
    git commit -m "🔄 Backup: $BACKUP_DATE" --quiet
    log "Pushing to repository..."
    if git push --quiet 2>&1; then
        log "✅ Backup completed successfully!"
        log "📦 Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
        log "📁 Files: $(find "$BACKUP_DIR" -type f | wc -l)"
        log "🧠 Skills: $(find "$BACKUP_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l)"
        log "💭 Memories: $(find "$BACKUP_DIR/memories" -type f 2>/dev/null | wc -l)"
        log "💬 Sessions: $(find "$BACKUP_DIR/sessions" -name "*.jsonl" 2>/dev/null | wc -l)"
        echo "BACKUP_SUCCESS: $BACKUP_DATE"
    else
        err "Failed to push to repository!"
        echo "BACKUP_FAILED_PUSH: $BACKUP_DATE"
        exit 1
    fi
fi
