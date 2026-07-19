from django import forms
from .models import Order

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 1,
            }
        ),
    )

    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput,
    )

    def __init__(
        self,
        *args,
        max_quantity=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if max_quantity is not None:
            self.fields["quantity"].max_value = (
                max_quantity
            )

            self.fields[
                "quantity"
            ].widget.attrs["max"] = max_quantity
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order

        fields = [
            "first_name",
            "last_name",
            "email",
            "address",
            "city",
            "postal_code",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }