"""PreToolUse Hook: 코드 작성 전 보안 패턴 검사

Edit/Write 도구가 .py 파일에 위험 패턴을 작성하려 할 때 차단.
Exit 0 = 허용, Exit 2 = 차단
"""

import json
import re
import sys


def check_security(data: dict) -> list[str]:
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {})

    if tool == "Edit":
        path = inp.get("file_path", "")
        content = inp.get("new_string", "")
    elif tool == "Write":
        path = inp.get("file_path", "")
        content = inp.get("content", "")
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
            "SQL injection 위험: f-string SQL 감지. "
            "parameterized query 사용 필요 (SQLAlchemy ORM 또는 text(:param))"
        )

    # 1b. .format() + SQL
    if re.search(
        r"\.format\s*\(.*\).*(SELECT|INSERT|UPDATE|DELETE)", content, re.IGNORECASE
    ):
        errors.append(
            "SQL injection 위험: .format() SQL 감지. parameterized query 사용 필요"
        )

    # 1c. text() + f-string (SQLAlchemy text with dynamic string)
    if re.search(r'text\s*\(\s*f["\x27]', content):
        errors.append(
            'SQL injection 위험: text(f"...") 감지. text(:param) + bindparams 사용 필요'
        )

    # 1d. execute() + f-string 또는 .format()
    if re.search(r'\.execute\s*\(\s*f["\x27]', content):
        errors.append(
            'SQL injection 위험: execute(f"...") 감지. parameterized query 사용 필요'
        )
    if re.search(r'\.execute\s*\(["\x27].*\.format\s*\(', content, re.IGNORECASE):
        errors.append(
            'SQL injection 위험: execute("...".format()) 감지. parameterized query 사용 필요'
        )

    # 2. 하드코딩된 시크릿 (Pydantic Field, 환경변수 패턴 제외, 테스트 파일 제외)
    is_test_file = "/tests/" in path or path.endswith("_test.py")
    if not is_test_file:
        secret_patterns = [
            r'(?:password|passwd|pwd)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:secret|secret_key)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:api_key|apikey)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:private_key)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:auth_token)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:encryption_key)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:credential)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
            r'(?:access_token)\s*=\s*["\x27][^"\x27\s]{3,}["\x27]',
        ]
        for pat in secret_patterns:
            if re.search(pat, content, re.IGNORECASE):
                if not re.search(
                    r"(Field\s*\(|os\.environ|settings\.|getenv|validation_alias|\.env)",
                    content,
                ):
                    errors.append(
                        "하드코딩된 시크릿 감지. 환경변수(Settings) 또는 시크릿 매니저 사용 필요"
                    )
                    break

    # 3. Domain → Infrastructure import 금지
    if "/domain/" in path:
        if re.search(r"from\s+src\..*\.infrastructure", content):
            errors.append(
                "아키텍처 위반: Domain 레이어에서 Infrastructure import 금지. Protocol(DIP) 사용 필요"
            )

    # 4. 로그/print에 민감 데이터 포함
    if re.search(
        r"(?:logger\.|logging\.|print\s*\().*(?:password|secret|token|api_key|private_key)",
        content,
        re.IGNORECASE,
    ):
        errors.append(
            "민감 데이터 로그 노출 위험: password/secret/token 등이 로그에 포함됨. 마스킹 필요"
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
