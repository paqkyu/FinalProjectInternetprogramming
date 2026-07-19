from django.shortcuts import get_object_or_404, render
from decimal import Decimal, InvalidOperation
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Category, Product, Review
from .forms import ReviewForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from cart.forms import CartAddProductForm

# Create your views here.
def product_list(request):
    products = Product.objects.filter(
        is_active=True,
        membership_plan__isnull=True,
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
    categories= Category.objects.exclude(
        name__iexact="Memberships",
    ).order_by("name")
    context = {
        "products": products,
        "categories": categories,
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
@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_active=True,
    )

    existing_review = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()

    form = ReviewForm(
        request.POST,
        instance=existing_review,
    )

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    review = form.save(
        commit=False,
    )

    review.product = product
    review.user = request.user
    review.save()

    rating_data = product.reviews.aggregate(
        average=Avg("rating"),
    )

    average_rating = rating_data["average"] or 0
    review_count = product.reviews.count()

    review_html = render_to_string(
        "catalog/partials/review_card.html",
        {
            "review": review,
        },
        request=request,
    )

    return JsonResponse(
        {
            "success": True,
            "review_id": review.id,
            "review_html": review_html,
            "average_rating": round(
                float(average_rating),
                1,
            ),
            "review_count": review_count,
        },
    )


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        pk=review_id,
        user=request.user,
    )

    product = review.product
    review.delete()

    rating_data = product.reviews.aggregate(
        average=Avg("rating"),
    )

    average_rating = rating_data["average"] or 0
    review_count = product.reviews.count()

    return JsonResponse(
        {
            "success": True,
            "average_rating": round(
                float(average_rating),
                1,
            ),
            "review_count": review_count,
        },
    )