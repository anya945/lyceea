from decimal import Decimal


FREE_SHIPPING_MINIMUM = Decimal("1000.00")
STANDARD_SHIPPING_FEE = Decimal("60.00")


def calculate_shipping(subtotal):
    """
    คำนวณค่าจัดส่ง

    - สั่งซื้อครบ 1,000 บาท ส่งฟรี
    - ต่ำกว่า 1,000 บาท คิดค่าจัดส่ง 60 บาท
    """

    subtotal = Decimal(subtotal)

    if subtotal >= FREE_SHIPPING_MINIMUM:
        return Decimal("0.00")

    return STANDARD_SHIPPING_FEE