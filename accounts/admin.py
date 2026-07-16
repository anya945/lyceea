from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "recipient_name",
        "user",
        "phone",
        "province",
        "postal_code",
        "is_default",
        "updated_at",
    )

    list_filter = (
        "is_default",
        "province",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "recipient_name",
        "phone",
        "address_line",
        "subdistrict",
        "district",
        "province",
        "postal_code",
        "user__username",
        "user__email",
    )

    ordering = (
        "-is_default",
        "-updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "เจ้าของที่อยู่",
            {
                "fields": (
                    "user",
                    "is_default",
                ),
            },
        ),
        (
            "ข้อมูลผู้รับ",
            {
                "fields": (
                    "recipient_name",
                    "phone",
                ),
            },
        ),
        (
            "รายละเอียดที่อยู่",
            {
                "fields": (
                    "address_line",
                    "subdistrict",
                    "district",
                    "province",
                    "postal_code",
                ),
            },
        ),
        (
            "ข้อมูลระบบ",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )