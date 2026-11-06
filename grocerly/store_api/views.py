import logging
import os
import time

import google.generativeai as genai
from django.core.cache import cache
from google.api_core import exceptions as google_errors
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from core.models import Product, Category
from core.templatetags.currency_filters import vnd
from store_api.serializers import ProductSerializer, CategorySerializer

logger = logging.getLogger(__name__)

# The store pages decide what a customer may see with one condition:
# `product_status='published'` (core/views.py). The assistant and the API used
# to ask a different question - `status=True, in_stock=True` - so a product the
# shop had hidden was still found here (L-10). Those two booleans look like they
# answer it, but no form on the site ever writes them, so they stay True on
# every product; what the shop really keeps up to date is `stock_count`, which
# is also what the cart trusts (D-024).


def published_products():
    """Products a customer is allowed to see, as the store pages define it."""
    return Product.objects.filter(product_status='published')


def buyable_products():
    """Published products with something left in stock."""
    return published_products().filter(stock_count__gt=0)


class ProductListAPI(generics.ListAPIView):
    queryset = buyable_products()
    serializer_class = ProductSerializer

class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['GET'])
def health(request):
    """Which commit this server runs; the deploy job in CI waits for it (D-036)."""
    # Render sets RENDER_GIT_COMMIT on every deploy. Anywhere else it is unset,
    # and "unknown" can never match the commit CI is waiting for.
    return Response({
        "status": "ok",
        "commit": os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    })

# ================= AI CHAT CONFIGURATION ================= #

def search_products(query: str) -> list[dict]:
    """Search for products in the grocery store based on a text query.
    Call this whenever the user asks about product availability, price, details, or stock.
    Product titles are in Vietnamese, so write the query in Vietnamese: translate
    product names from any other language first (e.g. "watermelon" -> "dưa hấu").
    A product is found only if its title holds every word of the query, so use
    just the main words of the product name and leave out general words such as
    "thịt", "rau" or "trái" (e.g. "beef" -> "bò", not "thịt bò").
    Returns a list of matching products.
    """
    # Gemini reads this docstring as the tool description. The search below
    # only matches words in the title, so an English query found nothing (L-31),
    # and neither did a query with one word too many (L-42, D-049).
    return search_results(find_products(query))


def find_products(query):
    """Buyable products whose title holds every word of `query`, at most 5."""
    products = buyable_products()
    for word in query.split():
        products = products.filter(title__icontains=word)
    return list(products[:5])


def search_results(products):
    """What Gemini is told about the products a search found."""
    if not products:
        return [{"message": "No matching products found."}]
    return [
        {
            "title": p.title,
            # Whole VND, written from the Decimal; float is not used for money.
            "price": f"{p.price:.0f} VND",
            "stock_count": p.stock_count,
            "weight_volume": p.weight_volume,
            "product_url_id": p.p_id,
        }
        for p in products
    ]

def request_add_to_cart(product_url_id: str, qty: int = 1):
    """Call this function when the user asks to add an item to their cart or wants to buy an item.
    Do not just tell them it's added; you MUST call this function so the system can confirm it.
    Provide the exact product_url_id from the search results, and how many they want (qty).
    """
    pass

def request_checkout():
    """Call this function when the user asks to checkout, pay, or place their order."""
    pass

def get_bestsellers() -> list[dict]:
    """Get the bestselling and featured products of the store.
    Call this when the user asks what is popular or what to buy.
    """
    products = buyable_products().filter(featured=True)[:5]
    results = []
    for p in products:
        results.append({
            "title": p.title,
            "price": f"{p.price:.0f} VND"
        })
    return results


# ---------- what the assistant may propose for the cart (UC-17) ----------

# Above this many units of one product in one go, the assistant asks the
# customer to check the number before adding (SRS AC-17.2, D-048).
LARGE_QTY = 10


def cart_problem(p, qty, cart):
    """Why `qty` of product `p` may not be proposed, or None if it may.

    The assistant may only offer what the customer could buy on the site
    itself: a product the shop has hidden is "not found" here too, one with
    nothing left in stock is refused instead of proposed (L-9), and so is a
    quantity the stock cannot cover (L-14). The cart adds to the line it
    already has, so what must fit the stock is the total (L-18). The reason
    goes back to Gemini so it can tell the customer.
    If the stock drops between this question and the customer's click, the
    cart still brings the line down to it (D-024).
    """
    if p is None:
        return "Product not found"
    stock = p.stock_count or 0
    if stock <= 0:
        return "Product is out of stock"
    if qty < 1:
        return "Quantity must be at least 1"
    in_cart = cart.get(str(p.id), {}).get('qty', 0)
    if in_cart + qty > stock:
        problem = f"Only {stock} left in stock"
        if in_cart:
            problem += f" and the cart already has {in_cart}"
        return problem
    return None


