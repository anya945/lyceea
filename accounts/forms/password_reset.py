import email.policy

from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader


class _EmailMultiAlternativesNoWrap(EmailMultiAlternatives):
    """
    EmailMultiAlternatives ที่ override message() เพื่อใช้ policy แบบ 8bit
    แทนค่าดีฟอลต์ (email.policy.default) ที่เลือก quoted-printable สำหรับ UTF-8

    ผลลัพธ์: URL ที่ยาวใน body จะไม่ถูกตัดกลางด้วย "=" อีกต่อไป
    """

    # policy นี้บังคับ CTE เป็น 7bit/8bit (ขึ้นอยู่กับเนื้อหา)
    # และไม่ wrap บรรทัดที่ < 998 ตัวอักษร (ตาม RFC 5322)
    _no_wrap_policy = email.policy.SMTP.clone(
        cte_type="8bit",
        max_line_length=998,
    )

    def message(self, *, policy=None):
        return super().message(policy=self._no_wrap_policy)


class PlainPasswordResetForm(PasswordResetForm):
    """
    PasswordResetForm ที่แก้ปัญหา URL ลิงก์ reset password ถูกตัดกลางบรรทัด
    ด้วย "=" (quoted-printable soft line break) ซึ่งเกิดจาก email.policy.default
    ของ Django 6 ที่ใช้ quoted-printable encoding สำหรับ UTF-8 body โดยอัตโนมัติ
    """

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = _EmailMultiAlternativesNoWrap(
            subject,
            body,
            from_email,
            [to_email],
        )

        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name,
                context,
            )
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()