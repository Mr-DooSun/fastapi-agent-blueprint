from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()

HANDOFF_GUIDE_URL = (
    "https://github.com/Mr-DooSun/fastapi-agent-blueprint"
    "/blob/main/docs/frontend-handoff.md"
)


@router.get(
    "/docs",
    include_in_schema=False,
    description="API Docs Selector - Main page for choosing among various documentation UIs",
)
def docs_selector(request: Request):
    root_path = request.scope.get("root_path", "")
    download_url = f"{root_path}/openapi-download.json"

    return HTMLResponse(
        f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Documentation Selector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}

      body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
      }}

      .container {{
        max-width: 1000px;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 60px 40px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
      }}

      .header {{
        text-align: center;
        margin-bottom: 50px;
      }}

      h1 {{
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 16px;
        letter-spacing: -0.02em;
      }}

      .subtitle {{
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
      }}

      .docs-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
        margin-top: 40px;
      }}

      .docs-card {{
        background: white;
        border-radius: 16px;
        padding: 32px 24px;
        text-decoration: none;
        color: inherit;
        display: block;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
      }}

      .docs-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
      }}

      .docs-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
      }}

      .docs-card:hover::before {{
        transform: scaleX(1);
      }}

      .card-icon {{
        font-size: 3rem;
        margin-bottom: 16px;
        display: block;
        text-align: center;
      }}

      .docs-title {{
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #1e293b;
        text-align: center;
        line-height: 1.3;
      }}

      .docs-desc {{
        color: #64748b;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.6;
        text-align: center;
      }}

      .badge {{
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 16px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }}

      .badge.muted {{
        background: #e2e8f0;
        color: #475569;
      }}

      .handoff-section {{
        margin-top: 56px;
        padding-top: 40px;
        border-top: 1px solid #e2e8f0;
      }}

      .handoff-section h2 {{
        font-size: 1.6rem;
        font-weight: 600;
        color: #1e293b;
        text-align: center;
        margin-bottom: 8px;
      }}

      .handoff-section p.handoff-subtitle {{
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        max-width: 640px;
        margin: 0 auto 28px;
        line-height: 1.6;
      }}

      .handoff-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
      }}

      @media (max-width: 768px) {{
        .container {{
          padding: 40px 24px;
          margin: 10px;
        }}

        h1 {{
          font-size: 2.5rem;
        }}

        .subtitle {{
          font-size: 1.1rem;
        }}

        .docs-grid {{
          grid-template-columns: 1fr;
          gap: 16px;
        }}

        .docs-card {{
          padding: 24px 20px;
        }}

        .handoff-grid {{
          grid-template-columns: 1fr;
        }}
      }}

      @keyframes fadeInUp {{
        from {{
          opacity: 0;
          transform: translateY(30px);
        }}
        to {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}

      .docs-card {{
        animation: fadeInUp 0.6s ease forwards;
      }}

      .docs-card:nth-child(1) {{ animation-delay: 0.1s; }}
      .docs-card:nth-child(2) {{ animation-delay: 0.2s; }}
      .docs-card:nth-child(3) {{ animation-delay: 0.3s; }}
      .docs-card:nth-child(4) {{ animation-delay: 0.4s; }}
      .docs-card:nth-child(5) {{ animation-delay: 0.5s; }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🚀 API Documentation</h1>
        <p class="subtitle">
          Choose your preferred style of API documentation below.<br>
          Each one offers a unique set of features and user experience.
        </p>
      </div>

      <div class="docs-grid">
        <a href="/api/docs-elements" class="docs-card">
          <span class="card-icon">🎨</span>
          <div class="docs-title">Stoplight Elements</div>
          <p class="docs-desc">
            An interactive, visually appealing API documentation that
            delivers a rich user experience.
          </p>
          <span class="badge">Recommended — Visual</span>
        </a>

        <a href="/api/docs-scalar" class="docs-card">
          <span class="card-icon">✨</span>
          <div class="docs-title">Scalar API Reference</div>
          <p class="docs-desc">
            A modern, sophisticated API documentation with built-in
            try-it experience that bridges into a full client.
          </p>
          <span class="badge">Recommended — Try-it</span>
        </a>

        <a href="/api/docs-swagger" class="docs-card">
          <span class="card-icon">📚</span>
          <div class="docs-title">FastAPI Swagger UI</div>
          <p class="docs-desc">
            The most widely used API documentation format, offering an
            intuitive interface with full-featured functionality.
          </p>
          <span class="badge muted">Compatibility</span>
        </a>

        <a href="/api/docs-redoc" class="docs-card">
          <span class="card-icon">📖</span>
          <div class="docs-title">ReDoc</div>
          <p class="docs-desc">
            A clean, readable, documentation-focused design that lets
            you explore API specifications in a well-organized manner.
          </p>
          <span class="badge muted">Clean</span>
        </a>

        <a href="/api/docs-rapidoc" class="docs-card">
          <span class="card-icon">⚡</span>
          <div class="docs-title">RapiDoc</div>
          <p class="docs-desc">
            A fast, lightweight API documentation that provides
            a simple yet efficient interface.
          </p>
          <span class="badge muted">Fast</span>
        </a>
      </div>

      <section class="handoff-section">
        <h2>📦 Share with Frontend</h2>
        <p class="handoff-subtitle">
          For testing flows where inputs, tokens, or environments need to persist
          (Postman / Bruno / Insomnia / Hoppscotch / Scalar Client), hand off the
          OpenAPI spec and let the frontend import it into their tool of choice.
        </p>
        <div class="handoff-grid">
          <a href="{download_url}" class="docs-card" download>
            <span class="card-icon">⬇️</span>
            <div class="docs-title">Download OpenAPI (JSON)</div>
            <p class="docs-desc">
              Save the live spec as <code>openapi.json</code> and import it into
              Postman, Bruno, or any OpenAPI-aware client.
            </p>
            <span class="badge">Spec</span>
          </a>

          <a href="{HANDOFF_GUIDE_URL}" class="docs-card" target="_blank" rel="noopener">
            <span class="card-icon">🧭</span>
            <div class="docs-title">Frontend Handoff Guide</div>
            <p class="docs-desc">
              Contract scope (auth, errors, pagination, CORS), test client
              comparison, and TypeScript SDK generation recipes.
            </p>
            <span class="badge">Guide</span>
          </a>
        </div>
      </section>
    </div>
  </body>
</html>"""
    )


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
        // proxyUrl: 'https://proxy.scalar.com' // Optional CORS bypass
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
