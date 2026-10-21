import os
import google.generativeai as genai
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from core.models import Product, Category
from store_api.serializers import ProductSerializer, CategorySerializer

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
    Returns a list of matching products.
    """
    products = buyable_products()
    for word in query.split():
        products = products.filter(title__icontains=word)
    products = products[:5]
    if not products.exists():
        return [{"message": "No matching products found."}]
        
    results = []
    for p in products:
        results.append({
            "title": p.title,
            "price": f"{float(p.price)} VND",
            "stock_count": p.stock_count,
            "weight_volume": p.weight_volume,
            "product_url_id": p.p_id
        })
    return results

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
            "price": f"{float(p.price)} VND"
        })
    return results

api_key = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=api_key)

try:
    # Initialize the model with tools and system instruction
    model = genai.GenerativeModel(
        model_name='gemini-3.1-flash-lite',
        tools=[search_products, get_bestsellers, request_add_to_cart, request_checkout],
        system_instruction=(
            "You are Grocerly Assistant, the AI shopping assistant for Grocerly E-commerce. "
            "You are polite, helpful, and concise. "
            "Always use the provided tools to search for products when the user asks about them. "
            "If quoting a price, mention the VND currency clearly. "
            "If a user wants to buy something, or add to cart, YOU MUST use the request_add_to_cart tool! "
            "If they ask to checkout, use the request_checkout tool."
        )
    )
    # create a global conversation history placeholder or start chat
    # To support multiple users effectively, we should let the frontend pass history,
    # but for this MVP, we will instantiate a new chat per request and pass history.
except Exception as e:
    model = None
    print(f"Failed to initialize Gemini Model: {e}")

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
    if not model or not api_key:
        return Response({
            "reply": str(_("System Error: Gemini API Key is missing or invalid. Please configure it in .env."))
        }, status=200) # Returns 200 so UI doesn't crash, but shows warning.

    user_message = request.data.get('message', '')
    history_data = request.data.get('history', [])

    if not user_message:
        return Response({"error": "Empty message"}, status=400)

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

        # Initialize chat with history (disabling automatic function calling)
        chat = model.start_chat(history=formatted_history)
        
        response = chat.send_message(user_message)
        
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

                # The assistant may only offer what the customer could buy on
                # the site itself: a product the shop has hidden is "not found"
                # here too, one with nothing left in stock is refused instead
                # of proposed (L-9), and so is a quantity the stock cannot cover
                # (L-14). Gemini gets the reason so it can tell the customer.
                # If the stock drops between this question and the customer's
                # click, the cart still brings the line down to it (D-024).
                p = published_products().filter(p_id=p_id).first()
                stock = (p.stock_count or 0) if p else 0
                if p is None:
                    tool_error = "Product not found"
                elif stock <= 0:
                    tool_error = "Product is out of stock"
                elif qty < 1:
                    tool_error = "Quantity must be at least 1"
                elif qty > stock:
                    tool_error = f"Only {stock} left in stock"
                else:
                    # Interrupt conversation to ask for UI confirmation
                    return Response({
                        "reply": str(_("Would you like to add **%(qty)sx %(title)s** to your cart?")) % {
                            'qty': qty, 'title': p.title,
                        },
                        "action": "confirm_add_cart",
                        "product": {
                            "id": str(p.id),
                            "pid": p.p_id,
                            "title": p.title,
                            "qty": qty,
                            "price": str(p.price),
                            "image": p.image.url if p.image else ""
                        }
                    })

                response = chat.send_message([{
                    "function_response": {
                        "name": name,
                        "response": {"error": tool_error}
                    }
                }])
                continue

            elif name == "request_checkout":
                return Response({
                    "reply": str(_("You can review your items and complete your order at the checkout page.")),
                    "action": "confirm_checkout"
                })

            elif name == "search_products":
                query_val = args.get('query', '')
                results = search_products(query_val)
                response = chat.send_message([{
                    "function_response": {
                        "name": name,
                        "response": {"result": results}
                    }
                }])
                return Response({
                    "reply": response.text,
                    "hidden_context": f"(SYSTEM CONTEXT - DO NOT MENTION: Latest Search Results: {results})"
                })
                
            elif name == "get_bestsellers":
                results = get_bestsellers()
                response = chat.send_message([{
                    "function_response": {
                        "name": name,
                        "response": {"result": results}
                    }
                }])
                return Response({
                    "reply": response.text,
                    "hidden_context": f"(SYSTEM CONTEXT - DO NOT MENTION: Latest Bestsellers: {results})"
                })
                
            else:
                break
        
        return Response({
            "reply": response.text
        })
    except Exception as e:
        import traceback
        import re
        traceback.print_exc()
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
            if "PerDay" in error_msg:
                return Response({
                    "reply": str(_("🛑 Hệ thống AI đã hết lượt sử dụng miễn phí (giới hạn 500 tin nhắn/ngày). Vui lòng quay lại vào ngày mai!"))
                }, status=200)
            
            # Try to extract the retry delay from Google's error response
            retry_match = re.search(r'retry in (\d+\.?\d*)', error_msg, re.IGNORECASE)
            if not retry_match:
                retry_match = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', error_msg)
            
            if retry_match:
                wait_seconds = int(float(retry_match.group(1)))
                return Response({
                    "reply": str(_("⏳ Hệ thống AI đang tạm nghỉ do giới hạn miễn phí. Vui lòng đợi **%(wait_seconds)s giây** rồi thử lại nhé!")) % {'wait_seconds': wait_seconds},
                    "retry_after": wait_seconds
                }, status=200)
            else:
                return Response({
                    "reply": str(_("⏳ Hệ thống AI đang tạm nghỉ do giới hạn miễn phí. Vui lòng đợi khoảng 30 giây rồi thử lại nhé!")),
                    "retry_after": 30
                }, status=200)
        return Response({"reply": str(_("Mình đang gặp trục trặc kết nối. Bạn thử lại sau nhé!"))}, status=200)
