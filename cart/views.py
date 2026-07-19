from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm, CheckoutForm
from django.db import transaction
from .models import Order, OrderItem
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from decimal import Decimal
from accounts.models import Profile
import logging
logger = logging.getLogger(__name__)
stripe.api_key=getattr(
    settings,
    "STRIPE_SECRET_KEY",
    "",
).strip()

# Create your views here.
def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        "cart/detail.html",
        {"cart": cart},
    )

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product.objects.select_related("membership_plan"),
        pk=product_id,
        is_active=True,
    )

    if product.membership_plan_id:
        for item in cart:
            existing_product = item["product"]

            if (
                existing_product.membership_plan_id
                and existing_product.id != product.id
            ):
                messages.error(
                    request,
                    "Only one membership plan can be purchased at a time.",
                )
                return redirect(
                    "catalog:product_detail",
                    product_id=product.id,
                )

        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(
                user=request.user,
            )

            current_plan = profile.current_membership
            selected_plan = product.membership_plan

            if (
                current_plan
                and selected_plan.tier_order
                <= current_plan.tier_order
            ):
                messages.error(
                    request,
                    "Please select a membership above your current plan.",
                )
                return redirect(
                    "catalog:product_detail",
                    product_id=product.id,
                )

        maximum_quantity = 1

    else:
        if product.stock_quantity == 0:
            messages.error(
                request,
                "This product is currently out of stock.",
            )
            return redirect(
                "catalog:product_detail",
                product_id=product.id,
            )

        maximum_quantity = product.stock_quantity

    form = CartAddProductForm(
        request.POST,
        max_quantity=maximum_quantity,
    )

    if form.is_valid():
        cart.add(
            product=product,
            quantity=form.cleaned_data["quantity"],
            override_quantity=form.cleaned_data["override"],
        )

        messages.success(
            request,
            f"{product.name} was added to your cart.",
        )
    else:
        messages.error(
            request,
            "Please enter a valid quantity.",
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    cart.remove(product)

    messages.success(
        request,
        f"{product.name} was removed from your cart.",
    )

    return redirect("cart:cart_detail")
@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        messages.warning(
            request,
            "Your cart is empty.",
        )
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    locked_products = {}

                    for item in cart_items:
                        product = (
                            Product.objects
                            .select_for_update()
                            .get(
                                pk=item["product"].id,
                                is_active=True,
                            )
                        )

                        if product.membership_plan_id:
                            if item["quantity"] !=1:
                                raise ValueError(
                                    "Membership quantity must be one."
                                )
                        elif item["quantity"] > product.stock_quantity:
                            raise ValueError(
                                f"Only {product.stock_quantity} "
                                f"of {product.name} remain in stock."
                            )
                        locked_products[product.id] = product

                    order = form.save(commit=False)
                    order.user = request.user
                    order.paid = False
                    order.status = Order.Status.PENDING
                    order.save()

                    for item in cart_items:
                        product = locked_products[
                            item["product"].id
                        ]

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            membership_plan=product.membership_plan,
                            product_name=product.name,
                            price=product.price,
                            quantity=item["quantity"],
                        )

            except Product.DoesNotExist:
                form.add_error(
                    None,
                    "A product in your cart is no longer available.",
                )

            except ValueError as error:
                form.add_error(
                    None,
                    str(error),
                )

            except Exception:
                logger.exception(
                    "Order creation failed before Stripe Checkout."
                )

                messages.error(
                    request,
                    "The order could not be created. Please try again.",
                )

                return redirect("cart:checkout")

            else:
                try:
                    stripe.api_key = getattr(
                        settings,
                        "STRIPE_SECRET_KEY",
                        "",
                    ).strip()

                    if not stripe.api_key:
                        raise RuntimeError(
                            "STRIPE_SECRET_KEY is not configured."
                        )

                    stripe_currency = getattr(
                        settings,
                        "STRIPE_CURRENCY",
                        "eur",
                    ).lower()

                    line_items = []

                    for item in order.items.all():
                        line_items.append(
                            {
                                "price_data": {
                                    "currency": stripe_currency,
                                    "product_data": {
                                        "name": item.product_name,
                                    },
                                    "unit_amount": int(
                                        item.price
                                        * Decimal("100")
                                    ),
                                },
                                "quantity": item.quantity,
                            }
                        )

                    success_url = request.build_absolute_uri(
                        reverse(
                            "cart:order_confirmation",
                            args=[order.id],
                        )
                    )

                    success_url += (
                        "?session_id={CHECKOUT_SESSION_ID}"
                    )

                    cancel_url = request.build_absolute_uri(
                        reverse("cart:checkout")
                    )

                    checkout_session = (
                        stripe.checkout.Session.create(
                            mode="payment",
                            payment_method_types=["card"],
                            customer_email=order.email,
                            client_reference_id=str(
                                order.id
                            ),
                            metadata={
                                "order_id": str(order.id),
                                "user_id": str(
                                    request.user.id
                                ),
                            },
                            line_items=line_items,
                            success_url=success_url,
                            cancel_url=cancel_url,
                        )
                    )

                    order.stripe_checkout_session_id = (
                        checkout_session.id
                    )

                    order.save(
                        update_fields=[
                            "stripe_checkout_session_id",
                        ]
                    )

                    return redirect(
                        checkout_session.url
                    )

                except Exception:
                    logger.exception(
                        (
                            "Checkout failed while creating "
                            "Stripe session for order %s."
                        ),
                        order.id,
                    )

                    order.delete()

                    messages.error(
                        request,
                        (
                            "Stripe checkout could not be "
                            "started. Please try again."
                        ),
                    )

                    return redirect("cart:checkout")

    else:
        form = CheckoutForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            }
        )

    return render(
        request,
        "cart/checkout.html",
        {
            "cart": cart,
            "form": form,
        },
    )
