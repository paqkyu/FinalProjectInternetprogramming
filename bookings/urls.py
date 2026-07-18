from django.urls import path
from . import views
app_name ="bookings"
urlpatterns = [
    path("trainers/",views.trainer_list,name="trainer_list",),
    path("trainers/<int:trainer_id>/",views.trainer_detail,name="trainer_detail",),
    path("my-bookings/",views.my_bookings,name="my_bookings",),
    path("my-bookings/<int:booking_id>/cancel/",views.cancel_booking,name="cancel_booking",),
]