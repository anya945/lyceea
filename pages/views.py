from django.shortcuts import render


def about_view(request):
    return render(
        request,
        "pages/about.html",
    )


def reviews_view(request):
    return render(
        request,
        "pages/reviews.html",
    )


def blog_list_view(request):
    return render(
        request,
        "pages/blog_list.html",
    )


def blog_detail_view(request):
    return render(
        request,
        "pages/blog_detail.html",
    )


def contact_view(request):
    return render(
        request,
        "pages/contact.html",
    )


def faq_view(request):
    return render(
        request,
        "pages/faq.html",
    )


def shipping_policy_view(request):
    return render(
        request,
        "pages/shipping_policy.html",
    )


def return_policy_view(request):
    return render(
        request,
        "pages/return_policy.html",
    )


def privacy_policy_view(request):
    return render(
        request,
        "pages/privacy_policy.html",
    )


def terms_view(request):
    return render(
        request,
        "pages/terms.html",
    )