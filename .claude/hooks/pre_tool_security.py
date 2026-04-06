"""PreToolUse Hook: Security pattern check before code writing

Blocks when Edit/Write/Bash tools attempt to write dangerous patterns to .py files.
Exit 0 = allow, Exit 2 = block
"""

import json
import re
import sys


def _extract_bash_write(command: str) -> tuple[str, str] | None:
    """Bash 명령에서 .py 파일 쓰기를 감지하여 (path, content) 반환.

    쓰기가 없으면 None.
    """
    # > 또는 >> 리다이렉트
    m = re.search(r">{1,2}\s*(\S+\.py)\b", command)
    if m:
        return (m.group(1), command)
    # tee [-a] file.py
    m = re.search(r"\btee\s+(?:-a\s+)?(\S+\.py)\b", command)
    if m:
        return (m.group(1), command)
    # heredoc: << EOF > file.py
    m = re.search(r"<<\s*[\x27\"]?(\w+)[\x27\"]?\s*>{0,2}\s*(\S+\.py)\b", command)
    if m:
        return (m.group(2), command)
    return None


def check_security(data: dict) -> list[str]:
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {})

    if tool == "Edit":
        path = inp.get("file_path", "")
        content = inp.get("new_string", "")
    elif tool == "Write":
        path = inp.get("file_path", "")
        content = inp.get("content", "")
    elif tool == "Bash":
        result = _extract_bash_write(inp.get("command", ""))
        if result is None:
            return []
        path, content = result
    else:
        return []

    if not path.endswith(".py"):
        return []

    errors = []

    # 1. SQL Injection: f-string SQL
    if re.search(
        r'f["\x27].*\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b', content, re.IGNORECASE
    ):
        errors.append(
            "SQL injection risk: f-string SQL detected. "
            "Use parameterized queries (SQLAlchemy ORM or text(:param))"
        )

    # 1b. .format() + SQL
    if re.search(
        r"\.format\s*\(.*\).*(SELECT|INSERT|UPDATE|DELETE)", content, re.IGNORECASE
    ):
        errors.append(
            "SQL injection risk: .format() SQL detected. Use parameterized queries"
        )

    # 1c. text() + f-string (SQLAlchemy text with dynamic string)
    if re.search(r'text\s*\(\s*f["\x27]', content):
        errors.append(
            'SQL injection risk: text(f"...") detected. Use text(:param) + bindparams'
        )

    # 1d. execute() + f-string or .format()
    if re.search(r'\.execute\s*\(\s*f["\x27]', content):
        errors.append(
            'SQL injection risk: execute(f"...") detected. Use parameterized queries'
        )
    if re.search(r'\.execute\s*\(["\x27].*\.format\s*\(', content, re.IGNORECASE):
        errors.append(
            'SQL injection risk: execute("...".format()) detected. Use parameterized queries'
        )

    # 2. Hardcoded secrets (excludes Pydantic Field, env var patterns, and test files)
    _quoted_value_re = (
        r"(?:[bruf]*)(?:"
        r'"{3}[\s\S]{3,}?"{3}'  # """..."""
        r"|\x27{3}[\s\S]{3,}?\x27{3}"  # '''...'''
        r'|["\x27][^"\x27\s]{3,}["\x27]'  # "..." or '...'
        r")"
    )
    _sensitive_keywords = [
        r"(?:password|passwd|pwd)",
        r"(?:secret|secret_key)",
        r"(?:api_key|apikey)",
        r"(?:private_key)",
        r"(?:auth_token)",
        r"(?:encryption_key)",
        r"(?:credential)",
        r"(?:access_token)",
    ]
    is_test_file = "/tests/" in path or path.endswith("_test.py")
    if not is_test_file:
        secret_patterns = [
            kw + r"\s*=\s*" + _quoted_value_re for kw in _sensitive_keywords
        ]
        for pat in secret_patterns:
            if re.search(pat, content, re.IGNORECASE):
                if not re.search(
                    r"(Field\s*\(|os\.environ|settings\.|getenv|validation_alias|\.env)",
                    content,
                ):
                    errors.append(
                        "Hardcoded secret detected. Use environment variables (Settings) or a secret manager"
                    )
                    break

    # 3. Prohibit Domain → Infrastructure import
    if "/domain/" in path:
        if re.search(r"from\s+src\..*\.infrastructure", content):
            errors.append(
                "Architecture violation: Domain layer must not import Infrastructure. Use Protocol (DIP)"
            )

    # 4. Sensitive data in logs/print
    if re.search(
        r"(?:logger\.|logging\.|print\s*\().*(?:password|secret|token|api_key|private_key)",
        content,
        re.IGNORECASE,
    ):
        errors.append(
            "Sensitive data exposure risk in logs: password/secret/token found in log output. Masking required"
        )

    return errors


def main():
    data = json.load(sys.stdin)
    errors = check_security(data)

    if errors:
        for e in errors:
            print(f"[BLOCKED] {e}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
