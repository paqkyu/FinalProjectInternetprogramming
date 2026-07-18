from django.db import models
from django.conf import settings

# Create your models here.
class Profile(models.Model):
    MEMBERSHIP_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("elite", "Elite"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default="none",
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def can_book_trainer(self):
        return(self.current_membership is not None and self.current_membership.can_book_trainer)