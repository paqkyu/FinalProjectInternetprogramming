from django.contrib import admin
from .models import Booking, TrainerProfile
# Register your models here.
@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display=(
        "user",
        "specialty",
        "is_available",
    )
    list_filter=(
        "is_available",
        "specialty",
    )
    search_fields=(
        "user__username",
        "user__first_name",
        "user__last_name",
        "specialty",
    )
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display=(
        "member",
        "trainer",
        "starts_at",
        "status",
    )
    list_filter=(
        "status",
        "starts_at",
    )
    search_fields=(
        "member__username",
        "member__first_name",
        "member__last_name",
        "trainer__user__username",
    )