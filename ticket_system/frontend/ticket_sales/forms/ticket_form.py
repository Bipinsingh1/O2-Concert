from django import forms
from frontend.ticket_sales.models import TicketCategory


class TicketSelectForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=TicketCategory.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
    )
    quantity = forms.IntegerField(
        min_value=1, max_value=10, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control text-center fw-bold', 'min': 1, 'max': 10}),
    )
    guest_name = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
    )
    guest_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
    )

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get('category')
        quantity = cleaned.get('quantity', 1)
        guest_name = cleaned.get('guest_name', '').strip()
        guest_email = cleaned.get('guest_email', '').strip()

        if category and not category.is_available:
            raise forms.ValidationError(f'Sorry, {category.name} tickets are sold out.')
        if category and quantity and category.remaining < quantity:
            raise forms.ValidationError(
                f'Only {category.remaining} ticket(s) remaining for {category.name}.'
            )

        # Require guest details when no user is logged in — checked server-side
        # (can't use request in form.clean directly, so we rely on a flag set by the view)
        if self._require_guest_fields:
            if not guest_name:
                self.add_error('guest_name', 'Please enter your full name.')
            if not guest_email:
                self.add_error('guest_email', 'Please enter your email address.')

        return cleaned

    def __init__(self, *args, require_guest_fields=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._require_guest_fields = require_guest_fields
