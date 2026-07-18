from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.models import Profile
from .models import Booking, TrainerProfile
# Create your views here.
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
@require_POST
def book_trainer(request, trainer_id):
    profile,_=Profile.objects.get_or_create(
        user=request.user
    )
    if not profile.can_book_trainer:
        messages.warning(
            request,
            "Trainer booking is available with Premium and Elite memberships. Please upgrade your plan",
        )
        return redirect("catalog:memberships")
    trainer = get_object_or_404(
        TrainerProfile,
        pk=trainer_id,
        is_available=True
    )
    starts_at=request.Post.get("starts_at")
    
    Bookings.objects.create(
        member=request.user,
        trainer=trainer,
        starts_at=starts_at,
    )
    messages.success(
        request,
        "Your trainer booking was submitted",
    )
    return redirect("accounts:member_dashboard")
