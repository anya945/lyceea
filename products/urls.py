from django.urls import path

from . import views


app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),

    path(
        'wishlist/',
        views.wishlist,
        name='wishlist',
    ),
    path(
        'wishlist/toggle/<int:product_id>/',
        views.toggle_wishlist,
        name='toggle_wishlist',
    ),

path(
    'cart/',
    views.cart_detail,
    name='cart_detail',
),
path(
    'cart/add/<int:product_id>/',
    views.cart_add,
    name='cart_add',
),
path(
    'cart/update/<int:product_id>/',
    views.cart_update,
    name='cart_update',
),
path(
    'cart/remove/<int:product_id>/',
    views.cart_remove,
    name='cart_remove',
),

path(
    'checkout/',
    views.checkout,
    name='checkout',
),

path(
    'order-success/',
    views.order_success,
    name='order_success',
),

    path(
        'products/<slug:slug>/',
        views.product_detail,
        name='product_detail',
    ),
]