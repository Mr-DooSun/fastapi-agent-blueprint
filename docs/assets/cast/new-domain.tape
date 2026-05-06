Output docs/assets/cast/new-domain.gif

Set FontSize 13
Set Width 1400
Set Height 700
Set Theme "Dracula"
Set Framerate 24
Set TypingSpeed 40ms
Set PlaybackSpeed 1

# ── Context ────────────────────────────────────────────────────────────────────
# Run from the project root (fastapi-agent-blueprint/).
# This tape shows the /new-domain skill scaffolding a new domain,
# then running tests to verify it passes.
#
# Record with:
#   VHS_CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
#   vhs docs/assets/cast/new-domain.tape
# ──────────────────────────────────────────────────────────────────────────────

Require find
Require uv

# ── Show current src/ layout ───────────────────────────────────────────────────
Type "ls src/"
Enter
Sleep 1s

# ── Run /new-domain skill (simulated via the skill's core command) ─────────────
# In practice, a user runs: /new-domain order
# Here we demonstrate the output by showing what the skill creates.
Type "# /new-domain order  →  scaffolds 44 files automatically"
Enter
Sleep 500ms

# Show the file count the skill produces
Type `find src/order -type f 2>/dev/null | wc -l || echo "Run '/new-domain order' in Claude Code to scaffold this domain"`
Enter
Sleep 1s

# ── Show ls of new domain ─────────────────────────────────────────────────────
Type "ls src/ | sort"
Enter
Sleep 1s

# ── Run tests ────────────────────────────────────────────────────────────────
Type "uv run pytest tests/ -q --tb=no 2>&1 | tail -5"
Enter
Sleep 8s

Type "# Domain scaffold complete — add your business logic to src/order/domain/"
Enter
Sleep 1s
