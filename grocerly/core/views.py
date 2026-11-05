from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Avg, Count, Min, Max
from django.db.models.functions import ExtractMonth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from django.core import serializers
from taggit.models import Tag

from decimal import Decimal
from core.vnpay import vnpay
from django.utils import timezone
from django.utils.dates import MONTHS
from django.utils.translation import gettext_lazy as _
from zoneinfo import ZoneInfo

from core.models import (
    Category, Vendor, Product, ProductReview,
    CartOrder, CartOrderItem, Wishlist, Address, Coupon, wishlist_of,
)
from core.forms import CheckoutInfoForm, ContactForm, ProductReviewForm
from userauths.models import Profile


import re
import logging

# Goes to the Render log through LOGGING in settings.py (D-038).
logger = logging.getLogger(__name__)


def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        val_str = str(val).replace('₫', '').replace('VND', '').replace('$', '').strip()
        
        if re.match(r'^\d{1,3}(\.\d{3})+$', val_str):
            val_str = val_str.replace('.', '')
            
        if re.match(r'^\d{1,3}(,\d{3})+$', val_str):
            val_str = val_str.replace(',', '')
            
        val_str = re.sub(r'[^\d.,]', '', val_str)
        if not val_str:
            return default
            
        val_str = val_str.replace(',', '.')
        return float(val_str)
    except (ValueError, TypeError):
        return default

def safe_int(val, default=1):
    try:
        return int(safe_float(val, default))
    except (ValueError, TypeError):
        return default



# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin/')
        elif request.user.is_staff:
            return redirect('useradmin:dashboard')
            
    products = Product.objects.filter(product_status='published').order_by('-id')
    categories = Category.objects.all()
    deals_products = Product.objects.filter(product_status='published', featured=True).order_by('-id')[:4]
    new_products_sidebar = Product.objects.filter(product_status='published').order_by('-date')[:3]

    context = {
        'products': products,
        'categories': categories,
        'deals_products': deals_products,
        'new_products_sidebar': new_products_sidebar,
    }

    return render(request, 'core/index.html', context)


def category_list_view(request):
    categories = Category.objects.all()

    context = {
        'categories': categories
    }

    return render(request, 'core/category-list.html', context)


def product_list_view(request):
    products = Product.objects.filter(product_status='published').order_by('-id')
    tags = Tag.objects.all().order_by('-id')[:6]
    categories = Category.objects.all().order_by('title')
    vendors = Vendor.objects.all().order_by('name')
    deals_products = Product.objects.filter(product_status='published', featured=True).order_by('-id')[:4]

    price_range = products.aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'products': products,
        'tags': tags,
        'categories': categories,
        'vendors': vendors,
        'deals_products': deals_products,
        'product_count': products.count(),
        'min_price': price_range.get('min_price') or 0,
        'max_price': price_range.get('max_price') or 0,
    }

    return render(request, 'core/product-list.html', context)


def category_product_list_view(request, c_id):
    category = get_object_or_404(Category, c_id=c_id)
    products = Product.objects.filter(category=category, product_status='published').order_by('-id')

    context = {
        'category': category,
        'products': products
    }

    return render(request, 'core/category-product-list.html', context)


def vendor_list_view(request):
    vendors = Vendor.objects.all()

    context = {
        'vendors': vendors
    }

    return render(request, 'core/vendor-list.html', context)


def vendor_detail_view(request, v_id):
    vendor = get_object_or_404(Vendor, v_id=v_id)
    products = Product.objects.filter(vendor=vendor, product_status='published').order_by('-id')
    context = {
        'vendor': vendor,
        'products': products
    }

    return render(request, 'core/vendor-detail.html', context)


