#!/usr/bin/env bash
# PostToolUse Hook: 프로젝트 기반 파일 변경 시 /sync-guidelines 실행 권고
# Exit 0 항상 (PostToolUse는 차단 불가, 경고만)

INPUT=$(cat)

# Extract file_path from tool_input JSON
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tool_input = data.get('tool_input', {})
path = tool_input.get('file_path', '')
print(path)
" 2>/dev/null)

# Check if the file is a foundation file
if echo "$FILE_PATH" | grep -qE '(src/_core/|pyproject\.toml|\.pre-commit-config\.yaml|\.serena/memories/|\.claude/skills/_shared/|\.claude/hooks/)'; then
    echo "프로젝트 기반 파일이 변경되었습니다. /sync-guidelines 실행을 권장합니다."
    echo "  변경 파일: $FILE_PATH"
    echo "  영향: project-dna.md 및 Skills의 패턴이 outdated 될 수 있습니다."
fi

exit 0
