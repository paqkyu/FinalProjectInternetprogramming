from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
    )

    email = forms.EmailField(
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap styling to every form field.
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control",
            })
    

        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["first_name"].widget.attrs["placeholder"] = "First name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last name"
        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"
    def clean_username(self):
        username=self.cleaned_data["username"].strip().upper()
        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )
        return username
class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model=User
        fields=(
            "first_name",
            "last_name",
            "email",
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                    "class": "form-control",
            })
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "First name",
        })
        self.fields["last_name"].widget.attrs.update({
            "placeholder": "Last name",
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "Email adderess",
        })
        
    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        existing_user=User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        )
        if existing_user.exists():
            raise forms.ValidationError(
                "This email address is already taken"
            )
        return email

class LoginForm(AuthenticationForm):

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Username",
            "autofocus": True,
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Password",
        })
    def clean_username(self):
        return self.cleaned_data["username"].strip().upper()