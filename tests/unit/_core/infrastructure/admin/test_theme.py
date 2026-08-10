"""Pure-constant tests for the admin theme module (#193).

These intentionally import nothing from nicegui — ``theme.py`` keeps its nicegui
import lazy inside ``install_admin_theme_css`` — so they run under
``make check-core`` even when the ``admin`` extra is not installed.

The admin shell uses a single neutral-mono theme (no preset selection) — a
desaturated zinc ramp with one blue accent, restyled from the previous
Toss-style look in #365.
"""

from __future__ import annotations

from src._core.infrastructure.admin.theme import (
    EMPTY_DISPLAY,
    AdminClasses,
    AdminColors,
    AdminMetrics,
    AdminVars,
    build_admin_css,
)


def _public_values(cls: type) -> list:
    return [v for k, v in vars(cls).items() if not k.startswith("_")]


def test_empty_display_is_em_dash():
    assert EMPTY_DISPLAY == "—"


def test_brand_colors_are_hex():
    values = _public_values(AdminColors)
    assert values, "AdminColors must define at least one color"
    assert all(isinstance(v, str) and v.startswith("#") for v in values)


def test_primary_is_the_single_blue_accent():
    """Single-theme brand primary (also the chart bar fill) is Tailwind blue-600.

    The neutral-mono look spends colour in exactly one place, so this value is
    the whole accent story — a fork rebrands by changing it (#365).
    """
    assert AdminColors.PRIMARY == "#2563eb"
    assert AdminColors.ACCENT == AdminColors.PRIMARY
    # INFO deliberately collapses onto the accent rather than sitting one hue
    # step away, where it read as an inconsistency instead of a semantic.
    assert AdminColors.INFO == AdminColors.PRIMARY


def test_palette_is_on_a_single_ramp():
    """Every AdminColors value is a Tailwind step (#365).

    This is the regression this test exists for: the pre-#365 palette mixed a
    Toss ramp (primary/positive/negative) with a Tailwind slate ramp
    (secondary/warning/info/chart), and two ramps with different hue and
    saturation curves cannot be reconciled by nudging individual tokens. Adding
    an off-ramp colour must fail here rather than quietly look wrong.
    """
    tailwind_steps = {
        "#2563eb",  # blue-600
        "#16a34a",  # green-600
        "#dc2626",  # red-600
        "#d97706",  # amber-600
        "#71717a",  # zinc-500
        "#a1a1aa",  # zinc-400
        "#a1a1aa33",  # zinc-400 @ ~0.2 alpha
    }
    off_ramp = set(_public_values(AdminColors)) - tailwind_steps
    assert not off_ramp, f"colours outside the Tailwind ramp: {sorted(off_ramp)}"


def test_css_var_names_are_custom_properties():
    values = _public_values(AdminVars)
    assert values
    assert all(isinstance(v, str) and v.startswith("--") for v in values)


def test_helper_class_names_are_admin_prefixed():
    values = _public_values(AdminClasses)
    assert values
    assert all(isinstance(v, str) and v.startswith("admin-") for v in values)


def test_metrics_are_numeric():
    values = _public_values(AdminMetrics)
    assert values
    assert all(isinstance(v, int) for v in values)


def test_brand_palette_is_emitted_on_body_with_important():
    """The `--q-*` group must outrank NiceGUI's inline body style (#365).

    NiceGUI writes its own brand palette as an inline style on ``<body>``
    (``--q-primary: #5898d4``, teal secondary, purple accent, cyan info). An
    inline declaration beats every stylesheet rule regardless of specificity, so
    declaring these on ``:root`` — which this module did from #193 until #365 —
    left the entire brand half of the palette inert: buttons, badges and
    ``text-primary`` all rendered NiceGUI's defaults next to our greys.

    `!important` in a stylesheet *does* outrank a normal inline declaration, so
    this asserts both halves of that contract: the selector is ``body`` and the
    declarations carry `!important`.
    """
    css = build_admin_css()
    brand_block = css[css.index("body {") : css.index(":root {")]
    for var in (
        AdminVars.Q_PRIMARY,
        AdminVars.Q_SECONDARY,
        AdminVars.Q_ACCENT,
        AdminVars.Q_POSITIVE,
        AdminVars.Q_NEGATIVE,
        AdminVars.Q_WARNING,
        AdminVars.Q_INFO,
    ):
        assert f"{var}: " in brand_block, f"{var} not emitted under body"
        line = next(ln for ln in brand_block.splitlines() if ln.strip().startswith(var))
        assert "!important" in line, f"{var} would lose to the inline body style"
    # A --q-* declaration in :root is the inert form — it must not come back.
    root_block = css[css.index(":root {") : css.index(".body--dark")]
    assert AdminVars.Q_PRIMARY not in root_block


