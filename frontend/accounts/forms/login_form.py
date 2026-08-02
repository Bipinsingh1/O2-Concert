from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
