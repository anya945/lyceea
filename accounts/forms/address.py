from django import forms

from accounts.models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address

        fields = (
            "recipient_name",
            "phone",
            "address_line",
            "subdistrict",
            "district",
            "province",
            "postal_code",
            "is_default",
        )

        labels = {
            "recipient_name": "ชื่อผู้รับ",
            "phone": "เบอร์โทรศัพท์",
            "address_line": "รายละเอียดที่อยู่",
            "subdistrict": "แขวง / ตำบล",
            "district": "เขต / อำเภอ",
            "province": "จังหวัด",
            "postal_code": "รหัสไปรษณีย์",
            "is_default": "ตั้งเป็นที่อยู่หลัก",
        }

        widgets = {
            "recipient_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ชื่อและนามสกุลผู้รับ",
                    "autocomplete": "name",
                },
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "เช่น 0812345678",
                    "autocomplete": "tel",
                    "inputmode": "tel",
                },
            ),
            "address_line": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "บ้านเลขที่ หมู่บ้าน อาคาร "
                        "ถนน และรายละเอียดเพิ่มเติม"
                    ),
                    "rows": 4,
                    "autocomplete": "street-address",
                },
            ),
            "subdistrict": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "แขวง / ตำบล",
                },
            ),
            "district": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "เขต / อำเภอ",
                },
            ),
            "province": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "จังหวัด",
                },
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "รหัสไปรษณีย์",
                    "autocomplete": "postal-code",
                    "inputmode": "numeric",
                    "maxlength": "10",
                },
            ),
            "is_default": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                },
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        normalized_phone = (
            phone
            .replace(" ", "")
            .replace("-", "")
        )

        if not normalized_phone.isdigit():
            raise forms.ValidationError(
                "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลข"
            )

        if not 9 <= len(normalized_phone) <= 10:
            raise forms.ValidationError(
                "เบอร์โทรศัพท์ต้องมี 9–10 หลัก"
            )

        return normalized_phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"].strip()

        if not postal_code.isdigit():
            raise forms.ValidationError(
                "กรุณากรอกรหัสไปรษณีย์เป็นตัวเลข"
            )

        if len(postal_code) != 5:
            raise forms.ValidationError(
                "รหัสไปรษณีย์ต้องมี 5 หลัก"
            )

        return postal_code