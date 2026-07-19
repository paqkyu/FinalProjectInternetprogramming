from django.contrib import admin
from .models import MembershipPlan, Category, Product, Subcategory, Review


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
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "name",
        "category__name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "subcategory",
        "brand",
        "price",
        "stock_quantity",
        "fitness_goal",
        "is_active",
        "membership_plan",
    )

    list_filter = (
        "category",
        "subcategory",
        "fitness_goal",
        "is_active",
        "membership_plan",
    )

    search_fields = (
        "name",
        "brand",
        "description",
    )

    list_editable = (
        "price",
        "stock_quantity",
        "is_active",
    )
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "updated_at",
    ]

    list_filter = [
        "rating",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "product__name",
        "user__username",
        "comment",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]