from .address import (
    address_create_view,
    address_delete_view,
    address_list_view,
    address_set_default_view,
    address_update_view,
)
from .auth import (
    login_view,
    logout_view,
    password_change_view,
    register_view,
)
from .dashboard import dashboard_view
from .profile import profile_edit_view, profile_view


__all__ = [
    "address_create_view",
    "address_delete_view",
    "address_list_view",
    "address_set_default_view",
    "address_update_view",
    "dashboard_view",
    "login_view",
    "logout_view",
    "password_change_view",
    "profile_edit_view",
    "profile_view",
    "register_view",
]