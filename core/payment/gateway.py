"""
Payment gateway integration.
Uses Stripe for card payment processing.
In development (placeholder keys), payments are simulated.
"""
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount_pence: int, currency: str = 'gbp', metadata: dict = None):
    """
    Create a Stripe PaymentIntent.
    amount_pence: amount in smallest currency unit (pence for GBP).
    Returns the PaymentIntent object.
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_pence,
            currency=currency,
            payment_method_types=['card'],
            metadata=metadata or {},
        )
        return {'success': True, 'client_secret': intent.client_secret, 'intent_id': intent.id}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': str(e)}


def confirm_payment(payment_intent_id: str):
    """Retrieve and confirm status of a PaymentIntent."""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {'success': True, 'status': intent.status, 'intent': intent}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': str(e)}


def simulate_payment_success(order_number: str) -> dict:
    """
    For development: simulate a successful payment without calling Stripe.
    Returns a mock payment result.
    """
    return {
        'success': True,
        'status': 'succeeded',
        'intent_id': f'pi_simulated_{order_number}',
        'client_secret': f'pi_simulated_{order_number}_secret',
    }
