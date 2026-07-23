from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from orders.emails import send_order_confirmation
from orders.models import Order, OrderItem
from orders.utils import calculate_shipping
from promotions.services import PromotionEngine

from .cart import Cart
from .forms import CheckoutForm
from .models import Category, Product, Wishlist
from accounts.models import Address

def home(request):
    categories = Category.objects.filter(
        is_active=True,
    ).order_by("name")

    featured_products = (
        Product.objects
        .filter(
            is_active=True,
            is_featured=True,
        )
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")[:8]
    )

    best_seller_products = (
        Product.objects
        .filter(
            is_active=True,
            is_best_seller=True,
        )
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")[:8]
    )

    wishlist_ids = set()

    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(
                user=request.user,
            ).values_list(
                "product_id",
                flat=True,
            )
        )

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "best_seller_products": best_seller_products,
        "wishlist_ids": wishlist_ids,
    }

    return render(
        request,
        "home.html",
        context,
    )

def product_list(request):
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")
    )

    category_slug = request.GET.get("category")

    if category_slug:
        products = products.filter(
            category__slug=category_slug,
            category__is_active=True,
        )

    paginator = Paginator(
        products,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(
        is_active=True,
    ).order_by("name")

    wishlist_ids = set()

    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(
                user=request.user,
            ).values_list(
                "product_id",
                flat=True,
            )
        )

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "wishlist_ids": wishlist_ids,
    }

    return render(
        request,
        "products/product-list.html",
        context,
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects
        .select_related("category")
        .prefetch_related("images"),
        slug=slug,
        is_active=True,
    )

    primary_image = (
        product.images
        .filter(is_primary=True)
        .first()
    )

    if primary_image is None:
        primary_image = product.images.first()

    related_products = (
        Product.objects
        .filter(
            category=product.category,
            is_active=True,
        )
        .exclude(id=product.id)
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")[:4]
    )

    wishlist_ids = set()

    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(
                user=request.user,
            ).values_list(
                "product_id",
                flat=True,
            )
        )

    context = {
        "product": product,
        "related_products": related_products,
        "primary_image": primary_image,
        "wishlist_ids": wishlist_ids,
    }

    return render(
        request,
        "products/product-detail.html",
        context,
    )

def product_search(request):
    query = request.GET.get(
        "q",
        "",
    ).strip()

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(
                short_description__icontains=query
            )
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()
    else:
        products = products.none()

    paginator = Paginator(
        products.order_by("-created_at"),
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    wishlist_ids = set()

    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(
                user=request.user,
            ).values_list(
                "product_id",
                flat=True,
            )
        )

    context = {
        "query": query,
        "page_obj": page_obj,
        "result_count": products.count(),
        "wishlist_ids": wishlist_ids,
    }

    return render(
        request,
        "products/search-results.html",
        context,
    )


@login_required
def wishlist(request):
    wishlist_products = (
        Product.objects
        .filter(
            wishlist_items__user=request.user,
            is_active=True,
        )
        .select_related("category")
        .prefetch_related("images")
        .order_by("-wishlist_items__created_at")
    )

    wishlist_ids = set(
        wishlist_products.values_list(
            "id",
            flat=True,
        )
    )

    context = {
        "wishlist_products": wishlist_products,
        "wishlist_ids": wishlist_ids,
    }

    return render(
        request,
        "products/wishlist.html",
        context,
    )


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    wishlist_item = (
        Wishlist.objects
        .filter(
            user=request.user,
            product=product,
        )
        .first()
    )

    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product,
        )

    next_url = request.POST.get(
        "next",
        "",
    )

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={
            request.get_host(),
        },
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect(
        "products:wishlist",
    )


