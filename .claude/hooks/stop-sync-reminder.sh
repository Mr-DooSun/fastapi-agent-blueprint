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
    echo "=== /sync-guidelines 강력 권고 ==="
    echo "프로젝트 기반 파일이 변경되었습니다:"
    echo "$FOUNDATION" | sed 's/^/  - /'
    echo "Claude: /sync-guidelines 실행"
    echo "Codex 사용 시: \$sync-guidelines도 실행 필요"
    echo "================================="
elif [ -n "$STRUCTURE" ]; then
    echo ""
    echo "=== /sync-guidelines 권고 ==="
    echo "도메인 구조 파일이 변경되었습니다:"
    echo "$STRUCTURE" | sed 's/^/  - /'
    echo "================================="
fi

exit 0
