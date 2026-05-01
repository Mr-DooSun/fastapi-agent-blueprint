from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

HANDOFF_GUIDE_URL = (
    "https://github.com/Mr-DooSun/fastapi-agent-blueprint"
    "/blob/main/docs/frontend-handoff.md"
)

# Card data shared by every theme renderer. Keep order stable: the first two
# entries are the recommended viewers, the rest are alternates.
DOCS_CARDS: list[dict[str, str]] = [
    {
        "key": "elements",
        "href": "/api/docs-elements",
        "title": "Stoplight Elements",
        "tagline": "Interactive, three-pane reader. Best for browsing.",
        "label": "Recommended — Visual",
        "kind": "primary",
        "icon": "🎨",
    },
    {
        "key": "scalar",
        "href": "/api/docs-scalar",
        "title": "Scalar API Reference",
        "tagline": "Modern reference with try-it that bridges into a client.",
        "label": "Recommended — Try-it",
        "kind": "primary",
        "icon": "✨",
    },
    {
        "key": "swagger",
        "href": "/api/docs-swagger",
        "title": "Swagger UI",
        "tagline": "FastAPI's bundled default. Familiar to most teams.",
        "label": "Compatibility",
        "kind": "secondary",
        "icon": "📚",
    },
    {
        "key": "redoc",
        "href": "/api/docs-redoc",
        "title": "ReDoc",
        "tagline": "Documentation-first three-panel layout.",
        "label": "Clean",
        "kind": "secondary",
        "icon": "📖",
    },
    {
        "key": "rapidoc",
        "href": "/api/docs-rapidoc",
        "title": "RapiDoc",
        "tagline": "Lightweight viewer. Fast initial load.",
        "label": "Fast",
        "kind": "secondary",
        "icon": "⚡",
    },
]


def _handoff_cards(download_url: str) -> list[dict[str, str]]:
    # `kind="secondary"` keeps the Recommended visual weight reserved for the
    # two viewer cards. Themes that read `kind` (Brutalist / Minimal / Mac /
    # Refined) treat handoff rows as quieter; themes that ignore it are
    # unaffected.
    return [
        {
            "key": "download",
            "href": download_url,
            "title": "Download OpenAPI (JSON)",
            "tagline": "Save the live spec as openapi.json for Postman, Bruno, or any client.",
            "label": "Spec",
            "external": "false",
            "kind": "secondary",
            "icon": "⬇️",
        },
        {
            "key": "handoff",
            "href": HANDOFF_GUIDE_URL,
            "title": "Frontend Handoff Guide",
            "tagline": "Contract scope, test client comparison, and TypeScript SDK recipes.",
            "label": "Guide",
            "external": "true",
            "kind": "secondary",
            "icon": "🧭",
        },
    ]


VALID_THEMES = {"brutalist", "editorial", "minimal", "mac", "refined"}


@router.get(
    "/docs",
    include_in_schema=False,
    description="API Docs Selector - Main page for choosing among various documentation UIs",
)
def docs_selector(request: Request, theme: str | None = None):
    root_path = request.scope.get("root_path", "")
    download_url = f"{root_path}/openapi-download.json"
    handoff_cards = _handoff_cards(download_url)
    docs_cards = DOCS_CARDS

    selected = theme if theme in VALID_THEMES else None
    if selected == "brutalist":
        body = _render_brutalist(docs_cards, handoff_cards)
    elif selected == "editorial":
        body = _render_editorial(docs_cards, handoff_cards)
    elif selected == "minimal":
        body = _render_minimal(docs_cards, handoff_cards)
    elif selected == "mac":
        body = _render_mac(docs_cards, handoff_cards)
    elif selected == "refined":
        body = _render_refined(docs_cards, handoff_cards)
    else:
        body = _render_default(docs_cards, handoff_cards)

    return HTMLResponse(body)


# ---------------------------------------------------------------------------
# Default theme — kept as the production surface from PR #156. Purple gradient,
# rounded cards, the original "AI-pattern" look. Future cleanup will replace
# this with whichever preview theme the user picks.
# ---------------------------------------------------------------------------


