from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )
    sku = models.CharField(max_length=50, unique=True)

    short_description = models.CharField(
        max_length=255,
        blank=True
    )
    description = models.TextField(blank=True)

    seo_title = models.CharField(
        max_length=60,
        blank=True,
        help_text=(
            "ชื่อที่แสดงบน Google ไม่เกิน 60 ตัวอักษร "
            "หากเว้นว่าง ระบบจะใช้ชื่อสินค้า"
        ),
    )

    meta_description = models.CharField(
        max_length=155,
        blank=True,
        help_text=(
            "คำอธิบายสำหรับผลการค้นหา Google "
            "ไม่เกิน 155 ตัวอักษร"
        ),
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
        "products:product_detail",
        kwargs={"slug": self.slug},
    )

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f'{self.product.name} - Image {self.id}'
    
class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product",
                ],
                name="unique_user_wishlist_product",
            ),
        ]

        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.product.name}"
        )    