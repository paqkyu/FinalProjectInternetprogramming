from django.shortcuts import render, redirect
from catalog.models import Product
from django.contrib import messages
from .forms import ContactForm

# Create your views here.
def home(request):
    membership_products=(
        Product.objects.filter(
            is_active=True,
            membership_plan__isnull=False,
            membership_plan__is_active=True,
        )
        .select_related("membership_plan")
        .order_by("membership_plan__tier_order")
    )
    featured_products=(
        Product.objects.filter(
            is_active=True,
            membership_plan__isnull=True,
        )
        .select_related(
            "category",
            "subcategory",
        )
        .order_by("-created_at")[:3]
    )
    return render(request, "core/home.html", {"membership_products": membership_products, "featured_products": featured_products},)
def about(request):
    return render(request, "core/about.html")
def contact(request):
    initial_data = {}

    if request.user.is_authenticated:
        initial_data = {
            "name": (
                request.user.get_full_name()
                or request.user.username
            ),
            "email": request.user.email,
        }

    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            contact_message = form.save(
                commit=False,
            )

            if request.user.is_authenticated:
                contact_message.user = request.user

            contact_message.save()

            messages.success(
                request,
                (
                    "Your message was sent successfully. "
                    "We will respond as soon as possible."
                ),
            )

            return redirect("core:contact")
    else:
        form = ContactForm(
            initial=initial_data,
        )

    return render(
        request,
        "core/contact.html",
        {
            "form": form,
        },
    )