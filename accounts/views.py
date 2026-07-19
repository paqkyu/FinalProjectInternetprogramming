from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from bookings.models import Booking, TrainerProfile
from catalog.models import MembershipPlan, Product, Review
from django.db.models import Count
from .forms import LoginForm, RegistrationForm, AccountUpdateForm
from django.contrib import messages
from .models import Profile
from catalog.forms import ProductForm
from cart.cart import Cart
from decimal import Decimal
User=get_user_model()
def is_staff_member(user):
    return(
        user.is_authenticated
        and (
            user.is_superuser or user.groups.filter(name="Staff").exists())
    )
def is_owner(user):
    return(
        user.is_authenticated
        and user.is_superuser
    )
#create your views here
def register(request):
    """Display and process the user registration form."""

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(user=user)
            login(request, user)

            return redirect("accounts:dashboard")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())

            return redirect("accounts:dashboard")
    else:
        form = LoginForm(request)

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@require_POST
def logout_view(request):

    logout(request)

    return redirect("core:home")


@login_required
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect("accounts:owner_dashboard")

    if is_staff_member(request.user):
        return redirect("accounts:staff_dashboard")

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
    )

    member_cart = Cart(request)
    cart_items = list(member_cart)

    cart_quantity = sum(
        item["quantity"]
        for item in cart_items
    )

    cart_total = sum(
        (
            item["total_price"]
            for item in cart_items
        ),
        Decimal("0.00"),
    )

    recent_reviews = (
        Review.objects.filter(
            user=request.user,
        )
        .select_related("product")
        .order_by("-updated_at")[:5]
    )

    total_user_reviews = Review.objects.filter(
        user=request.user,
    ).count()

    return render(
        request,
        "accounts/dashboard.html",
        {
            "profile": profile,
            "cart_items": cart_items,
            "cart_quantity": cart_quantity,
            "cart_total": cart_total,
            "recent_reviews": recent_reviews,
            "total_user_reviews": total_user_reviews,
        },
    )
@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    low_stock_threshold = 5

    physical_products = Product.objects.filter(
        is_active=True,
        membership_plan__isnull=True,
    )

    low_stock_products = (
        physical_products.filter(
            stock_quantity__lte=low_stock_threshold,
        )
        .select_related(
            "category",
            "subcategory",
        )
        .order_by(
            "stock_quantity",
            "name",
        )[:10]
    )

    recent_bookings = (
        Booking.objects.select_related(
            "member",
            "trainer",
            "trainer__user",
        )
        .order_by("-created_at")[:8]
    )

    recent_reviews = (
        Review.objects.select_related(
            "product",
            "user",
        )
        .order_by("-updated_at")[:6]
    )

    total_members = (
        Profile.objects.exclude(
            user__is_superuser=True,
        )
        .exclude(
            user__groups__name="Staff",
        )
        .distinct()
        .count()
    )

    total_staff = (
        User.objects.filter(
            groups__name="Staff",
        )
        .distinct()
        .count()
    )

    active_memberships = Profile.objects.filter(
        current_membership__isnull=False,
    ).count()

    membership_distribution = (
        Profile.objects.filter(
            current_membership__isnull=False,
        )
        .values(
            "current_membership__name",
            "current_membership__tier_order",
        )
        .annotate(
            total=Count("id"),
        )
        .order_by(
            "current_membership__tier_order",
        )
    )

    context = {
        "total_products": physical_products.count(),

        "low_stock_count": physical_products.filter(
            stock_quantity__lte=low_stock_threshold,
        ).count(),

        "out_of_stock_count": physical_products.filter(
            stock_quantity=0,
        ).count(),

        "total_members": total_members,
        "total_staff": total_staff,

        "active_trainers": TrainerProfile.objects.filter(
            is_available=True,
        ).count(),

        "pending_bookings": Booking.objects.filter(
            status=Booking.Status.PENDING,
        ).count(),

        "active_membership_plans": MembershipPlan.objects.filter(
            is_active=True,
        ).count(),

        "active_memberships": active_memberships,

        "total_reviews": Review.objects.count(),

        "low_stock_products": low_stock_products,
        "recent_bookings": recent_bookings,
        "recent_reviews": recent_reviews,
        "membership_distribution": membership_distribution,
    }

    return render(
        request,
        "accounts/owner_dashboard.html",
        context,
    )