def product_detail_view(request, p_id):
    product = get_object_or_404(Product, p_id=p_id)
    images = product.p_image.all()
    related_products = Product.objects.filter(category=product.category, product_status='published').exclude(p_id=p_id).order_by('-id')[:4]

    # Getting all reviews related to the product
    reviews = ProductReview.objects.filter(product=product).order_by('-date')

    # Getting average review rating
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    total_reviews = reviews.count()
    rating_5 = int((reviews.filter(rating=5).count() / total_reviews) * 100) if total_reviews > 0 else 0
    rating_4 = int((reviews.filter(rating=4).count() / total_reviews) * 100) if total_reviews > 0 else 0
    rating_3 = int((reviews.filter(rating=3).count() / total_reviews) * 100) if total_reviews > 0 else 0
    rating_2 = int((reviews.filter(rating=2).count() / total_reviews) * 100) if total_reviews > 0 else 0
    rating_1 = int((reviews.filter(rating=1).count() / total_reviews) * 100) if total_reviews > 0 else 0

    # Product Review form
    review_form = ProductReviewForm()

    # Biểu mẫu đánh giá chỉ hiện với khách đã nhận sản phẩm và chưa đánh giá lần nào
    # (UC-14). ajax_add_review kiểm tra lại đúng hai điều kiện này ở phía máy chủ.
    make_review = False

    if request.user.is_authenticated:
        already_reviewed = ProductReview.objects.filter(user=request.user, product=product).exists()
        make_review = has_received_product(request.user, product) and not already_reviewed

    context = {
        'p': product,
        'p_image': images,
        'related_products': related_products,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_form': review_form,
        'make_review': make_review,
        'rating_5': rating_5,
        'rating_4': rating_4,
        'rating_3': rating_3,
        'rating_2': rating_2,
        'rating_1': rating_1,
    }

    return render(request, 'core/product-detail.html', context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status='published').order_by('-id')

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        'products': products,
        'tag': tag,
    }

    return render(request, 'core/tag.html', context)


def has_received_product(user, product):
    """True if `user` has an order holding `product` that already left the store."""
    return CartOrderItem.objects.filter(
        order__user=user,
        order__product_status__in=('shipped', 'delivered'),
        product=product,
    ).exists()


@login_required
def ajax_add_review(request, p_id):
    product = get_object_or_404(Product, pk=p_id)
    user = request.user

    # UC-14: chỉ khách đã nhận sản phẩm mới đánh giá được, và mỗi người một lần.
    # Trang chi tiết đã giấu sẵn biểu mẫu, nhưng đó chỉ là giao diện -
    # ai cũng gửi thẳng POST tới đây được nên máy chủ phải tự kiểm tra lại.
    if not has_received_product(user, product):
        return JsonResponse(
            {'bool': False, 'message': _("You can only review a product you have received.")},
            status=403,
        )

    if ProductReview.objects.filter(user=user, product=product).exists():
        return JsonResponse(
            {'bool': False, 'message': _("You have already reviewed this product.")},
            status=403,
        )

    form = ProductReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'bool': False, 'errors': form.errors}, status=400)

    review = form.save(commit=False)
    review.user = user
    review.product = product
    review.save()

    context = {
        'user': user.username,
        'review': review.review,
        'rating': review.rating,
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))

    return JsonResponse({
        'bool': True,
        # Shown on the product page by the script of partials/base.html (L-49).
        'message': _("Thank you! Your review has been added."),
        'context': context,
        'average_reviews': average_reviews,
    })


# ======================== Search ========================

def search_view(request):
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query, product_status='published').order_by('-date')

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'core/search.html', context)


def filter_product(request):
    category_ids = [c for c in (request.GET.getlist("category") + request.GET.getlist("category[]")) if c.isdigit()]
    vendor_ids = [v for v in (request.GET.getlist("vendor") + request.GET.getlist("vendor[]")) if v.isdigit()]
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = Product.objects.filter(product_status='published').order_by('-id').distinct()

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (TypeError, ValueError):
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (TypeError, ValueError):
            pass

    if category_ids:
        products = products.filter(category__id__in=category_ids).distinct()

    if vendor_ids:
        products = products.filter(vendor__id__in=vendor_ids).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products}, request=request)
    return JsonResponse({
        "data": data,
        "count": products.count(),
    })


# ======================== Cart (Session-based) ========================

