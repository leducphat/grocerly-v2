"""Every static file a page asks for exists. Traces to L-63 in docs/ISSUES.md.

A missing file does not break the page, so no other test notices it; on the host
it shows up only as a 404 in the log at every page view. These checks read the
templates and stylesheets, no server needed.
"""

import re
from pathlib import Path

import pytest
from django.conf import settings

STATIC = Path(settings.BASE_DIR) / "static"
TEMPLATES = Path(settings.BASE_DIR) / "templates"

STATIC_TAG = re.compile(r"""\{%\s*static\s+['"]([^'"]+)['"]\s*%\}""")
RELATIVE_ASSET = re.compile(r"""(?:src|href)=["']((?:assets|assets2)/[^"']+)["']""")
CSS_URL = re.compile(r"""url\(\s*['"]?([^'")]+?)['"]?\s*\)""")


def templates():
    return sorted(TEMPLATES.rglob("*.html"))


@pytest.mark.xfail(reason="L-63: three {% static %} references point at no file")
def test_every_static_tag_names_an_existing_file():
    """`{% static 'x.js?v=1.1' %}` turns "?" into "%3F", so the query string becomes
    part of the file name; a sample image the theme never shipped 404s the same way."""
    missing = [
        f"{template.relative_to(TEMPLATES)}: {ref}"
        for template in templates()
        for ref in STATIC_TAG.findall(template.read_text(encoding="utf-8"))
        if not (STATIC / ref.removeprefix("./")).is_file()
    ]

    assert missing == []


@pytest.mark.xfail(reason="L-63: the staff favicon is loaded by a relative path")
def test_templates_load_no_asset_by_relative_path():
    """A relative path is joined to the page URL: on /vi/useradmin/orders/ the
    browser asks for /vi/useradmin/orders/assets2/..., which is no file."""
    relative = [
        f"{template.relative_to(TEMPLATES)}: {ref}"
        for template in templates()
        for ref in RELATIVE_ASSET.findall(template.read_text(encoding="utf-8"))
    ]

    assert relative == []


@pytest.mark.xfail(reason="L-63: the theme's main.css names images that are not in static")
def test_every_file_named_in_the_theme_stylesheets_exists():
    """The theme's own stylesheets only; the fallback font formats of vendor
    libraries are left out."""
    missing = []
    for css in sorted(STATIC.rglob("*.css")):
        if "vendors" in css.parts:
            continue
        for ref in CSS_URL.findall(css.read_text(encoding="utf-8", errors="ignore")):
            if ref.startswith(("data:", "http", "//", "#")):
                continue
            if not (css.parent / ref.split("?")[0].split("#")[0]).is_file():
                missing.append(f"{css.relative_to(STATIC)}: {ref}")

    assert missing == []
