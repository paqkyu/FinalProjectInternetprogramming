from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("products/",views.product_list,name="product_list",),
    path("products/<int:product_id>/",views.product_detail,name="product_detail",),
    path("products/<int:product_id>/reviews/submit",views.submit_review,name="submit_review"),
    path("products/<int:review_id>/delete/",views.delete_review,name="delete_review"),
]