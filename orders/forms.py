from django import forms

from .models import Order


class PaymentSlipForm(forms.ModelForm):
    payment_slip = forms.ImageField(
        label="หลักฐานการชำระเงิน",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
        error_messages={
            "required": "กรุณาเลือกไฟล์สลิปการชำระเงิน",
            "invalid_image": "ไฟล์ที่เลือกไม่ใช่รูปภาพที่ถูกต้อง",
        },
    )

    class Meta:
        model = Order
        fields = (
            "payment_slip",
        )

    def clean_payment_slip(self):
        payment_slip = self.cleaned_data["payment_slip"]

        allowed_content_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        content_type = getattr(
            payment_slip,
            "content_type",
            "",
        )

        if content_type not in allowed_content_types:
            raise forms.ValidationError(
                "รองรับเฉพาะไฟล์ JPG, PNG และ WEBP"
            )

        maximum_size = 5 * 1024 * 1024

        if payment_slip.size > maximum_size:
            raise forms.ValidationError(
                "ไฟล์ต้องมีขนาดไม่เกิน 5 MB"
            )

        return payment_slip