def money_text(p, qty):
    """Quantity, name, unit price and total, ready for the translated sentences.
    Prices come from the database and are written like on the shop pages,
    never taken from what Gemini said (AC-17.1)."""
    return {'qty': qty, 'title': p.title, 'price': vnd(p.price), 'total': vnd(p.price * qty)}


def proposal(p, qty):
    """One product offered for the cart, as data the chat window and the
    assistant evaluation (P-42 d) can read without parsing sentences (AC-17.5)."""
    large_qty = qty > LARGE_QTY
    if large_qty:
        label = str(_("Yes, add %(qty)s to cart")) % {'qty': qty}
    else:
        label = str(_("Yes, Add to Cart"))
    return {
        "id": str(p.id),
        "pid": p.p_id,
        "title": p.title,
        "qty": qty,
        "price": str(p.price),
        "total": str(p.price * qty),
        "large_qty": large_qty,
        "label": label,
        "image": p.image.url if p.image else "",
    }


def large_qty_warning(qty):
    """The ask-again sentence for a quantity above LARGE_QTY, else nothing."""
    if qty <= LARGE_QTY:
        return ""
    return str(_("%(qty)s is more than usual, please check the quantity.")) % {'qty': qty} + " "


def confirm_add_cart(p, qty, hidden_context=None):
    """Ask the customer to confirm one product (AC-17.1, AC-17.2).
    The search results of this message go back with the question, as with
    choose_product: the customer may change the quantity in the next message
    ("sorry, only 10"), and Gemini still needs the product id then (L-38)."""
    values = money_text(p, qty)
    question = str(_("Would you like to add **%(qty)sx %(title)s** to your cart?")) % values
    price = str(_("Unit price %(price)s ₫, total **%(total)s ₫**.")) % values
    reply = {
        "reply": large_qty_warning(qty) + question + " " + price,
        "action": "confirm_add_cart",
        "product": proposal(p, qty),
    }
    if hidden_context:
        reply["hidden_context"] = hidden_context
    return reply


def choose_product(choices, qty, hidden_context):
    """Let the customer pick among several matching products (AC-17.3).
    Each button already says quantity, name and total, so clicking one both
    picks and confirms. The search results stay in the chat history, so the
    customer may also answer in words ("the second one")."""
    reply = large_qty_warning(qty) + str(_("Several products match. Tap the one you want to add to your cart:"))
    return {
        "reply": reply,
        "action": "choose_product",
        "choices": [
            {**proposal(c, qty), "label": str(_("Add %(qty)sx %(title)s - %(total)s ₫")) % money_text(c, qty)}
            for c in choices
        ],
        "hidden_context": hidden_context,
    }

api_key = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

# The models the assistant tries, in this order (D-060). Overload (503) and the
# free quota (429) hit one model at a time, so when one fails the next one
# usually still answers. The two "lite" models come first: in the measurements
# of 06/11/2026 they were 2-3 times faster and have 500 calls a day, against 20
# for the bigger "flash" models, which stay as a reserve.
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]
SYSTEM_INSTRUCTION = (
    "You are Grocerly Assistant, the AI shopping assistant for Grocerly E-commerce. "
    "You are polite, helpful, and concise. "
    "Always use the provided tools to search for products when the user asks about them. "
    "If quoting a price, mention the VND currency clearly. "
    "If a user wants to buy something, or add to cart, YOU MUST use the request_add_to_cart tool! "
    "If they ask to checkout, use the request_checkout tool."
)

try:
    # Building a model does not call Google; that happens on send_message.
    models = {
        name: genai.GenerativeModel(
            model_name=name,
            tools=[search_products, get_bestsellers, request_add_to_cart, request_checkout],
            system_instruction=SYSTEM_INSTRUCTION,
        )
        for name in GEMINI_MODELS
    }
except Exception as e:
    models = {}
    print(f"Failed to initialize Gemini Model: {e}")


# Time limits (L-37, D-051, D-060). By default the library waits up to 600 s
# and calls again by itself after a 503, but gunicorn kills the request at 30 s.
# An overloaded model often does not answer 503 at once: it hangs until the
# deadline. So one try gets 8 s (a healthy model answers in 1-5 s) and no retry
# by the library, and the whole customer message gets 25 s whatever the number
# of models tried, which still leaves time before gunicorn's 30 s.
GEMINI_TIMEOUT = 8
GEMINI_DEADLINE = 25
# A model that just failed is skipped by the next messages for this long, so
# they do not wait another 8 s on a model that is still hanging.
GEMINI_SKIP_SECONDS = 5 * 60

