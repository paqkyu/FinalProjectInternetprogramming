from django.db import models
from django.conf import settings

# Create your models here.
class ContactMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="contact_messages",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=150,
    )

    message = models.TextField(
        max_length=3000,
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.name}"