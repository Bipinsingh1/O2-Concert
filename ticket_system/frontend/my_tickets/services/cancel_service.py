import logging

from django.db import transaction
from django.core.mail import EmailMessage
from django.conf import settings
from core.constants import TICKET_CANCELLED, ORDER_CANCELLED, ORDER_REFUNDED, PAYMENT_REFUNDED
from core.permissions import can_cancel_ticket, get_refund_eligibility
from core.payment.refund import process_refund
from core.utils.email import send_cancellation_email

logger = logging.getLogger(__name__)


def _notify_next_waitlist(category):
    """Email the next person on the waitlist (if any) that a ticket is now free."""
    from frontend.ticket_sales.models import WaitlistEntry
    entry = WaitlistEntry.objects.filter(category=category, notified=False).first()
    if not entry:
        return
    try:
        msg = EmailMessage(
            subject=f'Ticket Available – {settings.EVENT_NAME}',
            body=(
                f'Good news! A {category.name} ticket for {settings.EVENT_NAME} '
                f'has just become available.\n\n'
                f'Visit the ticket page now to secure yours: '
                f'it may sell out quickly.\n\n'
                f'— The O2 Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[entry.email],
        )
        msg.send(fail_silently=True)
        entry.notified = True
        entry.save(update_fields=['notified'])
        logger.info('Waitlist notification sent to %s for %s', entry.email, category.name)
    except Exception:
        logger.exception('Failed to send waitlist notification to %s', entry.email)


@transaction.atomic
def cancel_ticket(ticket, requesting_user) -> dict:
    """Cancel a ticket and issue a refund if applicable."""
    can, reason = can_cancel_ticket(ticket, requesting_user)
    if not can:
        return {'success': False, 'error': reason}

    order = getattr(ticket, 'order', None)
    refund_amount = None

    will_refund, _ = get_refund_eligibility(ticket, requesting_user)
    if will_refund:
        payment = getattr(order, 'payment', None) if order else None
        if payment:
            result = process_refund(payment.stripe_payment_intent_id, ticket.amount_paid)
            if result['success']:
                refund_amount = result['refund_amount']
                from frontend.checkout.models import Refund
                Refund.objects.create(
                    payment=payment,
                    amount=refund_amount,
                    reason='Customer cancellation',
                    processed_by=requesting_user if requesting_user.is_staff else None,
                )
                payment.status = PAYMENT_REFUNDED
                payment.save(update_fields=['status'])

    ticket.status = TICKET_CANCELLED
    ticket.save(update_fields=['status'])

    if order:
        order.status = ORDER_REFUNDED if refund_amount else ORDER_CANCELLED
        order.save(update_fields=['status'])

    send_cancellation_email(ticket, refund_amount)

    # Notify the next person on the waitlist for this category
    try:
        _notify_next_waitlist(ticket.category)
    except Exception:
        logger.exception('Waitlist notification failed after cancelling ticket %s', ticket.ticket_number)

    return {'success': True, 'refund_amount': refund_amount}
