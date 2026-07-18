from django.db import models

# Create your models here.
class Exercise(models.Model):
    external_id=models.CharField(
        max_length=20,
        unique=True,
    )
    name=models.CharField(
        max_length=200,
    )
    body_part=models.CharField(
        max_length=100,
        blank=True,
    )
    target=models.CharField(
        max_length=100,
        blank=True,
    )
    equipment=models.CharField(
        max_length=100,
        blank=True,
    )
    difficulty=models.CharField(
        max_length=50,
        blank=True,
    )
    mechanic=models.CharField(
        max_length=50,
        blank=True,
    )
    force=models.CharField(
        max_length=50,
        blank=True,
    )
    description=models.TextField(
        blank=True,
    )
    instructions=models.JSONField(
        default=list,
        blank=True,
    )
    secondary_muscles=models.JSONField(
        default=list,
        blank=True,
    )
    gif_url=models.URLField(
        max_length=500,
        blank=True,
    )
    recommended_sets=models.CharField(
        max_length=30,
        blank=True,
    )
    recommended_reps=models.CharField(
        max_length=30,
        blank=True,
    )
    calories_per_minute=models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active=models.BooleanField(
        default=True,
    )
    synced_at=models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        ordering=["name"]
    def __str__(self):
        return self.name