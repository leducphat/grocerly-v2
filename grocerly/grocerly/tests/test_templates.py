"""Every template closes the <div> tags it opens. Traces to L-65 in docs/ISSUES.md.

The browser repairs a missing </div> without an error, so the page still loads;
the block after it just ends up inside the wrong parent. On the product list the
"Deals Of The Day" section landed inside the product grid, and the page grew 12 px
wider than the screen. Counting tags in the source finds this without a browser.
"""

import re
from pathlib import Path

from django.conf import settings

TEMPLATES = Path(settings.BASE_DIR) / "templates"

# Commented-out markup is not sent to the browser, so it does not count.
DJANGO_COMMENT = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def div_balance(source):
    source = HTML_COMMENT.sub("", DJANGO_COMMENT.sub("", source))
    return len(re.findall(r"<div\b", source)) - len(re.findall(r"</div>", source))


def test_div_balance_ignores_commented_out_markup():
    source = "<div></div>{% comment %}<div>{% endcomment %}<!-- <div> -->"

    assert div_balance(source) == 0


def test_every_template_closes_the_divs_it_opens():
    unbalanced = [
        f"{template.relative_to(TEMPLATES)}: {div_balance(template.read_text(encoding='utf-8')):+d}"
        for template in sorted(TEMPLATES.rglob("*.html"))
        if div_balance(template.read_text(encoding="utf-8")) != 0
    ]

    assert unbalanced == []