# Errors that mean "this model cannot answer right now, try another one":
# ServerError covers 500, 503 and the 504 a deadline raises; TooManyRequests is
# the 429 of the quota. Anything else (400 bad request, 403 wrong key, 404 wrong
# model name) is a mistake on our side that another model would not fix, so it
# is not hidden behind a fallback.
MODEL_ERRORS = (google_errors.ServerError, google_errors.TooManyRequests)


def skip_key(name):
    return f"gemini-skip:{name}"


def models_to_try():
    """GEMINI_MODELS in order, minus those that failed in the last few minutes.
    If every model failed recently, try them all anyway rather than not at all."""
    fresh = [name for name in GEMINI_MODELS if not cache.get(skip_key(name))]
    return fresh or list(GEMINI_MODELS)


class GeminiChat:
    """The conversation of one customer message with Gemini (D-060).

    Each send() starts from the first model in models_to_try(), which is the
    model that answered last unless the skip list changed meanwhile. If a model
    fails, the conversation so far moves to the next model and the same content
    is sent again. The library adds to a chat's history only when a call
    succeeds, and our tools only read data, so sending again is safe.
    """

    def __init__(self, history):
        self.started = time.monotonic()
        self.history = history  # what was said before, in Gemini's format
        self.chat = None
        self.model_name = None

    def send(self, content):
        error = None
        for name in models_to_try():
            time_left = GEMINI_DEADLINE - (time.monotonic() - self.started)
            if time_left <= 0:
                break
            if name != self.model_name:
                history = self.chat.history if self.chat else self.history
                self.chat = models[name].start_chat(history=history)
                self.model_name = name
            timeout = min(GEMINI_TIMEOUT, time_left)
            try:
                return self.chat.send_message(
                    content, request_options={"timeout": timeout, "retry": None}
                )
            except MODEL_ERRORS as e:
                logger.warning("Gemini model %s failed, trying the next one: %s", name, e)
                # A model that ran out of time only because this message had
                # less than GEMINI_TIMEOUT left may be healthy: other messages
                # should not skip it.
                cut_short = isinstance(e, google_errors.DeadlineExceeded) and timeout < GEMINI_TIMEOUT
                if not cut_short:
                    cache.set(skip_key(name), True, GEMINI_SKIP_SECONDS)
                error = e
        # Every model failed, or the message ran out of time. The last error goes
        # to the caller, which turns it into the answer the customer reads.
        raise error or google_errors.DeadlineExceeded("The chat message ran out of time")

@api_view(['POST'])
def ai_chat(request):
    # The chat API sits outside i18n_patterns, so the URL does not say which
    # language the customer is reading. The chat window sends the language of
    # its page; without one, keep what Django chose from the language cookie
    # (L-15).
    language = request.data.get('language')
    if not isinstance(language, str) or language not in dict(settings.LANGUAGES):
        language = translation.get_language()
    with translation.override(language):
        return _chat_reply(request)


