from django.urls import path
from . import views
app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("staff/bookings/<int:booking_id>/status/", views.update_booking_status, name="update_booking_status",),
    path("owner/dashboard/",views.owner_dashboard, name="owner_dashboard"),
    path("owner/products/",views.owner_products,name="owner_products"),
    path("owner/products/add",views.owner_product_add,name="owner_product_add"),
    path("owner/products/<int:product_id>/edit/",views.owner_product_edit,name="owner_product_edit"),
]