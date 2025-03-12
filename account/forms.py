from django import forms
from .models import CustomUser, ProfileUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm


class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'username', 'password', 'confirm_password']


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already exist.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already exist")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password must be match")
        return confirm_password


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), max_length=255)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), max_length=255)


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ProfileUser
        fields = ['photo', 'bio']