"""Pure-constant tests for the admin theme module (#193).

These intentionally import nothing from nicegui — ``theme.py`` keeps its nicegui
import lazy inside ``install_admin_theme_css`` — so they run under
``make check-core`` even when the ``admin`` extra is not installed.
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


def test_css_defines_light_and_dark_blocks():
    css = build_admin_css()
    assert ":root {" in css
    assert ".body--dark {" in css


def test_css_defines_every_token_in_both_themes():
    """Each Quasar brand + semantic var must be set, and every dark-flippable
    token must also appear in the .body--dark block."""
    css = build_admin_css()
    root_block = css.split(".body--dark")[0]
    dark_block = css[css.index(".body--dark") :]

    # Quasar brand vars live in :root (brand is theme-independent here).
    for var in (
        AdminVars.Q_PRIMARY,
        AdminVars.Q_NEGATIVE,
        AdminVars.Q_POSITIVE,
    ):
        assert var in root_block

    # Semantic surfaces must be defined in BOTH light and dark so they flip.
    for var in (
        AdminVars.HEADER_BG,
        AdminVars.DRAWER_BG,
        AdminVars.NAV_ACTIVE,
        AdminVars.SURFACE,
        AdminVars.TEXT_MUTED,
        AdminVars.SUCCESS_BG,
        AdminVars.ROW_ALT,
    ):
        assert var in root_block, f"{var} missing from :root"
        assert var in dark_block, f"{var} missing from .body--dark"


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
