from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import (
    DISCOUNT_TYPE_CHOICES,
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_NONE,
    DISCOUNT_TYPE_PERCENT,
    PROMOTION_TYPE_CHOICES,
    PROMOTION_TYPE_COUPON,
    PROMOTION_TYPE_FREE_SHIPPING,
)


class Promotion(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="ชื่อโปรโมชั่น",
    )

    promotion_type = models.CharField(
        max_length=30,
        choices=PROMOTION_TYPE_CHOICES,
        verbose_name="ประเภทโปรโมชั่น",
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="รหัสคูปอง",
        help_text=(
            "กรอกเฉพาะโปรโมชั่นประเภทคูปอง "
            "เช่น WELCOME10"
        ),
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_TYPE_PERCENT,
        verbose_name="รูปแบบส่วนลด",
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="มูลค่าส่วนลด",
    )

    minimum_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="ยอดซื้อขั้นต่ำ",
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="ส่วนลดสูงสุด",
    )

    starts_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="วันเริ่มใช้งาน",
    )

    ends_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="วันสิ้นสุด",
    )

    usage_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="จำนวนสิทธิ์ทั้งหมด",
    )

    used_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="ใช้ไปแล้ว",
    )

    priority = models.PositiveIntegerField(
        default=100,
        verbose_name="ลำดับความสำคัญ",
        help_text="ตัวเลขน้อยมีความสำคัญสูงกว่า",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="เปิดใช้งาน",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "priority",
            "-created_at",
        ]
        verbose_name = "โปรโมชั่น"
        verbose_name_plural = "โปรโมชั่น"

    def __str__(self):
        if self.code:
            return f"{self.name} ({self.code})"

        return self.name

    def clean(self):
        errors = {}

        if (
            self.promotion_type == PROMOTION_TYPE_COUPON
            and not self.code
        ):
            errors["code"] = (
                "โปรโมชั่นประเภทคูปองต้องระบุรหัสคูปอง"
            )

        if (
            self.promotion_type != PROMOTION_TYPE_COUPON
            and self.code
        ):
            errors["code"] = (
                "รหัสคูปองใช้ได้เฉพาะโปรโมชั่นประเภทคูปอง"
            )

        if (
            self.promotion_type
            == PROMOTION_TYPE_FREE_SHIPPING
        ):
            self.discount_type = DISCOUNT_TYPE_NONE
            self.discount_value = Decimal("0")

        if (
            self.discount_type
            == DISCOUNT_TYPE_PERCENT
            and (
                self.discount_value <= 0
                or self.discount_value > 100
            )
        ):
            errors["discount_value"] = (
                "ส่วนลดเปอร์เซ็นต์ต้องมากกว่า 0 "
                "และไม่เกิน 100"
            )

        if (
            self.discount_type == DISCOUNT_TYPE_FIXED
            and self.discount_value <= 0
        ):
            errors["discount_value"] = (
                "ส่วนลดแบบจำนวนเงินต้องมากกว่า 0"
            )

        if (
            self.starts_at
            and self.ends_at
            and self.starts_at >= self.ends_at
        ):
            errors["ends_at"] = (
                "วันสิ้นสุดต้องอยู่หลังวันเริ่มใช้งาน"
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()

        self.full_clean()

        super().save(*args, **kwargs)

    def is_available(self, now=None):
        now = now or timezone.now()

        if not self.is_active:
            return False

        if self.starts_at and now < self.starts_at:
            return False

        if self.ends_at and now > self.ends_at:
            return False

        if (
            self.usage_limit is not None
            and self.used_count >= self.usage_limit
        ):
            return False

        return True