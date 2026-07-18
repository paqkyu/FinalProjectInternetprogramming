from django.db import models


class MembershipPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    tier_order=models.PositiveSmallIntegerField(
        unique=True,
        help_text="Basic = 1, Premium = 2, Elite = 3",
    )
    # Basic will be False.
    # Premium and Elite will be True.
    can_book_trainer = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering=["tier_order"]
    def __str__(self):
        return self.name