def _refresh_cart(request):
    """Rewrite every line of the session cart with the price and the stock kept
    in the database, then return the total of the cart in VND.

    The browser sends a price when it adds a product to the cart, because that is
    the price the product page displays - but the customer can edit that request
    (L-6). So the price kept in the session is only ever a copy of
    `Product.price`, and every amount the server computes - the cart total here,
    the order total in `save_checkout_info` - is read from the database.

    The quantity is the customer's to choose, but the shop cannot sell more than
    it has: a line asking for more than `Product.stock_count` is brought back
    down to the stock and the customer is told (L-7). The quantity box on the
    page only has a lower bound, and an upper bound there would not help either:
    it would travel in a request the customer can edit.

    A line whose product no longer exists, has been soft deleted, or has nothing
    left in stock is dropped.
    """
    cart_data = request.session.get('cart_data_obj')
    if not cart_data:
        return Decimal("0")

    products_in_cart = {
        str(product.id): product
        for product in Product.objects.filter(
            id__in=[safe_int(p_id, 0) for p_id in cart_data]
        )
    }

    cart_total_amount = Decimal("0")
    for p_id in list(cart_data):
        product = products_in_cart.get(p_id)
        if product is None:
            del cart_data[p_id]
            continue

        stock = product.stock_count or 0
        if stock <= 0:
            messages.warning(
                request,
                _("%(product)s is out of stock and has been removed from your cart.")
                % {"product": product.title},
            )
            del cart_data[p_id]
            continue

        item = cart_data[p_id]
        qty = safe_int(item.get('qty'))
        if qty > stock:
            messages.warning(
                request,
                _("Only %(stock)s of %(product)s left in stock, so your cart now holds %(stock)s.")
                % {"stock": stock, "product": product.title},
            )
            qty = stock

        item['qty'] = qty
        item['price'] = str(product.price)
        cart_total_amount += product.price * qty

    request.session['cart_data_obj'] = cart_data
    return cart_total_amount


# The cart and wishlist routes only take POST, which the CSRF check covers: on GET a
# link planted on another site could change them for a signed-in customer (L-19).
@require_POST
def add_to_cart(request):
    product = Product.objects.filter(id=safe_int(request.POST.get('id'), 0)).first()
    if product is None:
        return JsonResponse({'error': _("Product not found.")}, status=404)

    # The request only says which product and how many of it; everything the cart
    # line shows is read from the database.
    product_id = str(product.id)
    cart_data = request.session.get('cart_data_obj', {})
    qty = safe_int(request.POST.get('qty'))

    # This route adds to the line; setting a quantity is update_cart's job (L-18).
    if product_id in cart_data:
        cart_data[product_id]['qty'] = safe_int(cart_data[product_id].get('qty')) + qty
    else:
        cart_data[product_id] = {
            'title': product.title,
            'qty': qty,
            'price': str(product.price),
            'image': product.image.url if product.image else '',
            'pid': product.p_id,
        }

    request.session['cart_data_obj'] = cart_data
    wanted_qty = cart_data[product_id]['qty']

    # The quantity asked for can be more than the shop has left, so the cart is
    # refreshed before answering: the line sent back to the page holds what can
    # actually be sold (L-7). wanted_qty lets the chat window tell the two apart.
    _refresh_cart(request)
    cart_data = request.session.get('cart_data_obj', {})

    return JsonResponse({
        'data': cart_data,
        'totalcartitems': len(cart_data),
        'wanted_qty': wanted_qty,
    })


def cart_view(request):
    cart_total_amount = _refresh_cart(request)
    if request.session.get('cart_data_obj'):
        return render(request, 'core/cart.html', {
            'cart_data': request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount,
        })
    else:
        messages.warning(request, _("Your cart is empty"))
        return redirect("core:index")


def _checkout_info_page(request, form, cart_total_amount):
    """The shipping information page, with `form` either filled from the profile or
    sent back with its errors (L-50)."""
    return render(request, 'core/checkout-info.html', {
        'cart_data': request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount,
        'form': form,
    })


@login_required
def checkout_info_view(request):
    cart_total_amount = _refresh_cart(request)
    if request.session.get('cart_data_obj'):
        profile = request.user.profile
        form = CheckoutInfoForm(initial={
            'full_name': profile.full_name or request.user.username.title(),
            'email': request.user.email,
            'mobile': profile.phone or '',
            'address': profile.address or '',
        })
        return _checkout_info_page(request, form, cart_total_amount)
    else:
        pending_order = _get_pending_order_from_session(request)
        if pending_order:
            messages.info(request, _("You have a pending checkout. Please complete payment."))
            return redirect('core:checkout', pending_order.oid)

        messages.warning(request, _("Your cart is empty"))
        return redirect("core:index")


