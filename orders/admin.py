from django.contrib import admin
from django.contrib import messages
from django.db import transaction

from .models import Order, OrderItem
from .services import restore_order_stock
from .constants import ORDER_STATUS_CANCELLED

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "quantity",
        "unit_price",
        "line_total",
    )
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "recipient_name",
        "phone",
        "grand_total",
        "payment_method",
        "payment_status",
        "order_status",
        "stock_restored",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "payment_status",
        "order_status",
        "stock_restored",
        "created_at",
    )

    search_fields = (
        "order_number",
        "recipient_name",
        "phone",
        "address",
    )

    readonly_fields = (
        "order_number",
        "subtotal",
        "shipping_fee",
        "grand_total",
        "stock_restored",
        "created_at",
        "updated_at",
    )

    inlines = [OrderItemInline]

    ordering = ("-created_at",)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous_status = None

        if change:
            previous_order = Order.objects.select_for_update().get(
                pk=obj.pk
            )
            previous_status = previous_order.order_status

        super().save_model(
            request,
            obj,
            form,
            change,
        )

        if (
            obj.order_status == ORDER_STATUS_CANCELLED
            and previous_status != ORDER_STATUS_CANCELLED
        ):
            restore_order_stock(obj)

            self.message_user(
                request,
                "ยกเลิกคำสั่งซื้อและคืน Stock เรียบร้อยแล้ว",
                level=messages.SUCCESS,
            )