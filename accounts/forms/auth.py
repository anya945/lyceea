from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
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
        },
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

    password1 = forms.CharField(
        label="รหัสผ่าน",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "รหัสผ่าน",
                "autocomplete": "new-password",
            }
        ),
        error_messages={
            "required": "กรุณากรอกรหัสผ่าน",
        },
    )

    password2 = forms.CharField(
        label="ยืนยันรหัสผ่าน",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "ยืนยันรหัสผ่าน",
                "autocomplete": "new-password",
            }
        ),
        error_messages={
            "required": "กรุณายืนยันรหัสผ่าน",
        },
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email,
        ).exists():
            raise forms.ValidationError(
                "อีเมลนี้ถูกใช้งานแล้ว กรุณาใช้อีเมลอื่น"
            )

        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="ชื่อผู้ใช้งาน",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ชื่อผู้ใช้งาน",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
        error_messages={
            "required": "กรุณากรอกชื่อผู้ใช้งาน",
        },
    )

    password = forms.CharField(
        label="รหัสผ่าน",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "รหัสผ่าน",
                "autocomplete": "current-password",
            }
        ),
        error_messages={
            "required": "กรุณากรอกรหัสผ่าน",
        },
    )

    error_messages = {
        "invalid_login": (
            "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง "
            "กรุณาตรวจสอบแล้วลองอีกครั้ง"
        ),
        "inactive": "บัญชีนี้ถูกระงับการใช้งาน",
    }


class AccountPasswordChangeForm(DjangoPasswordChangeForm):
    error_messages = {
        "password_incorrect": (
            "รหัสผ่านปัจจุบันไม่ถูกต้อง "
            "กรุณาตรวจสอบแล้วลองอีกครั้ง"
        ),
        "password_mismatch": (
            "รหัสผ่านใหม่ทั้งสองช่องไม่ตรงกัน"
        ),
    }

    old_password = forms.CharField(
        label="รหัสผ่านปัจจุบัน",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "กรอกรหัสผ่านปัจจุบัน",
                "autocomplete": "current-password",
                "autofocus": True,
            }
        ),
        error_messages={
            "required": "กรุณากรอกรหัสผ่านปัจจุบัน",
        },
    )

    new_password1 = forms.CharField(
        label="รหัสผ่านใหม่",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "กรอกรหัสผ่านใหม่",
                "autocomplete": "new-password",
            }
        ),
        error_messages={
            "required": "กรุณากรอกรหัสผ่านใหม่",
        },
    )

    new_password2 = forms.CharField(
        label="ยืนยันรหัสผ่านใหม่",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "กรอกรหัสผ่านใหม่อีกครั้ง",
                "autocomplete": "new-password",
            }
        ),
        error_messages={
            "required": "กรุณายืนยันรหัสผ่านใหม่",
        },
    )