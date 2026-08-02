from django import forms
from django.forms import formset_factory
from core.constants import GROUP_MAX_MEMBERS, AGE_GROUPS


class MemberForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
    )
    age_group = forms.ChoiceField(
        choices=AGE_GROUPS,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class GroupTicketForm(forms.Form):
    guest_name = forms.CharField(
        max_length=200, required=False,
        label='Purchaser Name',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    guest_email = forms.EmailField(
        required=False,
        label='Purchaser Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )


MemberFormSet = formset_factory(MemberForm, extra=GROUP_MAX_MEMBERS - 1, min_num=1, max_num=GROUP_MAX_MEMBERS, validate_min=True)
