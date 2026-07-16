from django import forms
from django.contrib.auth.models import User


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label="ชื่อผู้ใช้งาน",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ชื่อผู้ใช้งาน",
                "autocomplete": "username",
            }
        ),
        error_messages={
            "required": "กรุณากรอกชื่อผู้ใช้งาน",
            "unique": "ชื่อผู้ใช้งานนี้ถูกใช้งานแล้ว",
        },
    )

    first_name = forms.CharField(
        label="ชื่อ",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ชื่อ",
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        label="นามสกุล",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "นามสกุล",
                "autocomplete": "family-name",
            }
        ),
    )

    email = forms.EmailField(
        label="อีเมล",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@email.com",
                "autocomplete": "email",
            }
        ),
        error_messages={
            "required": "กรุณากรอกอีเมล",
            "invalid": "กรุณากรอกอีเมลให้ถูกต้อง",
        },
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        email_exists = (
            User.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if email_exists:
            raise forms.ValidationError(
                "อีเมลนี้ถูกใช้งานโดยบัญชีอื่นแล้ว"
            )

        return email