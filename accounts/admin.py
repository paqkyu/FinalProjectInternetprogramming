from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=(
        "user",
        "current_membership",
        "trainer_booking_allowed",
    )
    list_filter=(
        "current_membership",
    )
    search_fields=(
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )
    @admin.display(
        boolean=True,
        description="Can book trainer",
    )
    def trainer_booking_allowed(self, profile):
        return profile.can_book_trainer