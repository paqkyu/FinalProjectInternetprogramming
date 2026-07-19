from .cart import Cart
def cart_summary(request):
    cart = Cart(request)

    return {
        "navbar_cart_count": len(cart),
    }