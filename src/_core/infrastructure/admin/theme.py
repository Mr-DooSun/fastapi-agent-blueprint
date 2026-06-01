"""Centralized theme for the NiceGUI admin dashboard (#193).

Single source of truth for admin colors, layout metrics, and the helper CSS
classes that every admin page consumes. Replaces the hardcoded Quasar/Tailwind
color classes (``bg-blue-800``, ``text-blue-800``, ``bg-blue-50`` …) and inline
grid heights that were previously scattered across the shell and domain pages.

Design (see plan #193 / Codex cross-review):

* **Quasar brand** is overridden via the ``--q-*`` CSS variables, and our own
  **semantic tokens** via ``--admin-*`` variables. Both are declared under
  ``:root`` (light) and ``.body--dark`` (dark), so the whole palette flips with
  Quasar's ``body--dark`` class — no Python re-render, no reload, and no
  per-page ``ui.colors()`` call (which is page-scoped in NiceGUI 3.x).
* The CSS is injected **once, app-wide** via ``ui.add_css(..., shared=True)``
  so it reaches *every* page — including login / setup / error, which never
  call :func:`admin_layout`.
* AG Grid dark theming is **built in** to NiceGUI (a ``body--dark`` observer
  flips ``data-ag-theme-mode`` + ``colorSchemeVariable``), so this module does
  not ship AG Grid dark overrides — only neutral layout helpers.

Constants here are intentionally **import-free** (no ``from nicegui``); the
nicegui import is lazy inside :func:`install_admin_theme_css` so the constants
and :func:`build_admin_css` remain testable when the ``admin`` extra is absent.
"""

from __future__ import annotations

from typing import Final

# Uniform empty / null cell rendering (replaces the bare "" used before).
EMPTY_DISPLAY: Final = "—"


class AdminColors:
    """Brand palette — the single source of truth for admin colors.

    Light/dark concrete values live in the CSS blocks below; these names are
    the canonical references used when wiring Quasar brand variables.
    """

    PRIMARY: Final = "#1d4ed8"  # was bg-blue-800 / text-blue-800
    SECONDARY: Final = "#475569"
    ACCENT: Final = "#0ea5e9"
    POSITIVE: Final = "#16a34a"  # success surfaces (was bg-green-1)
    NEGATIVE: Final = "#dc2626"  # errors (was text-red-700)
    WARNING: Final = "#d97706"
    INFO: Final = "#0284c7"


class AdminVars:
    """Names of the CSS custom properties consumed by the helper classes."""

    # Quasar brand variables (override Quasar's defaults app-wide).
    Q_PRIMARY: Final = "--q-primary"
    Q_SECONDARY: Final = "--q-secondary"
    Q_ACCENT: Final = "--q-accent"
    Q_POSITIVE: Final = "--q-positive"
    Q_NEGATIVE: Final = "--q-negative"
    Q_WARNING: Final = "--q-warning"
    Q_INFO: Final = "--q-info"

    # Semantic admin tokens (our own surfaces).
    HEADER_BG: Final = "--admin-header-bg"
    HEADER_TEXT: Final = "--admin-header-text"
    DRAWER_BG: Final = "--admin-drawer-bg"
    NAV_ACTIVE: Final = "--admin-nav-active"
    SURFACE: Final = "--admin-surface"
    BORDER: Final = "--admin-border"
    TEXT_MUTED: Final = "--admin-text-muted"
    SUCCESS_BG: Final = "--admin-success-bg"
    ROW_ALT: Final = "--admin-row-alt"
    ROW_HOVER: Final = "--admin-row-hover"
    GRID_HEIGHT: Final = "--admin-grid-height"
    GRID_HEIGHT_COMPACT: Final = "--admin-grid-height-compact"
    LABEL_COL_WIDTH: Final = "--admin-label-col-width"


class AdminMetrics:
    """Layout metrics (numbers, not colors)."""

    GRID_ROW_HEIGHT: Final = 44
    GRID_MIN_COL_WIDTH: Final = 120


class AdminClasses:
    """Helper CSS class names (all ``admin-`` prefixed for the AST guard).

    Pages reference these instead of hardcoded ``bg-*`` / ``text-*`` colors.
    """

    HEADER: Final = "admin-header"
    DRAWER: Final = "admin-drawer"
    NAV_ACTIVE: Final = "admin-nav-active"
    ACCENT_ICON: Final = "admin-accent-icon"
    CARD: Final = "admin-card"
    FIELD_LABEL: Final = "admin-field-label"
    FIELD_VALUE: Final = "admin-field-value"
    # Muted/caption text — flips with dark mode (unlike fixed Quasar greys).
    MUTED: Final = "admin-text-muted"
    EMPTY_VALUE: Final = "admin-empty-value"
    SUCCESS_SURFACE: Final = "admin-success-surface"
    GRID: Final = "admin-grid"
    GRID_COMPACT: Final = "admin-grid-compact"
    PAGINATION: Final = "admin-pagination"
    EMPTY_STATE: Final = "admin-empty-state"
    PRE: Final = "admin-pre"
    HIDDEN: Final = "admin-hidden"


