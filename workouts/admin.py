from django.contrib import admin
from .models import Exercise
# Register your models here.
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display=(
        "name",
        "body_part",
        "target",
        "equipment",
        "difficulty",
        "is_active",
    )
    list_filter=(
        "body_part",
        "target",
        "equipment",
        "difficulty",
        "is_active",
    )
    search_fields=(
        "name",
        "target",
        "equipment",
    )
    readonly_fields=(
        "external_id",
        "synced_at",
    )