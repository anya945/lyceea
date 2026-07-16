from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .constants import (
    PAYMENT_METHOD_COD,
    PAYMENT_STATUS_PAID,
    PAYMENT_STATUS_PENDING,
)
from .forms import PaymentSlipForm
from .models import Order


@login_required
def order_list_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(
        Order.objects
        .select_related("user")
        .prefetch_related("items__product"),
        order_number=order_number,
        user=request.user,
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
        },
    )


@login_required
def payment_view(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user,
    )

    if order.payment_method == PAYMENT_METHOD_COD:
        messages.info(
            request,
            "คำสั่งซื้อนี้เลือกชำระเงินปลายทาง "
            "จึงไม่ต้องอัปโหลดสลิป",
        )

        return redirect(
            "orders:order_detail",
            order_number=order.order_number,
        )

    if request.method == "POST":
        form = PaymentSlipForm(
            request.POST,
            request.FILES,
            instance=order,
        )

        if form.is_valid():
            payment = form.save(commit=False)

            payment.payment_status = PAYMENT_STATUS_PENDING
            payment.payment_submitted_at = timezone.now()

            payment.save(
                update_fields=[
                    "payment_slip",
                    "payment_status",
                    "payment_submitted_at",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "ส่งหลักฐานการชำระเงินเรียบร้อยแล้ว "
                "กรุณารอเจ้าหน้าที่ตรวจสอบ",
            )

            return redirect(
                "orders:order_detail",
                order_number=order.order_number,
            )
    else:
        form = PaymentSlipForm(
            instance=order,
        )

    context = {
        "order": order,
        "form": form,
        "is_paid": (
            order.payment_status == PAYMENT_STATUS_PAID
        ),
    }

    return render(
        request,
        "orders/payment.html",
        context,
    )