def _chat_reply(request):
    if not models or not api_key:
        return Response({
            "reply": str(_("System Error: Gemini API Key is missing or invalid. Please configure it in .env."))
        }, status=200) # Returns 200 so UI doesn't crash, but shows warning.

    user_message = request.data.get('message', '')
    history_data = request.data.get('history', [])

    if not user_message:
        return Response({"error": str(_("Empty message"))}, status=400)

    try:
        # `history` is what was said before `message`. The chat window used to
        # put the new message at the end of `history` as well, so Gemini read it
        # twice and a customer answering "2" was offered 22 (L-13). The window
        # no longer does that, but a page opened before the fix still sends the
        # copy. This sits inside `try` because `history` comes from the browser
        # and may not be a list at all.
        if history_data and history_data[-1] == {'role': 'user', 'content': user_message}:
            history_data = history_data[:-1]

        # Convert frontend history to gemini history format
        formatted_history = []
        for msg in history_data:
            role = 'model' if msg.get('role') == 'assistant' else 'user'
            formatted_history.append({"role": role, "parts": [msg.get('content', '')]})

        # One conversation for this message; it may move to another model (D-060).
        chat = GeminiChat(formatted_history)
        response = chat.send(user_message)
        hidden_context = None
        # Products the latest search of this message found. Several of them
        # and Gemini goes straight to the cart: the customer picks (AC-17.3).
        found = []

        # Manual loop to process function calls (max 3 loops to prevent recursion)
        for _step in range(3):
            if not response.parts:
                break
                
            # Collect all function calls from the response
            function_calls_to_execute = []
            for part in response.parts:
                if part.function_call:
                    function_calls_to_execute.append(part.function_call)
                    
            if not function_calls_to_execute:
                break
                
            # We process the first function call for simplicity
            fc = function_calls_to_execute[0]
            name = fc.name
            args = {k: v for k, v in fc.args.items()} if hasattr(fc.args, 'items') else dict(fc.args)
            
            if name == "request_add_to_cart":
                p_id = args.get('product_url_id')
                # Handle possible float representation from JSON
                try:
                    qty = int(float(args.get('qty', 1)))
                except Exception:
                    qty = 1

                cart = request.session.get('cart_data_obj', {})
                p = published_products().filter(p_id=p_id).first()
                tool_error = cart_problem(p, qty, cart)
                if tool_error is None:
                    # Stop the conversation here: the customer confirms in
                    # the chat window. Only products that could take this
                    # quantity are offered as choices.
                    choices = [c for c in found if cart_problem(c, qty, cart) is None]
                    if len(choices) >= 2:
                        return Response(choose_product(choices, qty, hidden_context))
                    return Response(confirm_add_cart(p, qty, hidden_context))

                response = chat.send([{
                    "function_response": {
                        "name": name,
                        "response": {"error": tool_error}
                    }
                }])
                continue

            elif name == "request_checkout":
                # An empty cart has nothing to pay for (UC-18). Gemini is told,
                # like it is told about a product out of stock, and asks the
                # customer to pick something first (L-41).
                if not request.session.get('cart_data_obj'):
                    response = chat.send([{
                        "function_response": {
                            "name": name,
                            "response": {"error": "The cart is empty"}
                        }
                    }])
                    continue
                return Response({
                    "reply": str(_("You can review your items and complete your order at the checkout page.")),
                    "action": "confirm_checkout"
                })

            # The answer to a search may be another tool call, not text: asked to
            # "find carrots and add one", Gemini searches, then asks for the cart
            # with the p_id it found. So both lookups go round the loop like the
            # other tools instead of answering at once (L-30).
            elif name == "search_products":
                found = find_products(args.get('query', ''))
                results = search_results(found)
                hidden_context = f"(SYSTEM CONTEXT - DO NOT MENTION: Latest Search Results: {results})"
                response = chat.send([{
                    "function_response": {
                        "name": name,
                        "response": {"result": results}
                    }
                }])
                continue

            elif name == "get_bestsellers":
                results = get_bestsellers()
                hidden_context = f"(SYSTEM CONTEXT - DO NOT MENTION: Latest Bestsellers: {results})"
                response = chat.send([{
                    "function_response": {
                        "name": name,
                        "response": {"result": results}
                    }
                }])
                continue

            else:
                break

        if any(part.function_call for part in response.parts):
            # Three tools in a row and Gemini still asks for another. Such an
            # answer has no text, and reading .text would raise (L-30).
            reply = {"reply": str(_(
                "Sorry, I could not finish that in one go. Could you tell me one step at a time?"
            ))}
        else:
            reply = {"reply": response.text}
        # The chat window keeps the results in its history so that the next
        # message ("add the second one") can name a product Gemini just found.
        if hidden_context:
            reply["hidden_context"] = hidden_context
        return Response(reply)
    except Exception as e:
        import traceback
        import re
        traceback.print_exc()
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
            if "PerDay" in error_msg:
                return Response({
                    "reply": str(_("🛑 The AI assistant has used up its free quota for today. Please come back tomorrow!"))
                }, status=200)
            
            # Try to extract the retry delay from Google's error response
            retry_match = re.search(r'retry in (\d+\.?\d*)', error_msg, re.IGNORECASE)
            if not retry_match:
                retry_match = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', error_msg)
            
            if retry_match:
                wait_seconds = int(float(retry_match.group(1)))
                return Response({
                    "reply": str(_("⏳ The AI assistant is paused by its free usage limit. Please wait **%(wait_seconds)s seconds** and try again!")) % {'wait_seconds': wait_seconds},
                    "retry_after": wait_seconds
                }, status=200)
            else:
                return Response({
                    "reply": str(_("⏳ The AI assistant is paused by its free usage limit. Please wait about 30 seconds and try again!")),
                    "retry_after": 30
                }, status=200)
        return Response({"reply": str(_("I am having trouble connecting. Please try again later!"))}, status=200)
