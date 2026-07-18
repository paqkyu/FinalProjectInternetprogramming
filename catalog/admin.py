from django.contrib import admin

from .models import MembershipPlan


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "tier_order",
        "can_book_trainer",
        "is_active",
    )

    list_filter = (
        "can_book_trainer",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "tier_order",
    )