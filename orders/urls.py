from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path(
        "",
        views.order_list_view,
        name="order_list",
    ),
    path(
        "<str:order_number>/payment/",
        views.payment_view,
        name="payment",
    ),
    path(
        "<str:order_number>/",
        views.order_detail_view,
        name="order_detail",
    ),
]