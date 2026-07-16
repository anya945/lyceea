from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_SHIPPED,
)
from orders.models import Order


@login_required
def dashboard_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    latest_order = orders.first()

    status_summary = (
        orders.values("order_status")
        .annotate(total=Count("id"))
    )

    status_map = {
        item["order_status"]: item["total"]
        for item in status_summary
    }

    context = {
        "total_orders": orders.count(),
        "latest_order": latest_order,
        "recent_orders": orders[:5],
        "processing_count": status_map.get(
            ORDER_STATUS_PROCESSING,
            0,
        ),
        "shipped_count": status_map.get(
            ORDER_STATUS_SHIPPED,
            0,
        ),
        "completed_count": status_map.get(
            ORDER_STATUS_COMPLETED,
            0,
        ),
    }

    return render(
        request,
        "accounts/dashboard.html",
        context,
    )