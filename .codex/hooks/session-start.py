from __future__ import annotations

import json

message = "\n".join(
    [
        "Codex repo harness active:",
        "- Shared rules: AGENTS.md",
        "- Repo workflows: .agents/skills/",
        "- Command hooks: .codex/hooks.json",
        "- Use `codex -p research` or `codex --search` only when live web search is actually needed.",
        "- If context feels tight, keep root AGENTS.md short and prefer AGENTS.override.md plus named skills.",
        "- Codex memories are personal/session optimization, not the team's canonical rules.",
    ]
)

print(json.dumps({"systemMessage": message}))
