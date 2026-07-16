from django import forms


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('bank_transfer', 'โอนเงินผ่านธนาคาร / PromptPay'),
        ('cod', 'เก็บเงินปลายทาง'),
    ]

    full_name = forms.CharField(
        label='ชื่อ–นามสกุล',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'ชื่อและนามสกุลผู้รับ',
                'autocomplete': 'name',
            }
        ),
    )

    phone = forms.CharField(
        label='เบอร์โทรศัพท์',
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': '08X-XXX-XXXX',
                'autocomplete': 'tel',
            }
        ),
    )

    email = forms.EmailField(
        label='อีเมล',
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'example@email.com',
                'autocomplete': 'email',
            }
        ),
    )

    address = forms.CharField(
        label='ที่อยู่',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'บ้านเลขที่ หมู่บ้าน ถนน ตำบล/แขวง',
                'rows': 4,
                'autocomplete': 'street-address',
            }
        ),
    )

    district = forms.CharField(
        label='อำเภอ / เขต',
        max_length=100,
    )

    province = forms.CharField(
        label='จังหวัด',
        max_length=100,
    )

    postal_code = forms.CharField(
        label='รหัสไปรษณีย์',
        max_length=10,
        widget=forms.TextInput(
            attrs={
                'inputmode': 'numeric',
                'autocomplete': 'postal-code',
            }
        ),
    )

    payment_method = forms.ChoiceField(
        label='วิธีชำระเงิน',
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
    )

    order_note = forms.CharField(
        label='หมายเหตุเพิ่มเติม',
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'ข้อมูลเพิ่มเติมสำหรับการจัดส่ง',
                'rows': 3,
            }
        ),
    )