import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order


logger = logging.getLogger(__name__)


def send_order_confirmation(
    order_id,
    recipient_email,
    order_detail_url="",
):
    try:
        order = (
            Order.objects
            .prefetch_related("items__product")
            .get(pk=order_id)
        )

        context = {
            "order": order,
            "order_detail_url": order_detail_url,
        }

        subject = (
            f"ยืนยันคำสั่งซื้อ {order.order_number} | Lyceea"
        )

        text_body = render_to_string(
            "emails/order_confirmation.txt",
            context,
        )

        html_body = render_to_string(
            "emails/order_confirmation.html",
            context,
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[recipient_email],
        )

        email.attach_alternative(
            html_body,
            "text/html",
        )

        email.send()

    except Exception:
        logger.exception(
            "ไม่สามารถส่งอีเมลยืนยันคำสั่งซื้อ order_id=%s",
            order_id,
        )