def build_admin_css() -> str:
    """Return the single CSS payload injected app-wide for the admin theme.

    Pure string builder (no nicegui import) so it is unit-testable without the
    ``admin`` extra. Defines ``:root`` (light) + ``.body--dark`` (dark) blocks
    for every Quasar brand and ``--admin-*`` token, then the helper classes that
    consume them.
    """
    return f"""
/* === Admin theme (#193) — light defaults === */
:root {{
  {AdminVars.Q_PRIMARY}: {AdminColors.PRIMARY};
  {AdminVars.Q_SECONDARY}: {AdminColors.SECONDARY};
  {AdminVars.Q_ACCENT}: {AdminColors.ACCENT};
  {AdminVars.Q_POSITIVE}: {AdminColors.POSITIVE};
  {AdminVars.Q_NEGATIVE}: {AdminColors.NEGATIVE};
  {AdminVars.Q_WARNING}: {AdminColors.WARNING};
  {AdminVars.Q_INFO}: {AdminColors.INFO};

  {AdminVars.HEADER_BG}: {AdminColors.PRIMARY};
  {AdminVars.HEADER_TEXT}: #ffffff;
  {AdminVars.DRAWER_BG}: #eff6ff;
  {AdminVars.NAV_ACTIVE}: #1e40af;
  {AdminVars.SURFACE}: #ffffff;
  {AdminVars.BORDER}: #e2e8f0;
  {AdminVars.TEXT_MUTED}: #64748b;
  {AdminVars.SUCCESS_BG}: #f0fdf4;
  {AdminVars.ROW_ALT}: #f8fafc;
  {AdminVars.ROW_HOVER}: #eef2ff;
  {AdminVars.GRID_HEIGHT}: calc(100vh - 240px);
  {AdminVars.GRID_HEIGHT_COMPACT}: calc(100vh - 360px);
  {AdminVars.LABEL_COL_WIDTH}: 160px;
}}

/* === Admin theme (#193) — dark overrides (Quasar body--dark) === */
.body--dark {{
  {AdminVars.HEADER_BG}: #1e293b;
  {AdminVars.HEADER_TEXT}: #f1f5f9;
  {AdminVars.DRAWER_BG}: #0f172a;
  {AdminVars.NAV_ACTIVE}: #60a5fa;
  {AdminVars.SURFACE}: #1e293b;
  {AdminVars.BORDER}: #334155;
  {AdminVars.TEXT_MUTED}: #94a3b8;
  {AdminVars.SUCCESS_BG}: #052e16;
  {AdminVars.ROW_ALT}: #0f172a;
  {AdminVars.ROW_HOVER}: #1e293b;
}}

/* === Helper classes consuming the tokens === */
.{AdminClasses.HEADER} {{
  background-color: var({AdminVars.HEADER_BG}) !important;
  color: var({AdminVars.HEADER_TEXT}) !important;
}}
.{AdminClasses.DRAWER} {{
  background-color: var({AdminVars.DRAWER_BG}) !important;
}}
.{AdminClasses.NAV_ACTIVE} {{
  color: var({AdminVars.NAV_ACTIVE}) !important;
  font-weight: 700;
}}
.{AdminClasses.ACCENT_ICON} {{
  color: var({AdminVars.NAV_ACTIVE}) !important;
}}
.{AdminClasses.FIELD_LABEL} {{
  width: var({AdminVars.LABEL_COL_WIDTH});
  font-weight: 700;
}}
.{AdminClasses.MUTED},
.{AdminClasses.EMPTY_VALUE} {{
  color: var({AdminVars.TEXT_MUTED});
}}
.{AdminClasses.SUCCESS_SURFACE} {{
  background-color: var({AdminVars.SUCCESS_BG}) !important;
}}
.{AdminClasses.GRID} {{
  width: 100%;
  height: var({AdminVars.GRID_HEIGHT});
}}
.{AdminClasses.GRID_COMPACT} {{
  width: 100%;
  height: var({AdminVars.GRID_HEIGHT_COMPACT});
}}
/* AG Grid (NiceGUI 3.x quartz theme) reads these CSS custom properties from
   the new theming API — set them on the grid element rather than overriding
   the legacy .ag-row-odd class (which the quartz theme no longer emits). */
.{AdminClasses.GRID},
.{AdminClasses.GRID_COMPACT} {{
  --ag-odd-row-background-color: var({AdminVars.ROW_ALT});
  --ag-row-hover-color: var({AdminVars.ROW_HOVER});
}}
.{AdminClasses.PAGINATION} {{
  justify-content: flex-end;
}}
.{AdminClasses.EMPTY_STATE} {{
  color: var({AdminVars.TEXT_MUTED});
  align-items: center;
  text-align: center;
  padding: 48px 0;
}}
.{AdminClasses.PRE} {{
  white-space: pre-wrap;
}}
.{AdminClasses.HIDDEN} {{
  display: none;
}}
"""


_theme_css_installed = False


def install_admin_theme_css() -> None:
    """Inject the admin theme CSS app-wide (once per process).

    Calls ``ui.add_css(..., shared=True)`` so the stylesheet lands in every
    page's ``<head>`` — including login / setup / error which never render
    :func:`admin_layout`. Guarded so repeated ``bootstrap_admin()`` calls (test
    reloads) do not double-inject, mirroring the exception-handler guard in
    ``bootstrap.py``.
    """
    global _theme_css_installed
    if _theme_css_installed:
        return
    from nicegui import ui

    ui.add_css(build_admin_css(), shared=True)
    _theme_css_installed = True