@require_POST
def delete_item_from_cart(request):
    product_id = str(request.POST['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = _refresh_cart(request)
    cart_data = request.session.get('cart_data_obj', {})

    context = render_to_string("core/async/cart-list.html", {
        'cart_data': cart_data,
        'totalcartitems': len(cart_data),
        'cart_total_amount': cart_total_amount,
    })
    return JsonResponse({
        'data': context,
        'totalcartitems': len(cart_data),
    })


@require_POST
def update_cart(request):
    product_id = str(request.POST['id'])
    product_qty = request.POST['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[product_id]['qty'] = safe_int(product_qty)
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = _refresh_cart(request)
    cart_data = request.session.get('cart_data_obj', {})

    context = render_to_string("core/async/cart-list.html", {
        'cart_data': cart_data,
        'totalcartitems': len(cart_data),
        'cart_total_amount': cart_total_amount,
    })
    return JsonResponse({
        'data': context,
        'totalcartitems': len(cart_data),
    })


# ======================== Checkout + Payment ========================


def _get_pending_order_from_session(request):
    pending_oid = request.session.get('pending_order_oid')
    if not pending_oid:
        return None

    # A checkout still in progress is an unpaid order the staff has not handled
    # yet. The session keeps the oid after the staff ships or cancels the order;
    # without the status condition the next checkout would be written into it.
    if request.user.is_authenticated:
        return CartOrder.objects.filter(
            oid=pending_oid,
            user=request.user,
            paid_status=False,
            product_status='processing',
        ).first()

    return None


def _get_checkout_order_or_none(request, oid):
    if request.user.is_authenticated:
        return CartOrder.objects.filter(oid=oid, user=request.user).first()
    return None

@login_required
def save_checkout_info(request):
    if request.method == "POST":
        # The order total comes from the database, not from the prices the
        # browser put in the cart (L-6).
        total_amount = _refresh_cart(request)
        cart_data = request.session.get('cart_data_obj')

        # CheckoutInfoForm checks the required boxes, the email and the length of
        # each value, so nothing longer than its column reaches the database (L-50).
        form = CheckoutInfoForm(request.POST)
        if cart_data and not form.is_valid():
            return _checkout_info_page(request, form, total_amount)

        if cart_data:
            full_name = form.cleaned_data["full_name"]
            email = form.cleaned_data["email"]
            mobile = form.cleaned_data["mobile"]
            address = form.cleaned_data["address"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            country = form.cleaned_data["country"]

            order = _get_pending_order_from_session(request)

            if order:
                order.price = total_amount
                order.full_name = full_name
                order.email = email
                order.phone = mobile
                order.address = address
                order.city = city
                order.state = state
                order.country = country
                order.saved = 0
                order.coupons.clear()
                order.save()
                CartOrderItem.objects.filter(order=order).delete()
            else:
                order = CartOrder.objects.create(
                    user=request.user,
                    price=total_amount,
                    full_name=full_name,
                    email=email,
                    phone=mobile,
                    address=address,
                    city=city,
                    state=state,
                    country=country,
                )

            # The keys of the cart are product ids, and _refresh_cart above dropped
            # every line whose product is gone.
            for product_id, item in cart_data.items():
                price = Decimal(item['price'])
                quantity = safe_int(item.get('qty'))
                CartOrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    invoice_no="INVOICE_NO-" + str(order.id),
                    item=item['title'],
                    image=item['image'],
                    quantity=quantity,
                    price=price,
                    total=price * quantity,
                )

            request.session['pending_order_oid'] = str(order.oid)

            return redirect("core:checkout", order.oid)

    return redirect("core:index")


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _vnpay_amount(order):
    """The order total the way VNPay writes it: VND x 100, as a string.

    The payment link and both replies from VNPay use this one function, so they
    cannot disagree on the rounding. VNPay's reply carries the amount as text and it
    can be missing, so the two checks compare text instead of calling int() (L-22).
    """
    return str(int(order.price) * 100)


def _log_wrong_vnpay_amount(view_name, order, vnpay_amount):
    """Write a warning for a VNPay reply whose amount is not the order total (L-34).

    The order stays unpaid, so this line is the only trace of the payment in
    Grocerly. Both amounts are in VNPay's form (VND x 100).
    """
    logger.warning(
        "%s: VNPay amount does not match order %s: VNPay sent %s, the order expects %s",
        view_name, order.oid, vnpay_amount, _vnpay_amount(order),
    )


@login_required
def vnpay_payment(request, oid):
    order = _get_checkout_order_or_none(request, oid)
    if not order:
        messages.warning(request, _("Order not found. Please start checkout again."))
        return redirect("core:checkout-info")

    # D-033: a cancelled order is closed, so it cannot be paid for any more.
    if order.product_status == 'cancelled':
        messages.warning(request, _("This order has been cancelled."))
        return redirect("core:dashboard")

    if order.paid_status:
        messages.info(request, _("This order has already been paid."))
        return redirect("core:payment-completed", order.oid)

    # Only the payment method is written here. The delivery status belongs to the
    # staff (useradmin change_order_status): this view used to write 'processing'
    # too, which pulled a shipped order back and got its stock deducted again (L-12).
    order.payment_method = 'online' # vnpay is an online method
    order.save(update_fields=['payment_method'])

    import time
    order_desc = f"Thanh_toan_don_hang_{order.oid}"
    txn_ref = f"{order.oid}-{int(time.time())}"

    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = _vnpay_amount(order)
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = txn_ref
    vnp.requestData['vnp_OrderInfo'] = order_desc
    vnp.requestData['vnp_OrderType'] = 'billpayment'
    vnp.requestData['vnp_Locale'] = 'vn'
    
    vnp.requestData['vnp_ReturnUrl'] = request.build_absolute_uri(reverse("core:vnpay_return"))
    vnp.requestData['vnp_IpAddr'] = get_client_ip(request)
    
    vn_tz = ZoneInfo('Asia/Ho_Chi_Minh')
    now = timezone.now().astimezone(vn_tz)
    vnp.requestData['vnp_CreateDate'] = now.strftime('%Y%m%d%H%M%S')
    
    vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET)
    
    return redirect(vnpay_payment_url)

def vnpay_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        txn_ref = inputData.get('vnp_TxnRef')
        order_id = txn_ref.split('-')[0] if txn_ref else None
        vnp_ResponseCode = inputData.get('vnp_ResponseCode')
        
        if vnp.validate_response(settings.VNPAY_HASH_SECRET):
            if vnp_ResponseCode == "00":
                try:
                    order = CartOrder.objects.get(oid=order_id)

                    # The order total can change after the link was made: another
                    # tab sends the shipping form again, or a coupon is applied.
                    # vnpay_ipn answers 04 for that; without this check the same
                    # payment would still mark the order paid here (L-22, D-040).
                    # The cart and the pending order stay, so the total can be paid.
                    if inputData.get('vnp_Amount') != _vnpay_amount(order):
                        # The money VNPay took is recorded nowhere else in Grocerly,
                        # so staff look for this line when the customer calls (L-34).
                        _log_wrong_vnpay_amount("vnpay_return", order, inputData.get('vnp_Amount'))
                        messages.error(request, _("The amount paid does not match this order, so it has not been confirmed. Please contact the store."))
                        return redirect("core:payment-failed")

                    order.paid_status = True
                    order.save()

                    if 'cart_data_obj' in request.session:
                        del request.session['cart_data_obj']
                        
                    pending_oid = request.session.get('pending_order_oid')
                    if pending_oid and str(order.oid) == str(pending_oid):
                        del request.session['pending_order_oid']
                        
                    messages.success(request, _("VNPay payment successful!"))
                    return redirect("core:payment-completed", order.oid)
                except CartOrder.DoesNotExist:
                    messages.error(request, _("This order does not exist."))
                    return redirect("core:index")
            else:
                messages.error(request, _("VNPay payment failed. Error code: %(code)s") % {"code": vnp_ResponseCode})
                return redirect("core:payment-failed")
        else:
            messages.error(request, _("Invalid security signature."))
            return redirect("core:payment-failed")
    return redirect("core:index")

@csrf_exempt
def vnpay_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        txn_ref = inputData.get('vnp_TxnRef')
        order_id = txn_ref.split('-')[0] if txn_ref else None
        amount = inputData.get('vnp_Amount')
        vnp_ResponseCode = inputData.get('vnp_ResponseCode')
        
        if vnp.validate_response(settings.VNPAY_HASH_SECRET):
            try:
                order = CartOrder.objects.get(oid=order_id)
                if amount != _vnpay_amount(order):
                    _log_wrong_vnpay_amount("vnpay_ipn", order, amount)
                    return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})
                    
                if order.paid_status:
                    return JsonResponse({'RspCode': '02', 'Message': 'Order already confirmed'})
                    
                if vnp_ResponseCode == '00':
                    order.paid_status = True
                    order.save()
                    return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    return JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
            except CartOrder.DoesNotExist:
                return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})
        else:
            return JsonResponse({'RspCode': '97', 'Message': 'Invalid signature'})
    return JsonResponse({'RspCode': '99', 'Message': 'Unknown error'})


