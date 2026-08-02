from django.db import transaction
from decimal import Decimal
from core.constants import TICKET_ACTIVE, TICKET_UPGRADE_PATHS, ORDER_COMPLETED, PAYMENT_SUCCEEDED
from core.permissions import can_amend_ticket
from core.utils.ticket_number import generate_order_number


@transaction.atomic
def upgrade_ticket(ticket, new_category, requesting_user) -> dict:
    """
    Upgrade a ticket to a higher category.
    The customer pays the price difference (up to the new ticket price).
    Creates an Order + Payment record for the upgrade charge for audit purposes.
    """
    can, reason = can_amend_ticket(ticket)
    if not can:
        return {'success': False, 'error': reason}

    valid_upgrades = TICKET_UPGRADE_PATHS.get(ticket.category.category_type, [])
    if new_category.category_type not in valid_upgrades:
        return {'success': False, 'error': 'You can only upgrade, not downgrade your ticket.'}

    if not new_category.is_available:
        return {'success': False, 'error': f'{new_category.name} tickets are sold out.'}

    price_diff = max(Decimal('0'), new_category.price - ticket.amount_paid)
    old_category_name = ticket.category.name

    # Update ticket
    ticket.category = new_category
    ticket.status = TICKET_ACTIVE
    ticket.amount_paid = ticket.amount_paid + price_diff
    ticket.save(update_fields=['category', 'status', 'amount_paid'])

    # Create an Order + Payment record so the upgrade charge has an audit trail
    if price_diff > 0:
        from frontend.checkout.models import Order, Payment
        upgrade_order = Order.objects.create(
            order_number=generate_order_number(),
            user=requesting_user if requesting_user and requesting_user.is_authenticated else None,
            guest_email=ticket.guest_email if ticket.is_guest_purchase else '',
            ticket=None,  # Upgrade orders are not linked to a ticket (ticket already has its original order)
            subtotal=price_diff,
            discount_amount=Decimal('0'),
            total_amount=price_diff,
            status=ORDER_COMPLETED,
        )
        Payment.objects.create(
            order=upgrade_order,
            amount=price_diff,
            status=PAYMENT_SUCCEEDED,
            stripe_payment_intent_id=f'pi_upgrade_{ticket.ticket_number}',
        )

    return {
        'success': True,
        'price_diff': price_diff,
        'old_category': old_category_name,
        'new_category': new_category.name,
    }
