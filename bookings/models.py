from django.db import models
from django.conf import settings

# Create your models here.
class TrainerProfile(models.Model):
    user =models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )
    specialty=models.CharField(max_length=100)
    biography=models.TextField(blank=True)
    is_available=models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED ="confirmed", "Confirmed"
        COMPLETED="completed", "Completed"
        CANCELLED="cancelled", "Cancelled"
    member=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trainer_bookings",
    )
    trainer=models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    starts_at=models.DateTimeField()
    status=models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["starts_at"]
        constraints=[
            models.UniqueConstraint(
                fields=["trainer", "starts_at"],
                name="unique_trainer_booking_time",
            )
        ]
    def __str__(self):
        return(
            f"{self.member.username} with" f"{self.trainer} at {self.starts_at}"
        )
