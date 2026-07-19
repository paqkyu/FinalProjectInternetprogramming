from django.db import models
from decimal import Decimal
from django.conf import settings
from catalog.models import Product, MembershipPlan

# Create your models here.
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING= "pending", "Pending Payment"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    address = models.CharField(
        max_length=255,
    )

    city = models.CharField(
        max_length=100,
    )

    postal_code = models.CharField(
        max_length=20,
    )

    paid = models.BooleanField(
        default=False,
    )
    stripe_checkout_session_id=models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    paid_at=models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def get_total_price(self):
        return sum(
            (
                item.get_cost()
                for item in self.items.all()
            ),
            Decimal("0.00"),
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    membership_plan = models.ForeignKey(
    MembershipPlan,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="purchased_order_items",
)

    product_name = models.CharField(
        max_length=150,
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def get_cost(self):
        return self.price * self.quantity
