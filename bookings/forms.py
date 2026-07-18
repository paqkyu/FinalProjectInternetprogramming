from django import forms
from django.utils import timezone

from .models import Booking
from datetime import timedelta

OPENING_HOUR=8
LAST_START_HOUR=23
SESSION_LENGTH=timedelta(hours=1)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            "starts_at",
            "notes",
        )

        widgets = {
            "starts_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "step": 3600,
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Optional notes for the trainer",
                }
            ),
        }

    def __init__(self, *args, trainer=None, member=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.trainer = trainer
        self.member = member

        self.fields["starts_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]
        now = timezone.now()
        if timezone.is_aware(now):
            now=timezone.localtime(now)
        next_available_time=(now + timedelta(hours=1)).replace(minute=0,second=0,microsecond=0)
        if next_available_time.hour < OPENING_HOUR:
            next_available_time=next_available_time.replace(hour=OPENING_HOUR)
        self.fields["starts_at"].widget.attrs["min"]=(
            next_available_time.strftime("%Y-%m-%dT%H:%M")
        )

    def clean_starts_at(self):
        starts_at = self.cleaned_data["starts_at"]
        if not starts_at:
            return starts_at

        if starts_at <= timezone.now():
            raise forms.ValidationError(
                "Please select a future date and time."
            )
        if timezone.is_aware(starts_at):
            local_starts_at=timezone.localtime(starts_at)
        else:
            local_starts_at=starts_at
        if (
            local_starts_at.minute !=0
            or local_starts_at.second !=0
        ):
            raise forms.ValidationError(
                "Bookings must begin exactly on the hour."
            )
        if not(
            OPENING_HOUR
            <=local_starts_at.hour
            <=LAST_START_HOUR
        ):
            raise forms.ValidationError(
                "Bookings are available from 8:00 AM until midnight."
                "The final sessions begin at 11:00 PM."
            )
        conflict_start=starts_at - SESSION_LENGTH
        conflict_end=starts_at + SESSION_LENGTH
        if (
            self.trainer
            and Booking.objects.filter(
                trainer=self.trainer,
                starts_at__gt=conflict_start,
                starts_at__lt=conflict_end,
            ).exclude(
                status=Booking.Status.CANCELLED,
            ).exists()
        ):
            raise forms.ValidationError(
                "This trainer already has a booking during "
                "that one-hour time slot."
            )
        if (
            self.member
            and Booking.objects.filter(
                member=self.member,
                starts_at__gt=conflict_start,
                starts_at__lt=conflict_end,
            ).exclude(
                status=Booking.Status.CANCELLED
            ).exists()
        ):
            raise forms.ValidationError(
                "You already have another booking during this time."
            )

        if (
            self.trainer
            and Booking.objects.filter(
                trainer=self.trainer,
                starts_at=starts_at,
            ).exclude(
                status=Booking.Status.CANCELLED,
            ).exists()
        ):
            raise forms.ValidationError(
                "This trainer is already booked at that time."
            )

        if (
            self.member
            and Booking.objects.filter(
                member=self.member,
                starts_at=starts_at,
            ).exclude(
                status=Booking.Status.CANCELLED,
            ).exists()
        ):
            raise forms.ValidationError(
                "You already have another booking at that time."
            )

        return starts_at