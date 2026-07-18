from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from bookings.models import Booking

from .forms import LoginForm, RegistrationForm, AccountUpdateForm
from django.contrib import messages
from .models import Profile

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
def dashboard(request):
    if request.user.is_superuser:
        return redirect("admin:index")
    
    if is_staff_member(request.user):
        return redirect("accounts:staff_dashboard")
    
    profile,_=Profile.objects.get_or_create(
        user=request.user
    )
    return render(request, "accounts/dashboard.html", {"profile": profile},)
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

def is_staff_member(user):
    return(
        user.is_authenticated
        and (
            user.is_superuser or user.groups.filter(name="Staff").exists())
    )
@login_required
@user_passes_test(is_staff_member)
def staff_dashboard(request):
    bookings=Booking.objects.filter(
        trainer__user=request.user
    ).select_related(
        "member",
        "member__profile",
        "trainer",
        "trainer__user",
    )
    return render(
        request,
        "accounts/staff_dashboard.html",
        {"bookings":bookings},
    )