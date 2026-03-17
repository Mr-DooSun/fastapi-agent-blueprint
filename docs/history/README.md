# Architecture Decision History

이 프로젝트의 기술 스택 선택 근거를 기록합니다.
각 문서는 "왜 이 기술을 선택했는가"에 대한 맥락과 판단 기준을 담고 있습니다.

## 목차

| # | 제목 | 상태 | 날짜 |
|---|------|------|------|
| [000](000-rabbitmq-to-celery.md) | RabbitMQ에서 Celery로 전환 | Superseded by 001 | 2025-09-10 |
| [001](001-celery-to-taskiq.md) | Celery에서 Taskiq로 전환 | Accepted | 2025-12-24 |

## 작성 가이드

### 파일 네이밍
```
{번호}-{주제}.md
예: 001-celery-to-taskiq.md
```

### 문서 구조
```markdown
# {번호}. {제목}

- 상태: Accepted / Deprecated / Superseded by {번호}
- 날짜: YYYY-MM-DD
- 관련 이슈: #{번호}

## 배경
## 문제
## 검토한 대안
## 결정
## 근거
```

### 상태 값
- **Accepted** — 현재 적용 중
- **Deprecated** — 더 이상 유효하지 않음
- **Superseded by XXX** — 다른 결정으로 대체됨