def cart_detail(request):
    cart = Cart(request)

    context = {
        "cart": cart,
    }

    return render(
        request,
        "products/cart-detail.html",
        context,
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    quantity = request.POST.get(
        "quantity",
        1,
    )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)

    cart = Cart(request)

    cart.add(
        product=product,
        quantity=quantity,
    )

    next_url = request.POST.get("next", "")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect("products:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    quantity = request.POST.get(
        "quantity",
        1,
    )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)

    cart = Cart(request)

    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=True,
    )

    return redirect("products:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    cart = Cart(request)
    cart.remove(product)

    return redirect("products:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect("products:cart_detail")

    subtotal = cart.get_total_price()
    shipping_cost = calculate_shipping(subtotal)

    coupon_code = request.POST.get(
        "coupon_code",
        "",
    )

    promotion_result = PromotionEngine.evaluate(
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        user=request.user,
        coupon_code=coupon_code,
    )

    grand_total = promotion_result.grand_total

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        form_is_valid = form.is_valid()

        if (
                form_is_valid
            and not promotion_result.is_valid
        ):
            form.add_error(
            None,
            promotion_result.message,
        )

        if (
            form_is_valid
            and promotion_result.is_valid
        ):
            payment_value = form.cleaned_data[
            "payment_method"
        ]

        
            payment_method_map = {
                "bank_transfer": "BANK_TRANSFER",
                "BANK_TRANSFER": "BANK_TRANSFER",
                "promptpay": "PROMPTPAY",
                "PROMPTPAY": "PROMPTPAY",
                "cod": "COD",
                "COD": "COD",
            }

            payment_method = payment_method_map.get(
                payment_value,
                "BANK_TRANSFER",
            )

            full_address = " ".join(
                [
                    form.cleaned_data["address"],
                    form.cleaned_data["district"],
                    form.cleaned_data["province"],
                    form.cleaned_data["postal_code"],
                ]
            )

            try:
                with transaction.atomic():
                    locked_products = {}

                    for item in cart:
                        product = (
                            Product.objects
                            .select_for_update()
                            .get(
                                id=item["product"].id,
                                is_active=True,
                            )
                        )

                        quantity = item["quantity"]

                        if product.stock < quantity:
                            raise ValueError(
                                f"สินค้า {product.name} "
                                f"มีไม่เพียงพอ "
                                f"เหลือ {product.stock} ชิ้น"
                            )

                        locked_products[
                            product.id
                        ] = product

                    order = Order.objects.create(
                        user=request.user,
                        recipient_name=(
                            form.cleaned_data[
                                "full_name"
                            ]
                        ),
                        phone=form.cleaned_data[
                            "phone"
                        ],
                        address=full_address,
                        subtotal=subtotal,
                        shipping_fee=shipping_cost,
                        discount_amount=(
                            promotion_result.discount_amount
                        ),
                        shipping_discount=(
                                promotion_result.shipping_discount
                        ),
                        coupon_code=promotion_result.coupon_code,
                        promotion_data=promotion_result.as_snapshot(),
                        grand_total=grand_total,
                        payment_method=payment_method,
                        payment_status="PENDING",
                        order_status="NEW",
                    )

                    order_items = []

                    for item in cart:
                        product = locked_products[
                            item["product"].id
                        ]

                        quantity = item["quantity"]

                        product.stock -= quantity

                        product.save(
                            update_fields=[
                                "stock",
                            ]
                        )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=item["price"],
                            line_total=(
                                item["total_price"]
                            ),
                        )

                        order_items.append(
                            {
                                "name": product.name,
                                "sku": product.sku,
                                "quantity": quantity,
                                "price": str(
                                    item["price"]
                                ),
                                "total_price": str(
                                    item[
                                        "total_price"
                                    ]
                                ),
                            }
                        )

                    PromotionEngine.consume(
                        promotion_result
                    )


                    recipient_email = (
                        form.cleaned_data["email"]
                    )

                    
                    order_detail_url = (
                        request.build_absolute_uri(
                            f"/orders/"
                            f"{order.order_number}/"
                        )
                    )

                    transaction.on_commit(
                        lambda order_id=order.id,
                        email=recipient_email,
                        detail_url=order_detail_url:
                        send_order_confirmation(
                            order_id=order_id,
                            recipient_email=email,
                            order_detail_url=(
                                detail_url
                            ),
                        )
                    )

            except Product.DoesNotExist:
                form.add_error(
                    None,
                    (
                        "มีสินค้าบางรายการ"
                        "ไม่พร้อมจำหน่าย "
                        "กรุณาตรวจสอบตะกร้า"
                        "อีกครั้ง"
                    ),
                )

            except ValueError as error:
                form.add_error(
                    None,
                    str(error),
                )

            else:
                payment_labels = dict(
                    CheckoutForm.PAYMENT_CHOICES
                )

                request.session[
                    "last_order"
                ] = {
                    "order_number": (
                        order.order_number
                    ),
                    "customer": {
                        "full_name": (
                            form.cleaned_data[
                                "full_name"
                            ]
                        ),
                        "phone": (
                            form.cleaned_data[
                                "phone"
                            ]
                        ),
                        "email": (
                            form.cleaned_data[
                                "email"
                            ]
                        ),
                        "address": (
                            form.cleaned_data[
                                "address"
                            ]
                        ),
                        "district": (
                            form.cleaned_data[
                                "district"
                            ]
                        ),
                        "province": (
                            form.cleaned_data[
                                "province"
                            ]
                        ),
                        "postal_code": (
                            form.cleaned_data[
                                "postal_code"
                            ]
                        ),
                    },
                    "payment_method": (
                        payment_labels.get(
                            payment_value,
                            payment_value,
                        )
                    ),
                    "payment_method_code": (
                        payment_method
                    ),
                    "order_note": (
                        form.cleaned_data[
                            "order_note"
                        ]
                    ),
                    "items": order_items,
                    "subtotal": str(subtotal),
                    "shipping_cost": str(
                        shipping_cost
                    ),
                    "discount_amount": str(
                        promotion_result.discount_amount
                    ),
                    "shipping_discount": str(
                        promotion_result.shipping_discount
                    ),
                    "coupon_code": (
                        promotion_result.coupon_code
                    ),
                    "grand_total": str(
                         grand_total
                    ),
                }

                cart.clear()

                return redirect(
                    "products:order_success"
                )

    else:
        form = CheckoutForm()
    addresses = (
    Address.objects
    .filter(user=request.user)
    .order_by(
        "-is_default",
        "-updated_at",
    )
    )

    default_address = (
    addresses
    .filter(is_default=True)
    .first()
    )

    context = {
        "cart": cart,
        "form": form,
        "addresses": addresses,
        "default_address": default_address,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "discount_amount": (
            promotion_result.discount_amount
        ),
        "shipping_discount": (
            promotion_result.shipping_discount
        ),
        "coupon_code": coupon_code,
        "promotion_result": promotion_result,
        "grand_total": grand_total,
    }

    return render(
        request,
        "products/checkout.html",
        context,
    )


def order_success(request):
    order = request.session.get(
        "last_order"
    )

    if not order:
        return redirect(
            "products:product_list"
        )

    return render(
        request,
        "products/order-success.html",
        {
            "order": order,
        },
    )