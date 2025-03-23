from django import forms
from .models import CustomUser, ProfileUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm


class SignUpForm(forms.ModelForm):
    """
    A form for user registration that includes fields for:
    full name, email, username, password, and password confirmation.

    The form ensures:
    - The username is unique.
    - The email is unique.
    - The password and confirmation password match.
    """
    # Additional field for confirming the password
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'username', 'password', 'confirm_password']


    def clean_username(self):
        """
        Validate that the username is unique.
        """
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already exist.")
        return username

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already exist")
        return email

    def clean_confirm_password(self):
        """
        Validate that the password and confirm_password fields match.
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password must be match")
        return confirm_password


class ForgetPasswordForm(forms.Form):
    """
    Form for requesting a password reset.
    Users need to provide their registered email address.
    """
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    """
    Form for resetting the user's password.
    Ensures that the new password and confirmation password match.
    """
    password = forms.CharField(widget=forms.PasswordInput(), max_length=255)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), max_length=255)

    def clean_confirm_password(self):
        """
        Validate that the password and confirm_password fields match.
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords must match.")
        return confirm_password



class CustomUserForm(forms.ModelForm):
    """
    Form for updating a user's full name.
    """
    class Meta:
        model = CustomUser
        fields = ['full_name']


class UserProfileForm(forms.ModelForm):
    """
    Form for updating a user's profile details, including photo and bio.
    """
    class Meta:
        model = ProfileUser
        fields = ['photo', 'bio']