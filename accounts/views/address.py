from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm
from accounts.models import Address


@login_required
def address_list_view(request):
    addresses = Address.objects.filter(
        user=request.user,
    )

    context = {
        "addresses": addresses,
    }

    return render(
        request,
        "accounts/address_list.html",
        context,
    )


@login_required
def address_create_view(request):
    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            has_address = Address.objects.filter(
                user=request.user,
            ).exists()

            if not has_address:
                address.is_default = True

            address.save()

            messages.success(
                request,
                "เพิ่มที่อยู่เรียบร้อยแล้ว",
            )

            return redirect(
                "accounts:address_list",
            )
    else:
        form = AddressForm()

    context = {
        "form": form,
        "page_title": "เพิ่มที่อยู่",
        "submit_label": "บันทึกที่อยู่",
    }

    return render(
        request,
        "accounts/address_form.html",
        context,
    )


@login_required
def address_update_view(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    if request.method == "POST":
        form = AddressForm(
            request.POST,
            instance=address,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "แก้ไขที่อยู่เรียบร้อยแล้ว",
            )

            return redirect(
                "accounts:address_list",
            )
    else:
        form = AddressForm(
            instance=address,
        )

    context = {
        "form": form,
        "address": address,
        "page_title": "แก้ไขที่อยู่",
        "submit_label": "บันทึกการแก้ไข",
    }

    return render(
        request,
        "accounts/address_form.html",
        context,
    )


@login_required
@require_POST
@transaction.atomic
def address_delete_view(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    was_default = address.is_default
    address.delete()

    if was_default:
        next_address = (
            Address.objects
            .filter(user=request.user)
            .order_by("-updated_at")
            .first()
        )

        if next_address:
            next_address.is_default = True
            next_address.save(
                update_fields=[
                    "is_default",
                    "updated_at",
                ],
            )

    messages.success(
        request,
        "ลบที่อยู่เรียบร้อยแล้ว",
    )

    return redirect(
        "accounts:address_list",
    )
@login_required
@require_POST
@transaction.atomic
def address_set_default_view(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    if address.is_default:
        messages.info(
            request,
            "ที่อยู่นี้เป็นที่อยู่หลักอยู่แล้ว",
        )

        return redirect(
            "accounts:address_list",
        )

    Address.objects.filter(
        user=request.user,
        is_default=True,
    ).update(
        is_default=False,
    )

    address.is_default = True
    address.save(
        update_fields=[
            "is_default",
            "updated_at",
        ],
    )

    messages.success(
        request,
        "ตั้งเป็นที่อยู่หลักเรียบร้อยแล้ว",
    )

    return redirect(
        "accounts:address_list",
    )