from django.db import transaction

from .models import Order


@transaction.atomic
def restore_order_stock(order: Order):
    """
    คืน Stock ของสินค้าทั้งหมดใน Order
    ใช้เมื่อ Order ถูกยกเลิก
    """

    if order.stock_restored:
        return

    for item in order.items.select_related("product"):
        product = item.product

        product.stock += item.quantity

        product.save(
            update_fields=["stock"]
        )

    order.stock_restored = True

    order.save(
        update_fields=["stock_restored"]
    )