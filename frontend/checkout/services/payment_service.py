from django.conf import settings
from frontend.checkout.models import Payment, Order
from core.payment.gateway import simulate_payment_success, create_payment_intent
from core.constants import ORDER_COMPLETED, PAYMENT_SUCCEEDED


def initiate_payment(order: Order, total_override=None) -> dict:
    """
    Initiate payment for an order.
    Pass total_override when a batch of orders share one payment.
    In dev mode (placeholder keys), simulate success immediately.
    """
    amount_pence = int((total_override or order.total_amount) * 100)

    if settings.DEBUG and settings.STRIPE_SECRET_KEY == 'sk_test_placeholder':
        result = simulate_payment_success(order.order_number)
    else:
        result = create_payment_intent(amount_pence, metadata={'order_number': order.order_number})

    return result


def complete_payment(order: Order, intent_id: str, total_override=None) -> Payment:
    """Mark the order and payment as completed.
    Pass total_override when multiple orders share one payment (batch purchase).
    """
    payment = Payment.objects.create(
        order=order,
        amount=total_override if total_override is not None else order.total_amount,
        status=PAYMENT_SUCCEEDED,
        stripe_payment_intent_id=intent_id,
    )
    order.status = ORDER_COMPLETED
    order.save(update_fields=['status'])
    return payment
