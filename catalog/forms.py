from django import forms
from .models import Review, Product


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    ]

    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            },
        ),
    )

    class Meta:
        model = Review

        fields = [
            "rating",
            "comment",
        ]

        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Share your experience with this product."
                    ),
                },
            ),
        }
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = [
            "name",
            "category",
            "subcategory",
            "description",
            "brand",
            "fitness_goal",
            "price",
            "stock_quantity",
            "image_url",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"},
            ),
            "category": forms.Select(
                attrs={"class": "form-select"},
            ),
            "subcategory": forms.Select(
                attrs={"class": "form-select"},
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                },
            ),
            "brand": forms.TextInput(
                attrs={"class": "form-control"},
            ),
            "fitness_goal": forms.Select(
                attrs={"class": "form-select"},
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                },
            ),
            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                },
            ),
            "image_url": forms.URLInput(
                attrs={"class": "form-control"},
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"},
            ),
        }