from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.models import Profile
from .forms import BookingForm
from django.db import IntegrityError, transaction
from .models import Booking, TrainerProfile
# Create your views here.
@login_required
def trainer_list(request):
    trainers=TrainerProfile.objects.filter(
        is_available=True
    ).select_related("user")
    return render(
        request,
        "bookings/trainer_list.html",
        {"trainers": trainers},
    )
@login_required
def trainer_detail(request, trainer_id):
    trainer = get_object_or_404(
        TrainerProfile.objects.select_related("user"),
        pk=trainer_id,
        is_available=True,
    )

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
    )

    if request.method == "POST":
        if not profile.can_book_trainer:
            messages.warning(
                request,
                "Trainer booking requires a Premium or Elite membership.",
            )

            # Temporary redirect until the membership purchase page exists.
            return redirect("accounts:dashboard")

        form = BookingForm(
            request.POST,
            trainer=trainer,
            member=request.user,
        )

        if form.is_valid():
            booking = form.save(commit=False)
            booking.member = request.user
            booking.trainer = trainer

            try:
                with transaction.atomic():
                    booking.save()

            except IntegrityError:
                form.add_error(
                    "starts_at",
                    "This trainer is already booked at that time.",
                )

            else:
                messages.success(
                    request,
                    "Your trainer booking was submitted.",
                )

                return redirect("bookings:my_bookings")

    else:
        form = BookingForm(
            trainer=trainer,
            member=request.user,
        )

    return render(
        request,
        "bookings/trainer_detail.html",
        {
            "trainer": trainer,
            "profile": profile,
            "form": form,
        },
    )
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        member=request.user,
    ).select_related(
        "trainer",
        "trainer__user",
    )

    return render(
        request,
        "bookings/my_bookings.html",
        {"bookings": bookings},
    )
@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        pk=booking_id,
        member=request.user,
    )

    if booking.status in (
        Booking.Status.COMPLETED,
        Booking.Status.CANCELLED,
    ):
        messages.warning(
            request,
            "This booking can no longer be cancelled.",
        )

        return redirect("bookings:my_bookings")

    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["status"])

    messages.success(
        request,
        "Your booking was cancelled.",
    )

    return redirect("bookings:my_bookings")