@login_required
def place_cod_order(request, oid):
    if request.method != "POST":
        return redirect("core:checkout", oid)

    order = _get_checkout_order_or_none(request, oid)
    if not order:
        messages.warning(request, _("Order not found. Please start checkout again."))
        return redirect("core:checkout-info")

    # D-033: a cancelled order is closed, so it cannot be placed again.
    if order.product_status == 'cancelled':
        messages.warning(request, _("This order has been cancelled."))
        return redirect("core:dashboard")

    if order.paid_status:
        messages.info(request, _("This order has already been paid."))
        return redirect("core:payment-completed", order.oid)

    # As in vnpay_payment: the payment method only, never the delivery status (L-12).
    order.payment_method = 'cod'
    order.save(update_fields=['payment_method'])

    if 'cart_data_obj' in request.session:
        del request.session['cart_data_obj']

    messages.success(request, _("Order placed with Cash on Delivery."))
    return redirect("core:payment-completed", order.oid)


@login_required
def checkout(request, oid):
    order = _get_checkout_order_or_none(request, oid)
    if not order:
        messages.warning(request, _("Checkout session not found. Please continue from checkout info."))
        return redirect("core:checkout-info")

    order_items = CartOrderItem.objects.filter(order=order)

    # D-033: no payment page, and no coupon, for an order the staff has cancelled.
    if order.product_status == 'cancelled':
        messages.warning(request, _("This order has been cancelled."))
        return redirect("core:dashboard")

    if order.paid_status:
        messages.info(request, _("This order has already been paid."))
        return redirect("core:payment-completed", order.oid)

    if request.method == "POST":
        code = request.POST.get("code")
        coupon = Coupon.objects.filter(code=code, active=True).first()
        if coupon:
            if coupon in order.coupons.all():
                messages.warning(request, _("Coupon already activated"))
                return redirect("core:checkout", order.oid)
            else:
                discount = order.price * coupon.discount / 100
                order.coupons.add(coupon)
                order.price -= discount
                order.saved += discount
                order.save()
                messages.success(request, _("Coupon Activated"))
                return redirect("core:checkout", order.oid)
        else:
            messages.error(request, _("Coupon Does Not Exist"))

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'core/checkout.html', context)


