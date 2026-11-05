from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils.dates import MONTHS
from django.utils.translation import gettext as _

from core.models import CartOrder, CartOrderItem, Product, Category, ProductReview, ProductImage, STATUS_CHOICES
from userauths.models import Profile, User
from useradmin.forms import AddProductForm, StaffPasswordChangeForm, StaffProfileForm
from useradmin.decorators import admin_required

import datetime

def revenue_orders():
    """Đơn được tính vào doanh thu: đã thanh toán và không bị hủy (UC-26, D-033).

    Đơn VNPay đã trả tiền rồi bị hủy vẫn giữ paid_status=True, vì tiền hoàn cho
    khách ngoài hệ thống. Chỉ lọc theo paid_status thì vẫn cộng cả tiền đơn đó.
    """
    return CartOrder.objects.filter(paid_status=True).exclude(product_status="cancelled")

@admin_required
def dashboard(request):
    revenue = revenue_orders().aggregate(price=Sum("price"))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.all()

    this_month = datetime.datetime.now().month
    monthly_revenue = revenue_orders().filter(order_date__month=this_month).aggregate(price=Sum("price"))

    from django.db.models.functions import ExtractMonth

    revenue_data = revenue_orders().annotate(
        month=ExtractMonth("order_date")
    ).values("month").annotate(total_revenue=Sum("price")).values("month", "total_revenue").order_by("month")
    
    rev_month = []
    rev_total = []
    for i in revenue_data:
        if i["month"]:
            # Django's month names, in the language of the page (vi: "Tháng 11").
            rev_month.append(str(MONTHS[i["month"]]))
            rev_total.append(float(i["total_revenue"]))

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
        "rev_month": rev_month,
        "rev_total": rev_total,
    }
    return render(request, "useradmin/dashboard.html", context)

@admin_required
def products(request):
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    
    context = {
        "all_products": all_products,
        "all_categories": all_categories,
    }
    return render(request, "useradmin/products.html", context)

@admin_required
def update_stock(request):
    if request.method == "POST":
        pid = request.POST.get("pid")
        stock_count = request.POST.get("stock_count")
        try:
            product = Product.objects.get(p_id=pid)
            product.stock_count = int(stock_count)
            product.save()
            return JsonResponse({"bool": True, "stock_count": product.stock_count})
        except Exception as e:
            return JsonResponse({"bool": False, "error": str(e)})
    return JsonResponse({"bool": False})

@admin_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.product_status = 'published'
            new_form.save()
            form.save_m2m()
            
            # Handle additional images
            additional_images = request.FILES.getlist('additional_images')
            import uuid
            for img in additional_images:
                if img.size > 0:
                    ext = img.name.split('.')[-1] if '.' in img.name else 'jpg'
                    img.name = f"{uuid.uuid4().hex[:10]}.{ext}"
                    ProductImage.objects.create(product=new_form, image=img)
                
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm()
    context = {
        'form':form
    }
    return render(request, "useradmin/add-products.html", context)

@admin_required
def edit_product(request, pid):
    product = get_object_or_404(Product, p_id=pid)

    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.save()
            form.save_m2m()
            
            # Handle additional images
            additional_images = request.FILES.getlist('additional_images')
            import uuid
            for img in additional_images:
                if img.size > 0:
                    ext = img.name.split('.')[-1] if '.' in img.name else 'jpg'
                    img.name = f"{uuid.uuid4().hex[:10]}.{ext}"
                    ProductImage.objects.create(product=new_form, image=img)
                
            # Handle deletion of existing images
            delete_images = request.POST.getlist('delete_images')
            # Lọc bỏ các giá trị rỗng/không hợp lệ để tránh ValueError (ví dụ: 'id' expected a number but got '')
            delete_images = [img_id for img_id in delete_images if str(img_id).strip().isdigit()]
            if delete_images:
                ProductImage.objects.filter(id__in=delete_images, product=new_form).delete()
                
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm(instance=product)
    context = {
        'form':form,
        'product':product,
    }
    return render(request, "useradmin/edit-products.html", context)

@admin_required
@require_POST
def delete_product(request, pid):
    # POST only: a link opened from another site still carries the staff's cookie (L-29).
    product = get_object_or_404(Product, p_id=pid)
    product.delete()
    return redirect("useradmin:dashboard-products")

@admin_required
def orders(request):
    orders = CartOrder.objects.all()
    context = {
        'orders':orders,
    }
    return render(request, "useradmin/orders.html", context)

@admin_required
def order_detail(request, oid):
    # Gọi đơn bằng oid như trang của khách (L-32, D-047), không bằng khóa chính số.
    # Mã đơn không có thì trả 404, không để .get() ném lỗi 500 (L-44).
    order = get_object_or_404(CartOrder, oid=oid)
    order_items = CartOrderItem.objects.filter(order=order)
    context = {
        'order':order,
        'order_items':order_items,
        'status_choices': STATUS_CHOICES,  # nhãn của ô chọn trạng thái
    }
    return render(request, "useradmin/order_detail.html", context)

