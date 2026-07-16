from django.conf import settings
from django.db import models


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    recipient_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=20,
    )

    address_line = models.TextField()

    subdistrict = models.CharField(
        max_length=100,
        blank=True,
    )

    district = models.CharField(
        max_length=100,
    )

    province = models.CharField(
        max_length=100,
    )

    postal_code = models.CharField(
        max_length=10,
    )

    is_default = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-is_default",
            "-updated_at",
        ]

    def __str__(self):
        return (
            f"{self.recipient_name} - "
            f"{self.province}"
        )

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True,
            ).exclude(
                pk=self.pk,
            ).update(
                is_default=False,
            )

        super().save(*args, **kwargs)