from django.urls import path
from . import views
app_name="workouts"

urlpatterns=[
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercises/<int:exercise_id>/",views.exercise_detail,name="exercise_detail"),
    path("exercises/<int:exercise_id>/gif/", views.exercise_gif, name="exercise_gif"),
]