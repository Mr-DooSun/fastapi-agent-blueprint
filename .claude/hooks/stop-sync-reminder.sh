#!/usr/bin/env bash
# Stop Hook: Recommend /sync-guidelines when foundation/structure files changed
# Uses git diff to detect ALL changes (Edit, Write, Bash, Subagent)
# Always exit 0 (advisory only)

set -euo pipefail

# 1) Uncommitted changes (staged + unstaged) + untracked files
UNCOMMITTED=$(git diff --name-only HEAD 2>/dev/null || true)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null || true)
CHANGED=$(printf '%s\n%s' "$UNCOMMITTED" "$UNTRACKED" | sort -u | grep -v '^$' || true)

# 2) Fallback: working tree clean but last commit is recent (within 2h) → session commit
if [ -z "$CHANGED" ]; then
    LAST_EPOCH=$(git log -1 --format='%ct' 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    if [ $((NOW_EPOCH - LAST_EPOCH)) -lt 7200 ]; then
        CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || true)
    fi
fi

[ -z "$CHANGED" ] && exit 0

# Foundation: project-wide impact
FOUNDATION=$(echo "$CHANGED" | grep -E '^(src/_core/|src/_apps/|pyproject\.toml$|\.pre-commit-config\.yaml$|AGENTS\.md$|CLAUDE\.md$|\.codex/|\.agents/|\.claude/rules/|\.claude/hooks/|\.claude/settings\.json$|docs/ai/shared/|docs/ai/shared/skills/)' || true)

# Domain Structure: domain-level architectural impact (exclude _core/_apps)
STRUCTURE=$(echo "$CHANGED" | grep -E '^src/[^_].*/((infrastructure/di/|interface/server/routers/|domain/protocols/|domain/dtos/))' || true)

if [ -n "$FOUNDATION" ]; then
    echo ""
    echo "=== /sync-guidelines strongly recommended ==="
    echo "Foundation files changed:"
    echo "$FOUNDATION" | sed 's/^/  - /'
    echo "Claude: run /sync-guidelines"
    echo "Codex: also run \$sync-guidelines"
    echo "============================================="
elif [ -n "$STRUCTURE" ]; then
    echo ""
    echo "=== /sync-guidelines recommended ==="
    echo "Domain structure files changed:"
    echo "$STRUCTURE" | sed 's/^/  - /'
    echo "===================================="
fi

# Phase 4 completion-gate (Pillar 7 + IC-11 marker lifecycle).
# Fail-open: helper crash → sync-reminder still emitted above (HC-4.7).
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPLETION_OUT=$(python3 "${HOOK_DIR}/completion_gate.py" 2>/dev/null || true)
if [ -n "$COMPLETION_OUT" ]; then
    echo ""
    echo "$COMPLETION_OUT"
fi

exit 0
