from django.shortcuts import get_object_or_404, render
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.
def product_list(request):
    products = Product.objects.filter(
        is_active=True,
    ).select_related(
        "category",
        "subcategory",
    )

    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    fitness_goal = request.GET.get("goal", "").strip()
    minimum_price = request.GET.get("min_price", "").strip()
    maximum_price = request.GET.get("max_price", "").strip()
    in_stock = request.GET.get("in_stock", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(brand__icontains=search_query)
        )

    if category_id:
        products = products.filter(
            category_id=category_id,
        )

    valid_goals = {
        value
        for value, label in Product.FITNESS_GOAL_CHOICES
    }

    if fitness_goal in valid_goals:
        products = products.filter(
            fitness_goal=fitness_goal,
        )

    try:
        if minimum_price:
            products = products.filter(
                price__gte=Decimal(minimum_price),
            )
    except InvalidOperation:
        minimum_price = ""

    try:
        if maximum_price:
            products = products.filter(
                price__lte=Decimal(maximum_price),
            )
    except InvalidOperation:
        maximum_price = ""

    if in_stock == "1":
        products = products.filter(
            stock_quantity__gt=0,
        )

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "fitness_goals": Product.FITNESS_GOAL_CHOICES,
        "search_query": search_query,
        "selected_category": category_id,
        "selected_goal": fitness_goal,
        "minimum_price": minimum_price,
        "maximum_price": maximum_price,
        "in_stock": in_stock,
    }

    return render(
        request,
        "catalog/product_list.html",
        context,
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related(
            "category",
            "subcategory",
        ),
        pk=product_id,
        is_active=True,
    )
    if product.membership_plan_id:
        maximum_quantity=1
    else:
        maximum_quantity=product.stock_quantity
    cart_form=CartAddProductForm(
        max_quantity=maximum_quantity,
    )

    return render(
        request,
        "catalog/product_detail.html",
        {
        "product": product,
        "cart_form": cart_form, 
        },
    )