def test_quasar_dark_surfaces_align_with_the_zinc_ladder():
    """Quasar's own dark menus/dialogs come from --q-dark, not --admin-* (#365)."""
    css = build_admin_css()
    brand_block = css[css.index("body {") : css.index(":root {")]
    assert f"{AdminVars.Q_DARK}: #18181b" in brand_block  # == SURFACE dark
    assert f"{AdminVars.Q_DARK_PAGE}: #09090b" in brand_block  # == BG dark


def test_css_defines_light_and_dark_blocks():
    css = build_admin_css()
    assert ":root {" in css
    assert ".body--dark {" in css


def test_css_defines_every_token_in_both_themes():
    """Brand/shape live in :root; content + chrome surfaces flip into dark."""
    css = build_admin_css()
    root_block = css.split(".body--dark")[0]
    dark_block = css[css.index(".body--dark") :]

    # Brand + shape are mode-constant, so they appear only in the pre-dark
    # portion of the payload. (Brand lives under `body`, not `:root` — see
    # test_brand_palette_is_emitted_on_body_with_important.)
    for var in (AdminVars.Q_PRIMARY, AdminVars.Q_NEGATIVE, AdminVars.RADIUS):
        assert var in root_block, f"{var} missing from the light/constant block"

    # Content + chrome surfaces are defined in BOTH blocks so they flip.
    for var in (
        AdminVars.SURFACE,
        AdminVars.BORDER,
        AdminVars.TEXT_MUTED,
        AdminVars.ROW_ALT,
        AdminVars.HEADER_BG,
        AdminVars.DRAWER_TEXT,
        AdminVars.CHROME_BORDER,
    ):
        assert var in root_block, f"{var} missing from :root"
        assert var in dark_block, f"{var} missing from .body--dark"


def test_chrome_flips_light_to_dark():
    """Chrome is white in light mode and zinc-950 in dark mode (not constant)."""
    css = build_admin_css()
    root_block = css.split(".body--dark")[0]
    dark_block = css[css.index(".body--dark") :]
    assert f"{AdminVars.HEADER_BG}: #ffffff" in root_block  # light = white sidebar
    assert f"{AdminVars.HEADER_BG}: #09090b" in dark_block  # dark = zinc-950


def test_dark_chrome_matches_page_and_card_is_the_raised_surface():
    """Dark mode separates chrome by border, not by an extra elevation step.

    The ladder is page = chrome < card. If chrome ever drifts off the page
    colour, the sidebar grows a seam the border already draws (#365).
    """
    css = build_admin_css()
    dark_block = css[css.index(".body--dark") :]
    assert f"{AdminVars.BG}: #09090b" in dark_block
    assert f"{AdminVars.DRAWER_BG}: #09090b" in dark_block
    assert f"{AdminVars.SURFACE}: #18181b" in dark_block


def test_zebra_striping_is_off_and_rows_separate_by_border():
    """Striping is pinned to the surface colour, not deleted (#365).

    Deleting the override would let the AG Grid quartz default odd-row tint
    leak back in. `--ag-row-border` is the v33 Theming API name; the legacy
    `--ag-row-border-color/style/width` trio no longer applies.
    """
    css = build_admin_css()
    root_block = css.split(".body--dark")[0]
    dark_block = css[css.index(".body--dark") :]
    # ROW_ALT == SURFACE in both modes → no visible banding.
    assert f"{AdminVars.ROW_ALT}: #ffffff" in root_block
    assert f"{AdminVars.SURFACE}: #ffffff" in root_block
    assert f"{AdminVars.ROW_ALT}: #18181b" in dark_block
    assert "--ag-odd-row-background-color: var(--admin-row-alt)" in css
    assert "--ag-row-border: 1px solid var(--admin-border)" in css


