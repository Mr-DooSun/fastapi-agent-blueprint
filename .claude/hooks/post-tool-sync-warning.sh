#!/usr/bin/env bash
# PostToolUse Hook: Recommend running /sync-guidelines when project foundation files change
# Sets a flag file so the Stop hook can issue a final reminder.
# Always exit 0 (PostToolUse cannot block, warning only)

SYNC_FLAG="${BASH_SOURCE[0]%/.claude/*}/.sync-pending"
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
    echo "A project foundation file has been modified. Running /sync-guidelines is recommended."
    echo "  Changed file: $FILE_PATH"
    echo "  Impact: Patterns in project-dna.md and Skills may become outdated."

    # Set flag for Stop hook
    echo "$FILE_PATH" >> "$SYNC_FLAG"
fi

exit 0
