from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import ProfileUpdateForm


@login_required
def profile_view(request):
    return render(
        request,
        "accounts/profile.html",
        {
            "user": request.user,
        },
    )


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(
            instance=request.user,
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
        },
    )