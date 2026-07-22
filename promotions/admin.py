from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "promotion_type",
        "code",
        "discount_summary",
        "minimum_subtotal",
        "starts_at",
        "ends_at",
        "usage_status",
        "priority",
        "is_active",
    )

    list_filter = (
        "promotion_type",
        "discount_type",
        "is_active",
        "starts_at",
        "ends_at",
    )

    search_fields = (
        "name",
        "code",
    )

    readonly_fields = (
        "used_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "priority",
        "-created_at",
    )

    fieldsets = (
        (
            "ข้อมูลโปรโมชั่น",
            {
                "fields": (
                    "name",
                    "promotion_type",
                    "code",
                    "is_active",
                    "priority",
                )
            },
        ),
        (
            "ส่วนลดและเงื่อนไข",
            {
                "fields": (
                    "discount_type",
                    "discount_value",
                    "minimum_subtotal",
                    "maximum_discount",
                )
            },
        ),
        (
            "ระยะเวลาและจำนวนสิทธิ์",
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                    "usage_limit",
                    "used_count",
                )
            },
        ),
        (
            "ข้อมูลระบบ",
            {
                "classes": (
                    "collapse",
                ),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(
        description="ส่วนลด",
    )
    def discount_summary(self, obj):
        if obj.promotion_type == "FREE_SHIPPING":
            return "ส่งฟรี"

        if obj.discount_type == "PERCENT":
            return f"{obj.discount_value}%"

        if obj.discount_type == "FIXED":
            return f"฿{obj.discount_value}"

        return "-"

    @admin.display(
        description="จำนวนใช้งาน",
    )
    def usage_status(self, obj):
        if obj.usage_limit is None:
            return f"{obj.used_count} / ไม่จำกัด"

        return (
            f"{obj.used_count} / "
            f"{obj.usage_limit}"
        )