def _render_default(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Documentation Selector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh; padding: 20px;
        display: flex; align-items: center; justify-content: center;
      }}
      .container {{
        max-width: 1000px; width: 100%;
        background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
        border-radius: 24px; padding: 60px 40px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
      }}
      .header {{ text-align: center; margin-bottom: 50px; }}
      h1 {{
        font-size: 3.5rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 16px; letter-spacing: -0.02em;
      }}
      .subtitle {{ font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto; line-height: 1.6; }}
      .docs-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 40px; }}
      .docs-card {{
        background: white; border-radius: 16px; padding: 32px 24px;
        text-decoration: none; color: inherit; display: block;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e2e8f0; position: relative; overflow: hidden;
      }}
      .docs-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0); transition: transform 0.3s ease;
      }}
      .docs-card:hover {{ transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); border-color: #667eea; }}
      .docs-card:hover::before {{ transform: scaleX(1); }}
      .docs-title {{ font-size: 1.4rem; font-weight: 600; margin-bottom: 12px; color: #1e293b; line-height: 1.3; }}
      .docs-desc {{ color: #64748b; margin: 0; font-size: 0.95rem; line-height: 1.6; }}
      .badge {{
        display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white;
        padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;
        margin-top: 16px; text-transform: uppercase; letter-spacing: 0.5px;
      }}
      .badge.muted {{ background: #e2e8f0; color: #475569; }}
      .handoff-section {{ margin-top: 56px; padding-top: 40px; border-top: 1px solid #e2e8f0; }}
      .handoff-section h2 {{ font-size: 1.6rem; font-weight: 600; color: #1e293b; text-align: center; margin-bottom: 8px; }}
      .handoff-section p.handoff-subtitle {{ text-align: center; color: #64748b; max-width: 640px; margin: 0 auto 28px; line-height: 1.6; }}
      .handoff-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
      .preview-bar {{
        position: fixed; top: 16px; right: 16px; background: rgba(255,255,255,0.95);
        padding: 8px 12px; border-radius: 8px; font-size: 0.78rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: flex; gap: 8px; align-items: center;
      }}
      .preview-bar a {{ color: #4a5568; text-decoration: none; padding: 2px 6px; border-radius: 4px; }}
      .preview-bar a:hover {{ background: #edf2f7; }}
      .preview-bar a.active {{ background: #667eea; color: white; }}
    </style>
  </head>
  <body>
    {_preview_bar("default")}
    <div class="container">
      <div class="header">
        <h1>🚀 API Documentation</h1>
        <p class="subtitle">
          Choose your preferred style of API documentation below.<br>
          Each one offers a unique set of features and user experience.
        </p>
      </div>
      <div class="docs-grid">
        {"".join(_default_card(c) for c in docs_cards)}
      </div>
      <section class="handoff-section">
        <h2>📦 Share with Frontend</h2>
        <p class="handoff-subtitle">
          For testing flows where inputs, tokens, or environments need to persist
          (Postman / Bruno / Insomnia / Hoppscotch / Scalar Client), hand off the
          OpenAPI spec and let the frontend import it into their tool of choice.
        </p>
        <div class="handoff-grid">
          {"".join(_default_handoff_card(c) for c in handoff_cards)}
        </div>
      </section>
    </div>
  </body>
</html>"""


def _default_card(card: dict[str, str]) -> str:
    badge_class = "badge" if card["kind"] == "primary" else "badge muted"
    icon = card.get("icon", "")
    return f"""
    <a href="{card["href"]}" class="docs-card">
      <span aria-hidden="true" style="font-size:3rem; display:block; text-align:center; margin-bottom:16px;">{icon}</span>
      <div class="docs-title" style="text-align:center;">{card["title"]}</div>
      <p class="docs-desc" style="text-align:center;">{card["tagline"]}</p>
      <div style="text-align:center;"><span class="{badge_class}">{card["label"]}</span></div>
    </a>"""


def _default_handoff_card(card: dict[str, str]) -> str:
    target = ' target="_blank" rel="noopener"' if card["external"] == "true" else ""
    download = " download" if card["external"] == "false" else ""
    icon = card.get("icon", "")
    return f"""
    <a href="{card["href"]}" class="docs-card"{target}{download}>
      <span aria-hidden="true" style="font-size:3rem; display:block; text-align:center; margin-bottom:16px;">{icon}</span>
      <div class="docs-title" style="text-align:center;">{card["title"]}</div>
      <p class="docs-desc" style="text-align:center;">{card["tagline"]}</p>
      <div style="text-align:center;"><span class="badge">{card["label"]}</span></div>
    </a>"""


def _preview_bar(active: str) -> str:
    """Render a tiny floating bar that lets the reviewer hop between previews.

    The bar is preview-only. Once the redesign is picked, this helper plus
    `?theme=` dispatch will be removed and the chosen renderer becomes the
    sole `_render` for `/docs`.
    """
    items = [
        ("default", "Current"),
        ("brutalist", "Brutalist"),
        ("editorial", "Editorial"),
        ("minimal", "Minimal"),
        ("mac", "Mac"),
        ("refined", "Refined"),
    ]
    rendered = []
    for key, label in items:
        href = "/docs" if key == "default" else f"/docs?theme={key}"
        klass = "active" if key == active else ""
        rendered.append(f'<a href="{href}" class="{klass}">{label}</a>')
    return f'<div class="preview-bar">Preview · {" ".join(rendered)}</div>'


# ---------------------------------------------------------------------------
# Brutalist Terminal — black background, monospace, single-line frame, no
# gradients / shadows / emojis. Reads like a TUI panel.
# ---------------------------------------------------------------------------


def _render_brutalist(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    rows = "\n".join(_brutalist_row(c) for c in docs_cards)
    handoff_rows = "\n".join(_brutalist_row(c) for c in handoff_cards)
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>fastapi-agent-blueprint :: docs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      :root {{
        --bg: #0a0a0a;
        --fg: #e6e6e6;
        --muted: #7a7a7a;
        --border: #2a2a2a;
        --border-hover: #4a4a4a;
        --accent: #e6c300;
      }}
      body {{
        font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace;
        background: var(--bg); color: var(--fg);
        min-height: 100vh; padding: 48px 24px; line-height: 1.55;
        font-size: 14px;
      }}
      .frame {{ max-width: 760px; margin: 0 auto; }}
      .head {{ border: 1px solid var(--border); padding: 20px 24px; margin-bottom: 0; }}
      .head .title {{ color: var(--fg); font-weight: 600; }}
      .head .meta {{ color: var(--muted); font-size: 12px; margin-top: 4px; }}
      .section-head {{
        border: 1px solid var(--border); border-top: none;
        padding: 12px 24px; color: var(--muted); font-size: 12px;
        text-transform: uppercase; letter-spacing: 0.1em;
      }}
      .row {{
        display: block; padding: 18px 24px;
        border: 1px solid var(--border); border-top: none;
        text-decoration: none; color: var(--fg); transition: border-color 0.12s linear;
        position: relative;
      }}
      .row:hover {{ border-color: var(--border-hover); }}
      .row.primary {{
        border-left: 3px solid var(--accent); padding-left: 22px;
      }}
      .row .marker {{ color: var(--muted); margin-right: 8px; }}
      .row.primary .marker {{ color: var(--accent); }}
      .row .name {{ font-weight: 600; }}
      .row.primary .name {{ color: var(--accent); }}
      .row .desc {{ color: var(--muted); margin-top: 4px; font-size: 13px; }}
      .row .label {{ color: var(--accent); font-size: 11px; margin-top: 8px; display: inline-block; }}
      .row .label.muted {{ color: var(--muted); }}
      .row.last {{ border-bottom: 1px solid var(--border); }}
      .preview-bar {{
        position: fixed; top: 12px; right: 12px;
        background: var(--bg); border: 1px solid var(--border);
        padding: 6px 10px; font-size: 12px; display: flex; gap: 6px; align-items: center;
      }}
      .preview-bar .lbl {{ color: var(--muted); margin-right: 4px; }}
      .preview-bar a {{ color: var(--muted); text-decoration: none; padding: 2px 6px; }}
      .preview-bar a:hover {{ color: var(--fg); }}
      .preview-bar a.active {{ color: var(--accent); }}
    </style>
  </head>
  <body>
    {_preview_bar("brutalist")}
    <div class="frame">
      <div class="head">
        <div class="title">fastapi-agent-blueprint :: api docs</div>
        <div class="meta">5 viewers · 2 handoff actions · selector @ /docs</div>
      </div>
      <div class="section-head">viewer</div>
{rows}
      <div class="section-head">handoff</div>
{handoff_rows}
    </div>
  </body>
</html>"""


def _brutalist_row(card: dict[str, str]) -> str:
    kind = card.get("kind", "primary")
    row_class = "row primary" if kind == "primary" else "row"
    label_class = "label" if kind == "primary" else "label muted"
    is_external = card.get("external", "false") == "true"
    target = ' target="_blank" rel="noopener"' if is_external else ""
    download = (
        " download"
        if card.get("external") == "false" and card["key"] == "download"
        else ""
    )
    marker = "*" if kind == "primary" else "&gt;"
    return f"""      <a class="{row_class}" href="{card["href"]}"{target}{download}>
        <div><span class="marker" aria-hidden="true">{marker}</span><span class="name">{card["title"]}</span></div>
        <div class="desc">{card["tagline"]}</div>
        <div class="{label_class}">[{card["label"].lower()}]</div>
      </a>"""


# ---------------------------------------------------------------------------
# Editorial / Print — cream background, serif headings, horizontal rules
# instead of cards. Reads like a magazine table of contents.
# ---------------------------------------------------------------------------


def _render_editorial(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    rows = "\n".join(_editorial_row(c) for c in docs_cards)
    handoff_rows = "\n".join(_editorial_row(c) for c in handoff_cards)
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>FastAPI Agent Blueprint — API Documentation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      :root {{
        --bg: #f7f3ec;
        --fg: #1a1a1a;
        --muted: #6b6353;
        --rule: #d4cdb8;
        --link: #1a1a1a;
        --link-hover: #5a3d1e;
      }}
      body {{
        background: var(--bg); color: var(--fg);
        font-family: 'Inter', -apple-system, system-ui, sans-serif;
        min-height: 100vh; padding: 80px 24px 120px; line-height: 1.6;
      }}
      .frame {{ max-width: 720px; margin: 0 auto; }}
      .masthead {{ border-bottom: 1px solid var(--rule); padding-bottom: 24px; margin-bottom: 32px; }}
      .masthead .eyebrow {{
        font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em;
        color: var(--muted); margin-bottom: 12px;
      }}
      .masthead h1 {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 2.6rem; font-weight: 600; line-height: 1.1; letter-spacing: -0.01em;
      }}
      .masthead .lede {{
        margin-top: 12px; color: var(--muted); font-size: 1.05rem; max-width: 560px;
      }}
      .section-title {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.2rem; font-weight: 600; margin: 48px 0 16px;
        color: var(--fg); padding-bottom: 8px; border-bottom: 1px solid var(--rule);
      }}
      .row {{
        display: block; padding: 22px 0; border-bottom: 1px solid var(--rule);
        text-decoration: none; color: var(--link); transition: color 0.15s ease;
      }}
      .row:hover {{ color: var(--link-hover); }}
      .row .row-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 16px; }}
      .row .row-leading {{ display: flex; align-items: baseline; gap: 14px; min-width: 0; flex: 1; }}
      .row .row-icon {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.5rem; color: var(--muted); flex-shrink: 0;
        font-style: italic; min-width: 24px; text-align: center;
      }}
      .row.primary .row-icon {{ color: var(--link); font-weight: 600; font-style: normal; }}
      .row .row-title {{
        font-family: 'Newsreader', Georgia, serif; font-size: 1.45rem; font-weight: 600; line-height: 1.2;
      }}
      .row.primary .row-title {{ font-size: 1.55rem; }}
      .row .arrow {{ color: var(--muted); font-size: 1.1rem; }}
      .row:hover .arrow {{ color: var(--link-hover); }}
      .row .row-desc {{ color: var(--muted); margin-top: 6px; font-size: 0.98rem; }}
      .row .row-label {{
        margin-top: 10px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.18em;
        color: var(--muted);
      }}
      .row.primary .row-label {{ color: var(--link); font-weight: 600; }}
      .preview-bar {{
        position: fixed; top: 16px; right: 16px;
        background: var(--bg); border: 1px solid var(--rule);
        padding: 6px 10px; font-size: 12px; display: flex; gap: 6px; align-items: center;
        font-family: 'Inter', sans-serif;
      }}
      .preview-bar .lbl {{ color: var(--muted); margin-right: 4px; }}
      .preview-bar a {{ color: var(--muted); text-decoration: none; padding: 2px 6px; }}
      .preview-bar a:hover {{ color: var(--fg); }}
      .preview-bar a.active {{ color: var(--fg); font-weight: 500; }}
    </style>
  </head>
  <body>
    {_preview_bar("editorial")}
    <div class="frame">
      <div class="masthead">
        <div class="eyebrow">FastAPI Agent Blueprint · API Documentation</div>
        <h1>Five readers, two handoffs.</h1>
        <p class="lede">
          The browser viewers are for reading. For the parts that need persisted
          state — tokens, environments, request bodies — hand off the spec.
        </p>
      </div>
      <div class="section-title">Viewers</div>
{rows}
      <div class="section-title">Handoff</div>
{handoff_rows}
    </div>
  </body>
</html>"""


def _editorial_row(card: dict[str, str]) -> str:
    kind = card.get("kind", "primary")
    row_class = "row primary" if kind == "primary" else "row"
    is_external = card.get("external", "false") == "true"
    target = ' target="_blank" rel="noopener"' if is_external else ""
    download = (
        " download"
        if card.get("external") == "false" and card["key"] == "download"
        else ""
    )
    icon = card.get("icon", "")
    return f"""      <a class="{row_class}" href="{card["href"]}"{target}{download}>
        <div class="row-head">
          <div class="row-leading">
            <span class="row-icon" aria-hidden="true">{icon}</span>
            <div class="row-title">{card["title"]}</div>
          </div>
          <div class="arrow">&rarr;</div>
        </div>
        <div class="row-desc">{card["tagline"]}</div>
        <div class="row-label">{card["label"]}</div>
      </a>"""


# ---------------------------------------------------------------------------
# Minimal Native — white background, system fonts, GitHub-flavoured 1px boxes.
# Quiet and forgettable in the best way.
# ---------------------------------------------------------------------------


def _render_minimal(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    rows = "\n".join(_minimal_row(c) for c in docs_cards)
    handoff_rows = "\n".join(_minimal_row(c) for c in handoff_cards)
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Documentation — fastapi-agent-blueprint</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      :root {{
        --bg: #ffffff;
        --fg: #0e0e10;
        --muted: #57606a;
        --border: #d0d7de;
        --border-hover: #0969da;
        --accent: #0969da;
      }}
      body {{
        background: var(--bg); color: var(--fg);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
        min-height: 100vh; padding: 64px 24px; line-height: 1.5;
        font-size: 15px;
      }}
      .frame {{ max-width: 720px; margin: 0 auto; }}
      .head h1 {{ font-size: 1.6rem; font-weight: 600; margin-bottom: 4px; }}
      .head .meta {{ color: var(--muted); font-size: 13px; }}
      .section-head {{
        margin: 36px 0 12px; font-size: 12px; font-weight: 600; color: var(--muted);
        text-transform: uppercase; letter-spacing: 0.04em;
      }}
      .list {{ display: flex; flex-direction: column; gap: 8px; }}
      .row {{
        display: flex; align-items: center; justify-content: space-between; gap: 16px;
        padding: 14px 16px; border: 1px solid var(--border); border-radius: 6px;
        text-decoration: none; color: var(--fg); transition: border-color 0.12s ease;
      }}
      .row:hover {{ border-color: var(--border-hover); }}
      .row.primary {{
        border-left: 3px solid var(--accent); padding-left: 14px;
      }}
      .row .row-leading {{ display: flex; align-items: center; gap: 12px; min-width: 0; flex: 1; }}
      .row .row-icon {{
        font-size: 1.5rem; line-height: 1; flex-shrink: 0;
        width: 32px; text-align: center;
      }}
      .row .row-text {{ min-width: 0; }}
      .row .row-text .name {{ font-weight: 600; font-size: 0.98rem; }}
      .row .row-text .desc {{ color: var(--muted); font-size: 13px; margin-top: 2px; }}
      .row .row-meta {{ display: flex; align-items: center; gap: 10px; flex-shrink: 0; }}
      .row .label {{
        font-size: 11px; color: var(--muted); border: 1px solid var(--border);
        padding: 2px 8px; border-radius: 999px; white-space: nowrap;
      }}
      .row .label.primary {{
        color: white; background: var(--accent); border-color: var(--accent);
      }}
      .row .arrow {{ color: var(--muted); font-size: 14px; }}
      .row:hover .arrow {{ color: var(--accent); }}
      .preview-bar {{
        position: fixed; top: 12px; right: 12px;
        background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
        padding: 6px 10px; font-size: 12px; display: flex; gap: 6px; align-items: center;
      }}
      .preview-bar .lbl {{ color: var(--muted); margin-right: 4px; }}
      .preview-bar a {{ color: var(--muted); text-decoration: none; padding: 2px 6px; border-radius: 3px; }}
      .preview-bar a:hover {{ color: var(--fg); }}
      .preview-bar a.active {{ color: var(--accent); font-weight: 500; }}
    </style>
  </head>
  <body>
    {_preview_bar("minimal")}
    <div class="frame">
      <div class="head">
        <h1>API Documentation</h1>
        <div class="meta">fastapi-agent-blueprint · dev environment · /docs</div>
      </div>
      <div class="section-head">Viewers</div>
      <div class="list">
{rows}
      </div>
      <div class="section-head">Handoff</div>
      <div class="list">
{handoff_rows}
      </div>
    </div>
  </body>
</html>"""


def _minimal_row(card: dict[str, str]) -> str:
    kind = card.get("kind", "primary")
    row_class = "row primary" if kind == "primary" else "row"
    label_class = "label primary" if kind == "primary" else "label"
    is_external = card.get("external", "false") == "true"
    target = ' target="_blank" rel="noopener"' if is_external else ""
    download = (
        " download"
        if card.get("external") == "false" and card["key"] == "download"
        else ""
    )
    icon = card.get("icon", "")
    return f"""        <a class="{row_class}" href="{card["href"]}"{target}{download}>
          <div class="row-leading">
            <span class="row-icon" aria-hidden="true">{icon}</span>
            <div class="row-text">
              <div class="name">{card["title"]}</div>
              <div class="desc">{card["tagline"]}</div>
            </div>
          </div>
          <div class="row-meta">
            <span class="{label_class}">{card["label"]}</span>
            <span class="arrow">&rsaquo;</span>
          </div>
        </a>"""


# ---------------------------------------------------------------------------
# Mac System Native — System Settings dialog inspired. Translucent panel,
# SF font stack, traffic-light header, compact list rows with chevrons.
# ---------------------------------------------------------------------------


def _render_mac(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    rows = "\n".join(_mac_row(c) for c in docs_cards)
    handoff_rows = "\n".join(_mac_row(c) for c in handoff_cards)
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Documentation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      :root {{
        --bg: #e6e6ec;
        --panel: rgba(246, 246, 248, 0.92);
        --panel-border: rgba(0,0,0,0.08);
        --fg: #1d1d1f;
        --muted: #6b6b70;
        --row-border: rgba(0,0,0,0.06);
        --accent: #007aff;
        --row-bg: rgba(255,255,255,0.6);
      }}
      body {{
        background: linear-gradient(180deg, #d8d8df 0%, #ececf2 100%); color: var(--fg);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
        min-height: 100vh; padding: 48px 24px;
        display: flex; align-items: flex-start; justify-content: center;
        font-size: 14px;
      }}
      .window {{
        max-width: 640px; width: 100%;
        background: var(--panel); backdrop-filter: blur(20px);
        border: 1px solid var(--panel-border); border-radius: 12px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.18), 0 1px 0 rgba(255,255,255,0.6) inset;
        overflow: hidden;
      }}
      .titlebar {{
        display: flex; align-items: center; padding: 12px 16px;
        border-bottom: 1px solid var(--row-border); background: rgba(255,255,255,0.4);
      }}
      .traffic {{ display: flex; gap: 8px; }}
      .traffic span {{ width: 12px; height: 12px; border-radius: 50%; display: block; }}
      .traffic .red {{ background: #ff5f57; }}
      .traffic .yellow {{ background: #febc2e; }}
      .traffic .green {{ background: #28c840; }}
      .titlebar .title {{ flex: 1; text-align: center; font-weight: 600; font-size: 13px; color: var(--fg); }}
      .titlebar .spacer {{ width: 52px; }}
      .body {{ padding: 24px 24px 28px; }}
      .body h2 {{ font-size: 1.5rem; font-weight: 600; margin-bottom: 4px; letter-spacing: -0.01em; }}
      .body .subtitle {{ color: var(--muted); margin-bottom: 24px; font-size: 13px; }}
      .group {{
        background: var(--row-bg); border: 1px solid var(--row-border); border-radius: 10px;
        overflow: hidden; margin-bottom: 16px;
      }}
      .group-label {{
        font-size: 11px; font-weight: 500; color: var(--muted);
        text-transform: uppercase; letter-spacing: 0.06em;
        padding: 0 4px 6px; margin-top: 8px;
      }}
      .row {{
        display: flex; align-items: center; gap: 12px;
        padding: 11px 14px; border-bottom: 1px solid var(--row-border);
        text-decoration: none; color: var(--fg); transition: background 0.1s ease;
      }}
      .row:last-child {{ border-bottom: none; }}
      .row:hover {{ background: rgba(0,122,255,0.08); }}
      .row .row-icon {{
        font-size: 1.6rem; line-height: 1; flex-shrink: 0;
        width: 32px; text-align: center;
      }}
      .row .row-text {{ flex: 1; min-width: 0; }}
      .row .row-text .name {{ font-weight: 500; font-size: 14px; }}
      .row.primary .row-text .name {{ font-weight: 700; color: var(--accent); }}
      .row .row-text .desc {{ color: var(--muted); font-size: 12px; margin-top: 1px; }}
      .row .label {{
        font-size: 11px; color: var(--muted); padding: 2px 8px;
        border-radius: 5px; background: rgba(0,0,0,0.05); white-space: nowrap;
      }}
      .row .label.primary {{ color: white; background: var(--accent); }}
      .row .chevron {{ color: var(--muted); font-size: 14px; flex-shrink: 0; }}
      .preview-bar {{
        position: fixed; top: 14px; right: 14px;
        background: rgba(255,255,255,0.85); backdrop-filter: blur(12px);
        border: 1px solid var(--panel-border); border-radius: 8px;
        padding: 6px 10px; font-size: 12px; display: flex; gap: 6px; align-items: center;
      }}
      .preview-bar .lbl {{ color: var(--muted); margin-right: 4px; }}
      .preview-bar a {{ color: var(--muted); text-decoration: none; padding: 2px 6px; border-radius: 4px; }}
      .preview-bar a:hover {{ color: var(--fg); }}
      .preview-bar a.active {{ color: white; background: var(--accent); }}
    </style>
  </head>
  <body>
    {_preview_bar("mac")}
    <div class="window">
      <div class="titlebar">
        <div class="traffic">
          <span class="red"></span><span class="yellow"></span><span class="green"></span>
        </div>
        <div class="title">API Documentation</div>
        <div class="spacer"></div>
      </div>
      <div class="body">
        <h2>Pick a viewer</h2>
        <p class="subtitle">Or hand the spec off to a real client below.</p>
        <div class="group-label">Viewers</div>
        <div class="group">
{rows}
        </div>
        <div class="group-label">Handoff</div>
        <div class="group">
{handoff_rows}
        </div>
      </div>
    </div>
  </body>
</html>"""


def _mac_row(card: dict[str, str]) -> str:
    kind = card.get("kind", "primary")
    row_class = "row primary" if kind == "primary" else "row"
    label_class = "label primary" if kind == "primary" else "label"
    is_external = card.get("external", "false") == "true"
    target = ' target="_blank" rel="noopener"' if is_external else ""
    download = (
        " download"
        if card.get("external") == "false" and card["key"] == "download"
        else ""
    )
    icon = card.get("icon", "")
    return f"""          <a class="{row_class}" href="{card["href"]}"{target}{download}>
            <span class="row-icon" aria-hidden="true">{icon}</span>
            <div class="row-text">
              <div class="name">{card["title"]}</div>
              <div class="desc">{card["tagline"]}</div>
            </div>
            <span class="{label_class}">{card["label"]}</span>
            <span class="chevron">&rsaquo;</span>
          </a>"""


# ---------------------------------------------------------------------------
# Refined Modern — keeps the legibility tools of the original surface (large
# rounded cards, emoji icons as visual cues, three-column grid, strong card /
# background contrast, hierarchy via shadow + colour badge) but strips the
# real AI-pattern clichés: purple gradient backgrounds, gradient text via
# -webkit-background-clip, gradient badges, frosted glass `backdrop-filter`.
# Light + dark variants share the same structure; theme is user-toggleable
# and persists in localStorage with a prefers-color-scheme fallback.
# ---------------------------------------------------------------------------


def _render_refined(
    docs_cards: list[dict[str, str]],
    handoff_cards: list[dict[str, str]],
) -> str:
    docs_grid = "".join(_refined_card(c) for c in docs_cards)
    handoff_grid = "".join(_refined_card(c) for c in handoff_cards)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>API Documentation — fastapi-agent-blueprint</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- theme: refined-modern -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
      (function() {{
        try {{
          var stored = localStorage.getItem('docs-selector-theme');
          if (stored === 'dark' || stored === 'light') {{
            document.documentElement.setAttribute('data-theme', stored);
          }}
        }} catch (e) {{ /* ignore */ }}
      }})();
    </script>
    <style>
      :root {{
        --bg: #f1f5f9;
        --card: #ffffff;
        --title: #0f172a;
        --desc: #475569;
        --muted: #64748b;
        --border: #e2e8f0;
        --border-strong: #cbd5e1;
        --shadow: 0 4px 12px rgba(15,23,42,0.06), 0 1px 3px rgba(15,23,42,0.04);
        --shadow-hover: 0 16px 36px rgba(15,23,42,0.12), 0 2px 6px rgba(15,23,42,0.06);
        --accent: #0f172a;
        --accent-fg: #ffffff;
        --accent-soft: #e2e8f0;
        --muted-bg: #e2e8f0;
        --muted-text: #475569;
        --section-rule: #e2e8f0;
        --focus-ring: #0f172a;
      }}
      :root[data-theme="dark"] {{
        --bg: #050a18;
        --card: #131e36;
        --title: #f8fafc;
        --desc: #cbd5e1;
        --muted: #94a3b8;
        --border: #233152;
        --border-strong: #334155;
        --shadow: 0 4px 12px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.3);
        --shadow-hover: 0 16px 36px rgba(0,0,0,0.65), 0 2px 6px rgba(0,0,0,0.4);
        --accent: #f8fafc;
        --accent-fg: #0b1220;
        --accent-soft: #1e2a44;
        --muted-bg: #1e2a44;
        --muted-text: #94a3b8;
        --section-rule: #233152;
        --focus-ring: #f8fafc;
      }}
      @media (prefers-color-scheme: dark) {{
        :root:not([data-theme]) {{
          --bg: #050a18;
          --card: #131e36;
          --title: #f8fafc;
          --desc: #cbd5e1;
          --muted: #94a3b8;
          --border: #233152;
          --border-strong: #334155;
          --shadow: 0 4px 12px rgba(0,0,0,0.5), 0 1px 3px rgba(0,0,0,0.3);
          --shadow-hover: 0 16px 36px rgba(0,0,0,0.65), 0 2px 6px rgba(0,0,0,0.4);
          --accent: #f8fafc;
          --accent-fg: #0b1220;
          --accent-soft: #1e2a44;
          --muted-bg: #1e2a44;
          --muted-text: #94a3b8;
          --section-rule: #233152;
          --focus-ring: #f8fafc;
        }}
      }}

      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ background: var(--bg); }}
      body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--title);
        min-height: 100vh; padding: 64px 24px 96px;
        line-height: 1.6;
        display: flex; align-items: flex-start; justify-content: center;
      }}
      .container {{
        width: 100%; max-width: 1000px;
        background: transparent;
        padding: 0;
      }}
      .header {{ text-align: center; margin-bottom: 44px; }}
      h1 {{
        font-size: 2.6rem; font-weight: 700;
        color: var(--title);
        margin-bottom: 12px;
      }}
      .subtitle {{
        font-size: 1.05rem; color: var(--muted);
        max-width: 560px; margin: 0 auto; line-height: 1.6;
      }}

      .docs-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 20px;
      }}

      .docs-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 28px 22px 24px;
        text-decoration: none; color: inherit;
        display: block; text-align: center;
        box-shadow: var(--shadow);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
      }}
      .docs-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
        border-color: var(--accent);
      }}
      .card-icon {{
        display: block;
        font-size: 2.6rem;
        margin-bottom: 14px;
        line-height: 1;
      }}
      .card-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--title);
        margin-bottom: 8px;
        line-height: 1.3;
      }}
      .card-desc {{
        color: var(--desc);
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 14px;
      }}
      .card-badge {{
        display: inline-block;
        font-size: 11px; font-weight: 600;
        padding: 4px 11px; border-radius: 999px;
        text-transform: uppercase; letter-spacing: 0.06em;
      }}
      .docs-card.primary .card-badge {{
        background: var(--accent);
        color: var(--accent-fg);
      }}
      .docs-card.secondary .card-badge {{
        background: var(--muted-bg);
        color: var(--muted-text);
      }}

      .handoff-section {{
        margin-top: 56px; padding-top: 36px;
        border-top: 1px solid var(--section-rule);
      }}
      .handoff-section h2 {{
        font-size: 1.4rem; font-weight: 600;
        color: var(--title); text-align: center;
        margin-bottom: 8px;
      }}
      .handoff-section .handoff-subtitle {{
        text-align: center; color: var(--muted);
        max-width: 600px; margin: 0 auto 24px; font-size: 0.95rem;
      }}
      .handoff-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
      }}

      .toolbar {{
        position: fixed; top: 14px; right: 14px;
        display: flex; gap: 4px; align-items: center;
        background: var(--card); border: 1px solid var(--border);
        border-radius: 8px; padding: 4px 6px;
        box-shadow: var(--shadow);
        font-size: 12px; z-index: 10;
      }}
      .toolbar a, .toolbar button {{
        background: transparent; border: 0; cursor: pointer;
        color: var(--muted); text-decoration: none;
        padding: 4px 8px; border-radius: 5px; font: inherit;
      }}
      .toolbar a:hover, .toolbar button:hover {{ color: var(--title); background: var(--accent-soft); }}
      .toolbar a.active {{ color: var(--accent-fg); background: var(--accent); }}
      .toolbar .sep {{ width: 1px; height: 14px; background: var(--border); margin: 0 2px; }}

      .docs-card:focus-visible,
      .toolbar a:focus-visible,
      .toolbar button:focus-visible {{
        outline: 2px solid var(--focus-ring); outline-offset: 2px;
      }}

      @media (max-width: 720px) {{
        body {{ padding: 32px 16px 64px; }}
        h1 {{ font-size: 2.1rem; }}
        .docs-grid, .handoff-grid {{ grid-template-columns: 1fr; }}
        .toolbar {{ top: 8px; right: 8px; }}
        .toolbar > a, .toolbar > .sep {{ display: none; }}
      }}
    </style>
  </head>
  <body>
    {_refined_toolbar()}
    <div class="container">
      <div class="header">
        <h1>API Documentation</h1>
        <p class="subtitle">
          fastapi-agent-blueprint &middot; Pick a viewer or hand off the spec.
        </p>
      </div>
      <div class="docs-grid">
{docs_grid}
      </div>
      <section class="handoff-section">
        <h2>Share with Frontend</h2>
        <p class="handoff-subtitle">
          For workflows that need persisted tokens or environments, hand the
          spec off to a real client (Postman, Bruno, Insomnia, Hoppscotch, or
          Scalar Client) and import it there.
        </p>
        <div class="handoff-grid">
{handoff_grid}
        </div>
      </section>
    </div>
    <script>
      (function() {{
        var KEY = 'docs-selector-theme';
        var root = document.documentElement;
        var btn = document.getElementById('theme-toggle');
        function currentTheme() {{
          return root.getAttribute('data-theme')
            || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        }}
        function paint() {{
          var dark = currentTheme() === 'dark';
          btn.textContent = dark ? 'Light' : 'Dark';
          btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
        }}
        paint();
        btn.addEventListener('click', function() {{
          var next = currentTheme() === 'dark' ? 'light' : 'dark';
          root.setAttribute('data-theme', next);
          try {{ localStorage.setItem(KEY, next); }} catch (e) {{ /* ignore */ }}
          paint();
        }});
      }})();
    </script>
  </body>
</html>"""


def _refined_card(card: dict[str, str]) -> str:
    kind = card.get("kind", "primary")
    klass = "docs-card primary" if kind == "primary" else "docs-card secondary"
    is_external = card.get("external", "false") == "true"
    target = ' target="_blank" rel="noopener"' if is_external else ""
    download = (
        " download"
        if card.get("external") == "false" and card["key"] == "download"
        else ""
    )
    icon = card.get("icon", "")
    return f"""        <a class="{klass}" href="{card["href"]}"{target}{download}>
          <span class="card-icon" aria-hidden="true">{icon}</span>
          <div class="card-title">{card["title"]}</div>
          <p class="card-desc">{card["tagline"]}</p>
          <span class="card-badge">{card["label"]}</span>
        </a>"""


def _refined_toolbar() -> str:
    """Tiny top-right bar that hosts the preview links plus the theme toggle.

    Once a redesign is picked, the preview-link cluster is dropped but the
    theme toggle stays — it is part of the final UX, not the cleanup target.
    """
    items = [
        ("default", "Current"),
        ("brutalist", "Brutalist"),
        ("editorial", "Editorial"),
        ("minimal", "Minimal"),
        ("mac", "Mac"),
        ("refined", "Refined"),
    ]
    links = []
    for key, label in items:
        href = "/docs" if key == "default" else f"/docs?theme={key}"
        is_active = key == "refined"
        klass = "active" if is_active else ""
        aria = ' aria-current="page"' if is_active else ""
        links.append(f'<a href="{href}" class="{klass}"{aria}>{label}</a>')
    return (
        '<nav class="toolbar" aria-label="Theme preview">'
        + "".join(links)
        + '<span class="sep" aria-hidden="true"></span>'
        + '<button id="theme-toggle" type="button"'
        ' aria-label="Toggle light or dark theme" aria-pressed="false">Dark</button>'
        + "</nav>"
    )


# ---------------------------------------------------------------------------
# Spec download + individual UI mounts (unchanged from PR #156).
# ---------------------------------------------------------------------------


@router.get(
    "/openapi-download.json",
    include_in_schema=False,
    description="OpenAPI spec download with attachment Content-Disposition for frontend handoff",
)
def openapi_download(request: Request):
    spec = request.app.openapi()
    return JSONResponse(
        content=spec,
        headers={"Content-Disposition": 'attachment; filename="openapi.json"'},
    )


@router.get(
    "/docs-scalar",
    include_in_schema=False,
    description="Scalar API Reference - Modern, clean API documentation",
)
def scalar_docs(request: Request):
    root_path = request.scope.get("root_path", "")
    spec_url = f"{root_path}{request.app.openapi_url}"
    return HTMLResponse(
        f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Reference - Scalar</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </head>
  <body>
    <div id="api"></div>
    <script>
      Scalar.createApiReference('#api', {{
        url: '{spec_url}',
      }});
    </script>
  </body>
</html>"""
    )


@router.get(
    "/docs-elements",
    include_in_schema=False,
    description="Stoplight Elements - Interactive, visually appealing API documentation",
)
def elements_docs(request: Request):
    root_path = request.scope.get("root_path", "")
    spec_url = f"{root_path}{request.app.openapi_url}"
    return HTMLResponse(
        f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Reference - Elements</title>
    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css" />
  </head>
  <body>
    <elements-api apiDescriptionUrl="{spec_url}" router="hash" />
  </body>
</html>"""
    )


@router.get(
    "/docs-rapidoc",
    include_in_schema=False,
    description="RapiDoc - Fast, lightweight API documentation",
)
def rapidoc_docs(request: Request):
    root_path = request.scope.get("root_path", "")
    spec_url = f"{root_path}{request.app.openapi_url}"
    return HTMLResponse(
        f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Reference - RapiDoc</title>
    <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
  </head>
  <body>
    <rapi-doc spec-url="{spec_url}"
              render-style="read"
              allow-try="true"
              show-method-in-nav-bar="true">
    </rapi-doc>
  </body>
</html>"""
    )
