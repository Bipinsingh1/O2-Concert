import stripe
from django.conf import settings
from core.utils.helpers import calculate_refund_amount
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


def process_refund(payment_intent_id: str, amount_paid: Decimal) -> dict:
    """
    Issue a partial refund (after deducting 20% cancellation fee).
    Returns dict with success, refund_amount, error.
    """
    refund_amount = calculate_refund_amount(amount_paid)
    refund_pence = int(refund_amount * 100)

    # Skip Stripe call for simulated/placeholder payments
    if payment_intent_id.startswith('pi_simulated_'):
        return {'success': True, 'refund_amount': refund_amount, 'refund_id': 'rf_simulated'}

    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=refund_pence,
        )
        return {'success': True, 'refund_amount': refund_amount, 'refund_id': refund.id}
    except stripe.error.StripeError as e:
        return {'success': False, 'refund_amount': Decimal('0'), 'error': str(e)}