@login_required
@user_passes_test(is_owner)
def owner_products(request):
    products = (
        Product.objects.filter(
            membership_plan__isnull=True,
        )
        .select_related(
            "category",
            "subcategory",
        )
        .order_by("name")
    )

    return render(
        request,
        "accounts/owner_products.html",
        {
            "products": products,
        },
    )


@login_required
@user_passes_test(is_owner)
def owner_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save()

            messages.success(
                request,
                f"{product.name} was added successfully.",
            )

            return redirect("accounts:owner_products")
    else:
        form = ProductForm()

    return render(
        request,
        "accounts/owner_product_form.html",
        {
            "form": form,
            "page_title": "Add Product",
            "submit_text": "Add Product",
        },
    )


@login_required
@user_passes_test(is_owner)
def owner_product_edit(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        membership_plan__isnull=True,
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            instance=product,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f"{product.name} was updated successfully.",
            )

            return redirect("accounts:owner_products")
    else:
        form = ProductForm(
            instance=product,
        )

    return render(
        request,
        "accounts/owner_product_form.html",
        {
            "form": form,
            "product": product,
            "page_title": f"Edit {product.name}",
            "submit_text": "Save Changes",
        },
    )
@login_required
def edit_profile(request):
    if request.method=="POST":
        form=AccountUpdateForm(
            request.POST,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your account details were updated successfully.",
            )
            return redirect("accounts:dashboard")
    else:
        form = AccountUpdateForm(
            instance=request.user,
        )
    return render(
        request,"accounts/profile_edit.html", {"form": form},
    )

@login_required
@user_passes_test(is_staff_member)
def staff_dashboard(request):
    base_bookings=Booking.objects.filter(
        trainer__user=request.user
    ).select_related(
        "member",
        "member__profile",
        "member__profile__current_membership",
        "trainer",
        "trainer__user",
    )
    active_bookings=base_bookings.exclude(
        status__in=[Booking.Status.COMPLETED, Booking.Status.CANCELLED,
        ],
    ).order_by(
        "starts_at",
    )
    booking_history = base_bookings.filter(
        status__in=[
            Booking.Status.COMPLETED,
            Booking.Status.CANCELLED,
        ],
    ).order_by(
        "-starts_at",
    )

    return render(
        request,
        "accounts/staff_dashboard.html",
        {"active_bookings":active_bookings, "booking_history":booking_history},
    )
@login_required
@user_passes_test(is_staff_member)
@require_POST
def update_booking_status(request, booking_id):
    booking=get_object_or_404(
        Booking,
        pk=booking_id,

        trainer__user=request.user,
    )
    new_status=request.POST.get("status","").strip().lower()

    allowed_transitions ={
        Booking.Status.PENDING: {
            Booking.Status.CONFIRMED,
            Booking.Status.CANCELLED,
        },
        Booking.Status.CONFIRMED: {
            Booking.Status.COMPLETED,
            Booking.Status.CANCELLED,
        },
        Booking.Status.COMPLETED: set(),
        Booking.Status.CANCELLED: set(),
    }
    permitted_statuses=allowed_transitions.get(
        booking.status,
        set(),
    )
    if new_status not in permitted_statuses:
        messages.error(
            request,
            "That booking status change is not allowed.",
        )
        return redirect("accounts:staff_dashboard")
    booking.status=new_status
    booking.save(update_fields=["status"])
    messages.success(
        request,
        "The booking status was updated successfully.",
    )
    return redirect("accounts:staff_dashboard")