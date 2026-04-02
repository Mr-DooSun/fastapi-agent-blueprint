#!/usr/bin/env bash
# Stop Hook: Final reminder to run /sync-guidelines if core files were modified
# The flag file is created by post-tool-sync-warning.sh during PostToolUse.
# Always exit 0 (Stop hooks are informational only)

SYNC_FLAG="${BASH_SOURCE[0]%/.claude/*}/.sync-pending"

if [ -f "$SYNC_FLAG" ]; then
    MODIFIED_FILES=$(sort -u "$SYNC_FLAG")
    echo ""
    echo "=== /sync-guidelines Reminder ==="
    echo "The following core files were modified but /sync-guidelines was not run:"
    echo "$MODIFIED_FILES" | sed 's/^/  - /'
    echo ""
    echo "Run /sync-guidelines to keep Skills and project-dna.md in sync."
    echo "================================="
fi

exit 0
