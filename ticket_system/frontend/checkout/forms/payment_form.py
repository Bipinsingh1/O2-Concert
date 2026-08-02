from django import forms


class PaymentForm(forms.Form):
    """Collects card details for Stripe payment (card element handled via JS)."""
    card_holder_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name on card'}),
    )
