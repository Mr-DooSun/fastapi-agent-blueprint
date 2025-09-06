# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get(
    "/docs",
    include_in_schema=False,
    description="API 문서 선택기 - 다양한 문서 UI 중 선택할 수 있는 메인 페이지",
)
def docs_selector():
    return HTMLResponse(
        """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>API Documentation Selector</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .container {
        max-width: 1000px;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 60px 40px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
      }

      .header {
        text-align: center;
        margin-bottom: 50px;
      }

      h1 {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 16px;
        letter-spacing: -0.02em;
      }

      .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
      }

      .docs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
        margin-top: 40px;
      }

      .docs-card {
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
      }

      .docs-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
      }

      .docs-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: #667eea;
      }

      .docs-card:hover::before {
        transform: scaleX(1);
      }

      .card-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        display: block;
        text-align: center;
      }

      .docs-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #1e293b;
        text-align: center;
        line-height: 1.3;
      }

      .docs-desc {
        color: #64748b;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.6;
        text-align: center;
      }

      .badge {
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
      }

      @media (max-width: 768px) {
        .container {
          padding: 40px 24px;
          margin: 10px;
        }

        h1 {
          font-size: 2.5rem;
        }

        .subtitle {
          font-size: 1.1rem;
        }

        .docs-grid {
          grid-template-columns: 1fr;
          gap: 16px;
        }

        .docs-card {
          padding: 24px 20px;
        }
      }

      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(30px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .docs-card {
        animation: fadeInUp 0.6s ease forwards;
      }

      .docs-card:nth-child(1) { animation-delay: 0.1s; }
      .docs-card:nth-child(2) { animation-delay: 0.2s; }
      .docs-card:nth-child(3) { animation-delay: 0.3s; }
      .docs-card:nth-child(4) { animation-delay: 0.4s; }
      .docs-card:nth-child(5) { animation-delay: 0.5s; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>🚀 API Documentation</h1>
        <p class="subtitle">
          다양한 스타일의 API 문서 중에서 원하는 형태를 선택하세요.<br>
          각각의 독특한 장점과 사용자 경험을 제공합니다.
        </p>
      </div>

      <div class="docs-grid">
        <a href="/api/docs-swagger" class="docs-card">
          <span class="card-icon">📚</span>
          <div class="docs-title">FastAPI Swagger UI</div>
          <p class="docs-desc">
            가장 널리 사용되는 API 문서 형태로, 직관적인 인터페이스와
            완전한 기능을 제공합니다.
          </p>
          <span class="badge">추천</span>
        </a>

        <a href="/api/docs-redoc" class="docs-card">
          <span class="card-icon">📖</span>
          <div class="docs-title">ReDoc</div>
          <p class="docs-desc">
            깔끔하고 읽기 좋은 문서 중심의 디자인으로,
            API 명세를 체계적으로 탐색할 수 있습니다.
          </p>
          <span class="badge">깔끔함</span>
        </a>

        <a href="/api/docs-scalar" class="docs-card">
          <span class="card-icon">✨</span>
          <div class="docs-title">Scalar API Reference</div>
          <p class="docs-desc">
            모던하고 세련된 디자인의 API 문서로,
            개발자 친화적인 기능들을 제공합니다.
          </p>
          <span class="badge">모던</span>
        </a>

        <a href="/api/docs-elements" class="docs-card">
          <span class="card-icon">🎨</span>
          <div class="docs-title">Stoplight Elements</div>
          <p class="docs-desc">
            인터랙티브하고 시각적으로 아름다운 API 문서로,
            풍부한 사용자 경험을 제공합니다.
          </p>
          <span class="badge">인터랙티브</span>
        </a>

        <a href="/api/docs-rapidoc" class="docs-card">
          <span class="card-icon">⚡</span>
          <div class="docs-title">RapiDoc</div>
          <p class="docs-desc">
            빠르고 가벼운 API 문서로,
            심플하면서도 효율적인 인터페이스를 제공합니다.
          </p>
          <span class="badge">빠름</span>
        </a>
      </div>
    </div>
  </body>
</html>"""
    )


@router.get(
    "/docs-scalar",
    include_in_schema=False,
    description="Scalar API Reference - 모던하고 깔끔한 디자인의 API 문서",
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
        // proxyUrl: 'https://proxy.scalar.com' // CORS 회피용(선택)
      }});
    </script>
  </body>
</html>"""
    )


@router.get(
    "/docs-elements",
    include_in_schema=False,
    description="Stoplight Elements - 인터랙티브하고 시각적으로 아름다운 API 문서",
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
    "/docs-rapidoc", include_in_schema=False, description="RapiDoc - 빠르고 가벼운 API 문서"
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
