from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
    )
    phone_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        if commit:
            user.save()
        return user
