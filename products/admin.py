from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    Product,
    ProductImage,
    Wishlist,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    fields = (
        'image',
        'alt_text',
        'is_primary',
        'sort_order',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    list_editable = (
        'is_active',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_thumbnail',
        'name',
        'category',
        'sku',
        'price',
        'discount_price',
        'stock_status',
        'is_featured',
        'is_best_seller',
        'is_active',
    )

    list_filter = (
        'category',
        'is_featured',
        'is_best_seller',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'sku',
        'short_description',
        'description',
        'seo_title',
        'meta_description',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    list_editable = (
        'is_featured',
        'is_best_seller',
        'is_active',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    ordering = (
        '-created_at',
    )

    list_per_page = 20

    inlines = [
        ProductImageInline,
    ]

    fieldsets = (
        (
            'ข้อมูลหลักของสินค้า',
            {
                'fields': (
                    'category',
                    'name',
                    'slug',
                    'sku',
                )
            },
        ),
        (
            'รายละเอียดสินค้า',
            {
                'fields': (
                    'short_description',
                    'description',
                )
            },
        ),
        
                (
            'SEO และข้อมูลสำหรับ Google',
            {
                'fields': (
                    'seo_title',
                    'meta_description',
                ),
                'description': (
                    'SEO Title ไม่เกิน 60 ตัวอักษร และ '
                    'Meta Description ไม่เกิน 155 ตัวอักษร'
                ),
            },
        ),
        
        (
            'ราคาและสต็อก',
            {
                'fields': (
                    'price',
                    'discount_price',
                    'stock',
                )
            },
        ),
        (
            'สถานะสินค้า',
            {
                'fields': (
                    'is_featured',
                    'is_best_seller',
                    'is_active',
                )
            },
        ),
        (
            'ข้อมูลระบบ',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                ),
                'classes': (
                    'collapse',
                ),
            },
        ),
    )

    @admin.display(description='รูป')
    def product_thumbnail(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()

        if primary_image is None:
            primary_image = obj.images.first()

        if primary_image and primary_image.image:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit: cover; border-radius: 6px;">',
                primary_image.image.url,
            )

        return 'ไม่มีรูป'

    @admin.display(description='สถานะสต็อก', ordering='stock')
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html(
                '<strong style="color: #c62828;">หมด</strong>'
            )

        if obj.stock <= 5:
            return format_html(
                '<strong style="color: #ef6c00;">เหลือน้อย ({})</strong>',
                obj.stock,
            )

        return format_html(
            '<strong style="color: #2e7d32;">พร้อมขาย ({})</strong>',
            obj.stock,
        )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'product',
        'alt_text',
        'is_primary',
        'sort_order',
    )

    list_filter = (
        'is_primary',
    )

    search_fields = (
        'product__name',
        'alt_text',
    )

    list_editable = (
        'is_primary',
        'sort_order',
    )

    @admin.display(description='รูป')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit: cover; border-radius: 6px;">',
                obj.image.url,
            )

        return 'ไม่มีรูป'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "product__name",
        "product__sku",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )