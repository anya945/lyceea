from datetime import date
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageOps

from products.models import Product

from .constants import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_CONFIRMED,
    ORDER_STATUS_NEW,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_SHIPPED,
    PAYMENT_METHOD_BANK_TRANSFER,
    PAYMENT_METHOD_COD,
    PAYMENT_METHOD_PROMPTPAY,
    PAYMENT_STATUS_FAILED,
    PAYMENT_STATUS_PAID,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_REFUNDED,
)


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        (
            PAYMENT_METHOD_BANK_TRANSFER,
            "โอนผ่านธนาคาร",
        ),
        (
            PAYMENT_METHOD_PROMPTPAY,
            "พร้อมเพย์",
        ),
        (
            PAYMENT_METHOD_COD,
            "เก็บเงินปลายทาง",
        ),
    ]

    PAYMENT_STATUS_CHOICES = [
        (
            PAYMENT_STATUS_PENDING,
            "รอตรวจสอบการชำระเงิน",
        ),
        (
            PAYMENT_STATUS_PAID,
            "ชำระเงินแล้ว",
        ),
        (
            PAYMENT_STATUS_FAILED,
            "ชำระเงินไม่สำเร็จ",
        ),
        (
            PAYMENT_STATUS_REFUNDED,
            "คืนเงินแล้ว",
        ),
    ]

    ORDER_STATUS_CHOICES = [
        (
            ORDER_STATUS_NEW,
            "คำสั่งซื้อใหม่",
        ),
        (
            ORDER_STATUS_CONFIRMED,
            "ยืนยันคำสั่งซื้อแล้ว",
        ),
        (
            ORDER_STATUS_PROCESSING,
            "กำลังเตรียมสินค้า",
        ),
        (
            ORDER_STATUS_SHIPPED,
            "จัดส่งแล้ว",
        ),
        (
            ORDER_STATUS_COMPLETED,
            "สำเร็จ",
        ),
        (
            ORDER_STATUS_CANCELLED,
            "ยกเลิก",
        ),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
    )

    recipient_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=20,
    )

    address = models.TextField()

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    shipping_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    shipping_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    promotion_data = models.JSONField(
        blank=True,
        default=dict,
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_BANK_TRANSFER,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING,
    )

    payment_slip = models.ImageField(
        upload_to="payment_slips/%Y/%m/",
        blank=True,
        null=True,
    )

    payment_submitted_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default=ORDER_STATUS_NEW,
    )

    stock_restored = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def _resize_payment_slip(self):
        if not self.payment_slip:
            return

        if getattr(self.payment_slip, "_committed", True):
            return

        self.payment_slip.file.seek(0)

        with Image.open(self.payment_slip.file) as image:
            image = ImageOps.exif_transpose(image)

            maximum_dimension = 1600

            if (
                image.width > maximum_dimension
                or image.height > maximum_dimension
            ):
                image.thumbnail(
                    (
                        maximum_dimension,
                        maximum_dimension,
                    ),
                    Image.Resampling.LANCZOS,
                )

            if image.mode in ("RGBA", "LA"):
                background = Image.new(
                    "RGB",
                    image.size,
                    "white",
                )

                alpha_channel = image.getchannel("A")

                background.paste(
                    image.convert("RGB"),
                    mask=alpha_channel,
                )

                image = background

            elif image.mode != "RGB":
                image = image.convert("RGB")

            output = BytesIO()
            target_size = 5 * 1024 * 1024
            quality_levels = (85, 75, 65)

            for quality in quality_levels:
                output.seek(0)
                output.truncate(0)

                image.save(
                    output,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                )

                if output.tell() <= target_size:
                    break

            original_name = Path(
                self.payment_slip.name
            ).stem

            resized_name = f"{original_name}.jpg"

            self.payment_slip = ContentFile(
                output.getvalue(),
                name=resized_name,
            )

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = date.today().strftime("%Y%m%d")

            last_order = (
                Order.objects
                .filter(
                    order_number__startswith=f"ELY{today}",
                )
                .order_by("-order_number")
                .first()
            )

            if last_order:
                last_number = int(
                    last_order.order_number[-4:]
                )
                running = last_number + 1
            else:
                running = 1

            self.order_number = (
                f"ELY{today}{running:04d}"
            )

        self._resize_payment_slip()

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"{self.product.name} "
            f"x {self.quantity}"
        )