@login_required
def payment_completed_view(request, oid):
    order = _get_checkout_order_or_none(request, oid)
    if not order:
        messages.warning(request, _("Order not found. Please start checkout again."))
        return redirect("core:checkout-info")

    # L-8: this page only displays the order. An online order becomes paid in
    # vnpay_return / vnpay_ipn, which check VNPay's signature first. Opening this
    # URL by hand must not confirm a payment that never happened - and must not
    # show "Payment Completed" for an order VNPay has not confirmed.
    if order.payment_method == 'online' and not order.paid_status:
        messages.warning(request, _("This order has not been paid yet. Please complete the payment."))
        return redirect("core:checkout", order.oid)

    if 'cart_data_obj' in request.session:
        del request.session['cart_data_obj']

    pending_oid = request.session.get('pending_order_oid')
    if pending_oid and str(order.oid) == str(pending_oid):
        del request.session['pending_order_oid']

    context = {
        'order': order,
    }
    return render(request, 'core/payment-completed.html', context)


@login_required
def payment_failed_view(request):
    pending_order = _get_pending_order_from_session(request)

    return render(request, 'core/payment-failed.html', {
        'pending_order': pending_order,
    })


# ======================== Dashboard ========================

@login_required
def customer_dashboard(request):
    orders_list = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    # Monthly order chart data: the customer's own orders only - counting every
    # order of the shop showed each customer how much the whole shop sells.
    orders = CartOrder.objects.filter(user=request.user).annotate(
        month=ExtractMonth("order_date")
    ).values("month").annotate(count=Count("id")).values("month", "count")
    month = []
    total_orders = []
    for i in orders:
        # MONTHS holds Django's translated month names ("Tháng 1" on /vi/);
        # calendar.month_name is always English.
        month.append(str(MONTHS[i["month"]]))
        total_orders.append(i["count"])

    # Handle new address creation
    if request.method == "POST":
        new_address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        Address.objects.create(
            user=request.user,
            address=new_address,
            mobile=mobile,
        )
        messages.success(request, _("Address Added Successfully."))
        return redirect("core:dashboard")

    user_profile = Profile.objects.get(user=request.user)

    context = {
        "user_profile": user_profile,
        "orders": orders,
        "orders_list": orders_list,
        "address": address,
        "month": month,
        "total_orders": total_orders,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def order_detail(request, oid):
    # By oid, as the checkout pages do: the old numeric id let anyone guess the next
    # order. An order that is not there, or belongs to another customer, is 404 (L-32).
    order = get_object_or_404(CartOrder, user=request.user, oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)

    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


# ======================== Wishlist ========================

@login_required
def wishlist_view(request):
    wishlist = wishlist_of(request.user)
    context = {
        "w": wishlist,
    }
    return render(request, "core/wishlist.html", context)

@require_POST
def add_to_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({"bool": False, "error": _("Please sign in to add products to your wishlist.")})

    # A page opened before staff deleted the product still shows its heart (L-28).
    product = Product.objects.filter(id=safe_int(request.POST.get('id'), 0)).first()
    if product is None:
        return JsonResponse({"bool": False, "error": _("This product is no longer available.")})

    wishlist_qs = Wishlist.objects.filter(product=product, user=request.user)

    if wishlist_qs.exists():
        wishlist_qs.delete()
        added = False
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product,
        )
        added = True
        
    total_wishlist = wishlist_of(request.user).count()
    context = {"bool": True, "added": added, "total_wishlist_items": total_wishlist}

    return JsonResponse(context)


@require_POST
def remove_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({"bool": False, "error": _("Please sign in to use your wishlist.")})

    pid = request.POST.get('id')
    try:
        wishlist_d = Wishlist.objects.get(id=pid, user=request.user)
        wishlist_d.delete()
    except Wishlist.DoesNotExist:
        pass

    wishlist = wishlist_of(request.user)
    total_wishlist = wishlist.count()

    context = {
        "bool": True,
        "w": wishlist,
    }
    wishlist_json = serializers.serialize('json', wishlist)
    t = render_to_string('core/async/wishlist-list.html', context, request=request)
    return JsonResponse({'data': t, 'w': wishlist_json, 'total_wishlist_items': total_wishlist})

# ======================== Static Pages & Contact ========================

def contact(request):
    return render(request, "core/contact.html")

@require_POST
def ajax_contact_form(request):
    # ContactForm checks the required boxes, the email and each length (L-50).
    form = ContactForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"data": {"bool": False, "errors": form.errors}}, status=400)

    form.save()
    data = {
        "bool": True,
        "message": _("Message Sent Successfully")
    }
    return JsonResponse({"data": data})

def about_us(request):
    return render(request, "core/about_us.html")

def purchase_guide(request):
    return render(request, "core/purchase_guide.html")

def privacy_policy(request):
    return render(request, "core/privacy_policy.html")

def terms_of_service(request):
    return render(request, "core/terms_of_service.html")

def coming_soon(request):
    return render(request, "core/coming-soon.html")