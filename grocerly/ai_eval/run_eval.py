"""
Measure how often the AI assistant proposes the right product and quantity (P-42 d, D-062).

Run from grocerly/:
    python ai_eval/run_eval.py               # every case in cases.py
    python ai_eval/run_eval.py --only A1,F2  # just these cases

Every case is sent to /api/v1/chat/ exactly as the chat window sends it, and the
real Gemini answers. What is compared with the expected answer is the data the
server returns (`action`, `pid`, `qty`, SRS AC-17.5), not the wording of the reply.

Because it calls the real Gemini, this is not a test: pytest does not collect it
and CI does not run it. The database is the in-memory SQLite of settings_test,
filled with the catalog of cases.py, never the database named in .env (D-002).
The Gemini key comes from the GEMINI_API_KEY environment variable, or else from
that one line of grocerly/.env.
"""

import argparse
import json
import os
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values

from cases import CASES, CATALOG, GROUPS

GROCERLY_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"

# What the models answering one customer message were, filled by RecordingChat.
answered_by = []
gemini_failed = []


def gemini_key():
    """Read the key before Django starts: settings_test blanks GEMINI_API_KEY."""
    return os.environ.get("GEMINI_API_KEY") or dotenv_values(GROCERLY_DIR / ".env").get("GEMINI_API_KEY", "")


def start_django(key):
    sys.path.insert(0, str(GROCERLY_DIR))
    # Set, not setdefault: a DJANGO_SETTINGS_MODULE left in the shell must not
    # point this script at a real database.
    os.environ["DJANGO_SETTINGS_MODULE"] = "grocerly.settings_test"
    # WhiteNoise warns that STATIC_ROOT is missing, as in pytest.ini.
    warnings.filterwarnings("ignore", message="No directory at", category=UserWarning)
    import django

    django.setup()

    from django.conf import settings
    from django.core.management import call_command

    database = settings.DATABASES["default"]
    if database["ENGINE"] != "django.db.backends.sqlite3" or database["NAME"] != ":memory:":
        raise SystemExit("The evaluation must run on the in-memory SQLite database of settings_test.")
    call_command("migrate", verbosity=0)

    import google.generativeai as genai
    from store_api import views

    # views.py read the blanked key when it was imported; give it the real one.
    genai.configure(api_key=key)
    views.api_key = key

    class RecordingChat(views.GeminiChat):
        """The assistant's own GeminiChat, also noting which model answered."""

        def send(self, content):
            try:
                response = super().send(content)
            except Exception:
                gemini_failed.append(True)
                raise
            answered_by.append(self.model_name)
            return response

    # _chat_reply looks the class up by name each time, so this is what it uses.
    views.GeminiChat = RecordingChat


def build_catalog():
    """Create the products of cases.py; return {key: p_id} for the expected answers."""
    from core.models import Category, Product

    category = Category.objects.create(title="Thực phẩm")
    pids = {}
    for key, item in CATALOG.items():
        product = Product.objects.create(
            title=item["title"],
            category=category,
            price=item["price"],
            stock_count=item["stock"],
            weight_volume=item["unit"],
            product_status=item.get("status", "published"),
        )
        pids[key] = product.p_id
    return pids


def chat(case, pause):
    """Send the messages of one case as a new visitor; return the last answer."""
    from django.test import Client

    client = Client()  # a new session: empty cart, no chat history
    history = []
    data = {}
    for message in case["messages"]:
        response = client.post(
            "/api/v1/chat/",
            {"message": message, "history": history, "language": case["language"]},
            content_type="application/json",
        )
        data = response.json()
        # The chat window keeps the history like this (templates/partials/base.html).
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": data.get("reply", "")})
        if data.get("hidden_context"):
            history.append({"role": "user", "content": data["hidden_context"]})
        # The free quota allows 15 calls a minute per model, and one message
        # takes 2-3 calls. Faster than that, the first model answers 429 and
        # the rest of the run is measured on the next one.
        time.sleep(pause)
    return data


