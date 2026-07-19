from django.db import models
from django.core.exceptions import ValidationError

class MembershipPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    tier_order=models.PositiveSmallIntegerField(
        unique=True,
        help_text="Basic = 1, Premium = 2, Elite = 3",
    )
    can_book_trainer = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering=["tier_order"]
    def __str__(self):
        return self.name
class Category(models.Model):
    name=models.CharField(
        max_length=100,
        unique=True,
    )
    description=models.TextField(
        blank=True
    )
    class Meta:
        verbose_name_plural="Categories"
        ordering=["name"]
    def __str__(self):
        return self.name
class Subcategory(models.Model):
    category=models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )
    name=models.CharField(
        max_length=100,
    )
    class Meta:
        verbose_name_plural="Subcategories"
        ordering=["category__name", "name"]
        
        constraints=[
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_subcategory_per_category",
            ),
        ]
    def __str__(self):
        return f"{self.category.name} - {self.name}"
class Product(models.Model):
    FITNESS_GOAL_CHOICES=[
        ("strength", "Strength"),
        ("cardio", "Cardio"),
        ("weight_lost", "Weight Loss"),
        ("flexibility", "Flexibility"),
        ("recovery", "Recovery"),
        ("general", "General Fitness"),
    ]
    name=models.CharField(
        max_length=150,
    )
    category=models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    subcategory=models.ForeignKey(
        Subcategory,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    membership_plan = models.OneToOneField(
    MembershipPlan,
    on_delete=models.PROTECT,
    related_name="catalog_product",
    null=True,
    blank=True,
)
    description=models.TextField()
    brand=models.CharField(
        max_length=100,
        blank=True,
    )
    fitness_goal = models.CharField(
        max_length=30,
        choices=FITNESS_GOAL_CHOICES,
        default="general",
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    stock_quantity = models.PositiveIntegerField(
        default=0,
    )

    image_url = models.URLField(
        max_length=500,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def clean(self):
        errors={}
        if(
            self.subcategory
            and self.category_id
            and self.subcategory.category_id != self.category_id
        ):
            errors["subcategory"]=(
                "The selected subcategory does not belong "
                "to the selected category."
            )
        if (
            self.membership_plan
            and self.price != self.membership_plan.price
        ):
            errors["price"]=(
                "A membership product's price must match "
                "the member ship plan price"
            )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name

    @property
    def is_membership_product(self):
        return self.membership_plan_id is not None


    @property
    def in_stock(self):
        return (
            self.is_membership_product
        or self.stock_quantity > 0
        )
    @property
    def average_rating(self):
        result = self.reviews.aggregate(
            average=models.Avg("rating"),
        )

        return result["average"] or 0

    @property
    def review_count(self):
        return self.reviews.count()
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(
        max_length=2000,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="one_review_per_user_per_product",
            ),
            models.CheckConstraint(
                check=models.Q(
                    rating__gte=1,
                    rating__lte=5,
                ),
                name="review_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.product.name} - "
            f"{self.rating}/5"
        )