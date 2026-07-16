from django.contrib import messages
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import (
    AccountPasswordChangeForm,
    LoginForm,
    RegisterForm,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("products:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("products:home")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("products:home")

    if request.method == "POST":
        form = LoginForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
            )

            if next_url:
                return redirect(next_url)

            return redirect("products:home")
    else:
        form = LoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        },
    )


def logout_view(request):
    if request.method == "POST":
        logout(request)

    return redirect("products:home")


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = AccountPasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว",
            )

            return redirect(
                "accounts:dashboard",
            )
    else:
        form = AccountPasswordChangeForm(
            user=request.user,
        )

    return render(
        request,
        "accounts/password_change.html",
        {
            "form": form,
        },
    )