def test_grid_surface_comes_from_the_same_token_as_every_other_panel():
    """The grid body must not keep the quartz palette's own surface (#365).

    Regression guard for a defect caught by the dark-mode screenshot pass: with
    only the odd-row override set, the grid rendered on quartz's surface while
    cards used ``--admin-surface``, so the grid floated as a lighter slab *and*
    the odd-row pin made striping reappear inverted (odd rows darker than the
    quartz base). Pinning the odd row without pinning the background is the
    broken half-state — assert both are present together.
    """
    css = build_admin_css()
    assert "--ag-background-color: var(--admin-surface)" in css
    assert "--ag-header-background-color: var(--admin-bg)" in css
    assert "--ag-border-color: var(--admin-border)" in css


def test_no_lift_on_hover():
    """State changes are colour/border only — nothing moves (#365).

    The pre-#365 look lifted clickable cards (`translateY(-2px)` plus a large
    shadow) and squished buttons on press (`scale(0.985)`). Assert on the
    movement primitives rather than the word "transform", which legitimately
    appears in `text-transform: uppercase` on the nav section labels.
    """
    css = build_admin_css()
    for primitive in ("translateY", "translateX", "scale("):
        assert primitive not in css, f"movement reintroduced: {primitive}"


def test_css_defines_helper_class_selectors():
    css = build_admin_css()
    for cls in (
        AdminClasses.HEADER,
        AdminClasses.DRAWER,
        AdminClasses.NAV_ACTIVE,
        AdminClasses.ACCENT_ICON,
        AdminClasses.FIELD_LABEL,
        AdminClasses.MUTED,
        AdminClasses.SUCCESS_SURFACE,
        AdminClasses.GRID,
        AdminClasses.GRID_COMPACT,
        AdminClasses.PAGINATION,
        AdminClasses.EMPTY_STATE,
        AdminClasses.PRE,
        AdminClasses.HIDDEN,
    ):
        assert f".{cls}" in css, f"selector .{cls} missing from CSS"


def test_css_styles_alternating_grid_rows_via_theming_vars():
    """NiceGUI 3.x quartz theme reads --ag-* custom properties, not .ag-row-odd."""
    css = build_admin_css()
    assert "--ag-odd-row-background-color" in css
    assert "--ag-row-hover-color" in css


def test_css_forces_grid_cells_visible():
    """AG Grid v33 can leave rows stuck `visibility:hidden` via `ag-delay-render`;
    the theme forces admin grid cells visible (#234)."""
    css = build_admin_css()
    assert ".admin-grid .ag-cell" in css
    assert "visibility: visible" in css


def test_css_defines_style_tokens_and_component_overrides():
    """The theme drives shape/elevation tokens + Quasar component overrides."""
    css = build_admin_css()
    for var in (
        AdminVars.RADIUS,
        AdminVars.RADIUS_BUTTON,
        AdminVars.SHADOW,
        AdminVars.CARD_BORDER,
        AdminVars.BG,
    ):
        assert var in css, f"{var} missing from CSS"
    # Quasar components are restyled globally so every page inherits the look.
    assert ".q-card" in css
    assert ".admin-header .q-btn" in css  # header text is token-driven, not white


def test_font_is_a_system_stack_with_no_webfont():
    """No bundled or remote webfont — the stack resolves against OS fonts (#365).

    #193 shipped a self-hosted Wanted Sans (1.29 MB woff2) served from
    /admin-static; #365 dropped both the asset and that mount. Any `@font-face`
    or absolute font URL reappearing here means a font dependency came back —
    either a CDN (a third-party request from an admin panel) or a repo asset
    plus the static route needed to serve it.
    """
    css = build_admin_css()
    assert "@font-face" not in css
    assert "Wanted Sans" not in css
    assert "/admin-static" not in css
    assert "url(" not in css  # no font (or image) fetched from anywhere
    assert "cdn.jsdelivr.net" not in css
    assert "fonts.googleapis.com" not in css
    # The stack itself: a Latin UI font first, then a Hangul fallback for
    # platforms whose UI font has no Hangul coverage (Segoe UI does not).
    assert f"{AdminVars.FONT}: -apple-system" in css
    assert "Malgun Gothic" in css


def test_login_backdrop_is_flat_not_a_gradient():
    """The login backdrop is a flat surface colour (#365).

    Renamed from `--admin-login-gradient`; a gradient value reappearing under
    the new name would make the token name lie again.
    """
    css = build_admin_css()
    assert AdminVars.LOGIN_BG == "--admin-login-bg"
    assert "linear-gradient" not in css
    assert "--admin-login-gradient" not in css
