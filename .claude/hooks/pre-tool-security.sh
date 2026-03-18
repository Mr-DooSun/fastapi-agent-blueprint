#!/usr/bin/env bash
# PreToolUse Hook: 코드 작성 전 보안 패턴 검사
# Exit 0 = 허용, Exit 2 = 차단

INPUT=$(cat)
echo "$INPUT" | python3 "$(dirname "$0")/pre_tool_security.py"