def proposed(data, key_of):
    """What the server proposed for the cart, written like the `expect` of a case."""
    action = data.get("action")
    if action == "confirm_add_cart":
        product = data["product"]
        return ("add", key_of.get(product["pid"], product["pid"]), product["qty"])
    if action == "choose_product":
        return ("choose", sorted(key_of.get(c["pid"], c["pid"]) for c in data["choices"]))
    return ("none",)


def is_right(expect, got):
    if expect[0] == "choose":
        # Buttons with exactly these products, or Gemini asking in words.
        return got == ("choose", sorted(expect[1])) or got == ("none",)
    return got == tuple(expect)


def run_case(case, key_of, pause, wait):
    """Run one case; if Gemini did not answer at all, wait and try once more."""
    for attempt in (1, 2):
        answered_by.clear()
        gemini_failed.clear()
        data = chat(case, pause)
        if not gemini_failed:
            break
        if attempt == 1:
            print(f"   {case['id']}: Gemini did not answer, trying again in {wait} s")
            time.sleep(wait)
    got = proposed(data, key_of)
    return {
        "id": case["id"],
        "group": case["group"],
        "messages": case["messages"],
        "expect": list(case["expect"]),
        "got": list(got),
        "measured": not gemini_failed,
        "passed": not gemini_failed and is_right(case["expect"], got),
        "models": list(answered_by),
        "reply": data.get("reply", ""),
    }


def report(results):
    measured = [r for r in results if r["measured"]]
    for r in results:
        verdict = "PASS" if r["passed"] else ("NO ANSWER" if not r["measured"] else "FAIL")
        models = ", ".join(sorted(set(r["models"])))
        print(f"{r['id']:<4} {verdict:<9} expected {r['expect']}  got {r['got']}  {models}")
    print()
    for group, name in GROUPS.items():
        in_group = [r for r in measured if r["group"] == group]
        if in_group:
            print(f"  {group} {name}: {sum(r['passed'] for r in in_group)}/{len(in_group)}")
    passed = sum(r["passed"] for r in measured)
    rate = 100 * passed / len(measured) if measured else 0
    print(f"\nRight product and quantity: {passed}/{len(measured)} ({rate:.1f}%)")
    # A failed case either proposed nothing (Gemini asked again in words) or
    # proposed something else. Only the second puts a wrong button in front
    # of the customer, so it is counted on its own.
    wrong = sum(not r["passed"] and r["got"][0] != "none" for r in measured)
    print(f"Wrong proposal (wrong product or quantity on the button): {wrong}/{len(measured)}")
    unmeasured = len(results) - len(measured)
    if unmeasured:
        print(f"{unmeasured} case(s) not counted: Gemini did not answer.")
    return passed, wrong, len(measured), rate


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Vietnamese text on a Windows console
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="comma-separated case ids, e.g. A1,F2")
    parser.add_argument("--pause", type=float, default=12, help="seconds between two messages (default 12)")
    parser.add_argument("--wait", type=float, default=60, help="seconds before trying a case again (default 60)")
    args = parser.parse_args()

    key = gemini_key()
    if not key:
        raise SystemExit("No GEMINI_API_KEY: set it in the environment or in grocerly/.env.")
    start_django(key)
    pids = build_catalog()
    key_of = {pid: name for name, pid in pids.items()}

    cases = CASES
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in CASES if c["id"] in wanted]

    started = datetime.now()
    results = []
    for case in cases:
        results.append(run_case(case, key_of, args.pause, args.wait))
        r = results[-1]
        print(f"   {r['id']}: {'pass' if r['passed'] else 'fail'}")
    print()
    passed, wrong, measured, rate = report(results)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{started:%Y-%m-%d_%H%M}.json"
    out.write_text(json.dumps({
        "started": started.isoformat(timespec="minutes"),
        "passed": passed,
        "measured": measured,
        "rate": round(rate, 1),
        "wrong_proposals": wrong,
        "cases": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {out.relative_to(GROCERLY_DIR)}")


if __name__ == "__main__":
    main()
