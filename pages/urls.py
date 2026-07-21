from django.urls import path

from . import views


app_name = "pages"


urlpatterns = [
    path(
        "about/",
        views.about_view,
        name="about",
    ),
    path(
        "reviews/",
        views.reviews_view,
        name="reviews",
    ),
    path(
        "blog/",
        views.blog_list_view,
        name="blog_list",
    ),
    path(
        "blog/detail/",
        views.blog_detail_view,
        name="blog_detail",
    ),
    path(
        "contact/",
        views.contact_view,
        name="contact",
    ),
    path(
        "faq/",
        views.faq_view,
        name="faq",
    ),
    path(
        "shipping-policy/",
        views.shipping_policy_view,
        name="shipping_policy",
    ),
    path(
        "return-policy/",
        views.return_policy_view,
        name="return_policy",
    ),
    path(
        "privacy-policy/",
        views.privacy_policy_view,
        name="privacy_policy",
    ),
    path(
        "terms/",
        views.terms_view,
        name="terms",
    ),
]