from decimal import Decimal
from django.conf import settings
from catalog.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get(
            settings.CART_SESSION_ID
        )

        if cart is None:
            cart = self.session[
                settings.CART_SESSION_ID
            ] = {}

        self.cart = cart

    def add(
        self,
        product,
        quantity=1,
        override_quantity=False,
    ):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
            }

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = (
                self.cart[product_id]["quantity"]
                + quantity
            )

        # Prevent the cart quantity exceeding available stock.
        if product.membership_plan_id:
            available_quantity=1
        else:
            available_quantity = product.stock_quantity
        new_quantity=min(new_quantity,available_quantity)

        if new_quantity > 0:
            self.cart[product_id]["quantity"] = (
                new_quantity
            )
        else:
            self.cart.pop(product_id, None)

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True,
        ).select_related(
            "category",
            "subcategory",
            "membership_plan",
        )

        cart = self.cart.copy()

        for product in products:
            item=self.cart[str(product.id)].copy()
            item["product"]=product
            item["price"]=product.price
            item["total_price"]=(
                product.price * item["quantity"]
            )

            yield item

    def __len__(self):
        return sum(
            item["quantity"]
            for item in self.cart.values()
        )

    def get_total_price(self):
        return sum(
            (
                item["total_price"]
                for item in self
            ),
            Decimal("0.00"),
        )

    def clear(self):
        self.session.pop(
            settings.CART_SESSION_ID,
            None,
        )

        self.save()