# Các trạng thái mà đơn được phép chuyển sang, tính từ trạng thái đang có. Đơn đi
# tới từng bước một (D-032), và đơn chưa giao xong thì hủy được (D-033).
# 'delivered' và 'cancelled' không có trong bảng vì đó là hai điểm dừng.
NEXT_STATUS = {
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered", "cancelled"},
}

@admin_required
def change_order_status(request, oid):
    # Mã đơn không có (link cũ, gõ sai) thì trả 404, không để .get() ném lỗi 500 (L-39).
    order = get_object_or_404(CartOrder, oid=oid)
    if request.method == "POST":
        status = request.POST.get("status")

        # Chỉ nhận bốn trạng thái của STATUS_CHOICES. Ô chọn có sẵn một dòng nhắc
        # không phải trạng thái, bấm Save mà chưa chọn gì thì không đổi gì cả.
        if status not in dict(STATUS_CHOICES):
            messages.error(request, _("Please choose an order status."))
            return redirect("useradmin:order_detail", order.oid)

        # Đơn chỉ đi tới, mỗi lần một bước, hoặc bị hủy khi chưa giao xong (SRS
        # §6.1, UC-20; D-032, D-033). Lùi, nhảy cóc hay gửi lại trạng thái đang có
        # đều bị từ chối. Đơn đã giao và đơn đã hủy không có trong bảng nên nhận về
        # tập rỗng, tức là không đổi được nữa.
        if status not in NEXT_STATUS.get(order.product_status, set()):
            # The translated labels of STATUS_CHOICES, not the stored values (D-033).
            messages.error(request, _('This order cannot go from "%(current)s" to "%(new)s".') % {
                "current": order.get_product_status_display(),
                "new": dict(STATUS_CHOICES)[status],
            })
            return redirect("useradmin:order_detail", order.oid)

        # Hàng rời kho thì trừ tồn kho. Qua được điều kiện trên nghĩa là đơn đang ở
        # 'processing'; đơn đã 'shipped' thì không quay lại nhánh này được nữa.
        # Hủy đơn không có nhánh cộng lại: đồ tươi đi giao rồi quay về chưa chắc
        # còn bán được, nên nhân viên tự chỉnh tồn kho ở trang sản phẩm (D-033).
        # Khóa ngoại đọc được cả sản phẩm đã xóa mềm: hàng đã rời kho thì vẫn phải
        # trừ. Dòng không có khóa ngoại thì bỏ qua, không đoán theo tên (L-25, D-045).
        if status == 'shipped':
            order_items = CartOrderItem.objects.filter(order=order).select_related("product")
            for item in order_items:
                product = item.product
                if product and product.stock_count is not None:
                    product.stock_count -= item.quantity
                    if product.stock_count < 0:
                        product.stock_count = 0
                    product.save()
                    
        # Nếu chuyển sang trạng thái delivered và là đơn hàng COD, đánh dấu đã thanh toán
        if status == 'delivered' and order.payment_method == 'cod':
            order.paid_status = True
                    
        messages.success(request, _("Order status changed to %(status)s.") % {"status": dict(STATUS_CHOICES)[status]})
        order.product_status = status
        order.save()
    
    return redirect("useradmin:order_detail", order.oid)

@admin_required
def shop_page(request):
    products = Product.objects.filter(user=request.user)
    revenue = revenue_orders().aggregate(price=Sum("price"))
    total_sales = CartOrderItem.objects.filter(order__in=revenue_orders()).aggregate(qty=Sum("quantity"))

    context = {
        'products':products,
        'revenue':revenue,
        'total_sales':total_sales,
    }
    return render(request, "useradmin/shop_page.html", context)

@admin_required
def reviews(request):
    reviews = ProductReview.objects.all()
    context = {
        'reviews':reviews,
    }
    return render(request, "useradmin/reviews.html", context)

@admin_required
def settings(request):
    profile = Profile.objects.get(user=request.user)

    # StaffProfileForm checks each box against its column and saves an empty box as
    # empty, so neither a long value nor the word "None" reaches the database
    # (L-45, L-50, D-055).
    form = StaffProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Profile Updated Successfully."))
        return redirect("useradmin:settings")

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, "useradmin/settings.html", context)

@admin_required
def change_password(request):
    # Django's PasswordChangeForm, as on the customer's page: the old password is
    # checked, the new one goes through AUTH_PASSWORD_VALIDATORS (L-51, D-055).
    form = StaffPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # Changing the password ends every session of the user unless this one is
        # updated; without it the staff was signed out right after saving (L-51).
        update_session_auth_hash(request, user)
        messages.success(request, _("Your password has been changed."))
        return redirect("useradmin:change_password")

    return render(request, "useradmin/change_password.html", {"form": form})