def fulfill_paid_checkout(checkout_session):
    if checkout_session["payment_status"] != "paid":
        return False

    metadata = checkout_session["metadata"] or {}

    if "order_id" in metadata:
        order_id = metadata["order_id"]
    else:
        order_id = None

    if not order_id:
        raise ValueError(
            "The Stripe Session has no order ID."
        )

    with transaction.atomic():
        order = (
            Order.objects
            .select_for_update()
            .select_related("user")
            .get(
                pk=order_id,
                stripe_checkout_session_id=checkout_session["id"],
            )
        )

        # Prevent the same Stripe event being processed twice.
        if order.paid:
            return False

        order_items = list(
            order.items.select_related(
                "product",
                "membership_plan",
            )
        )

        expected_amount = sum(
            int(item.price * Decimal("100"))
            * item.quantity
            for item in order_items
        )

        if checkout_session["amount_total"] != expected_amount:
            raise ValueError(
                "The Stripe payment total does not match the order total."
            )

        membership_items = [
            item
            for item in order_items
            if item.membership_plan_id is not None
        ]

        if len(membership_items) > 1:
            raise ValueError(
                "An order cannot contain multiple membership plans."
            )

        physical_product_ids = [
            item.product_id
            for item in order_items
            if (
                item.membership_plan_id is None
                and item.product_id is not None
            )
        ]

        products = {
            product.id: product
            for product in (
                Product.objects
                .select_for_update()
                .filter(id__in=physical_product_ids)
            )
        }

        # Validate all physical stock first.
        for item in order_items:
            if item.membership_plan_id:
                if item.quantity != 1:
                    raise ValueError(
                        "Membership quantity must be one."
                    )

                continue

            product = products.get(item.product_id)

            if product is None:
                raise ValueError(
                    f"{item.product_name} is no longer available."
                )

            if item.quantity > product.stock_quantity:
                raise ValueError(
                    f"There is not enough stock for "
                    f"{item.product_name}."
                )

        # Reduce stock only for physical products.
        for item in order_items:
            if item.membership_plan_id:
                continue

            product = products[item.product_id]
            product.stock_quantity -= item.quantity
            product.save(
                update_fields=["stock_quantity"],
            )

        # Activate the purchased membership.
        if membership_items:
            purchased_plan = membership_items[0].membership_plan

            profile, _ = Profile.objects.select_for_update().get_or_create(
                user=order.user,
            )

            profile.current_membership = purchased_plan
            profile.save(
                update_fields=["current_membership"],
            )

        order.paid = True
        order.paid_at = timezone.now()
        order.status = Order.Status.COMPLETED
        order.save(
            update_fields=[
                "paid",
                "paid_at",
                "status",
            ]
        )

    return True
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    session_id = request.GET.get(
        "session_id",
        "",
    )

    if (
        session_id
        and session_id == order.stripe_checkout_session_id
        and not order.paid
    ):
        try:
            checkout_session = (
                stripe.checkout.Session.retrieve(
                    session_id
                )
            )

            fulfill_paid_checkout(
                checkout_session
            )

        except (
            stripe.StripeError,
            Order.DoesNotExist,
            ValueError,
        ):
            messages.warning(
                request,
                "Your payment is still being verified.",
            )

        order.refresh_from_db()

    if order.paid:
        Cart(request).clear()

    return render(
        request,
        "cart/order_confirmation.html",
        {"order": order},
    )
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body

    signature = request.META.get(
        "HTTP_STRIPE_SIGNATURE",
        "",
    )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]

    if event_type in (
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    ):
        checkout_session = event["data"]["object"]

        try:
            fulfill_paid_checkout(
                checkout_session
            )

        except (
            Order.DoesNotExist,
            ValueError,
        ):
            return HttpResponse(status=400)

    return HttpResponse(status=200)