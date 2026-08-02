from django.db import transaction, IntegrityError
from frontend.ticket_sales.models import Ticket, TicketHolder
from core.utils.ticket_number import generate_ticket_number
from core.utils.qr import generate_qr_code, get_qr_code_path
from core.constants import TICKET_ACTIVE
import os

_MAX_TICKET_NUMBER_RETRIES = 5


@transaction.atomic
def create_ticket(category, user=None, guest_name='', guest_email='',
                  amount_paid=None, original_price=None,
                  discount_percent=0, discount_amount=None,
                  holders=None):
    """
    Create a Ticket and its TicketHolder records.
    holders: list of dicts with keys 'name' and 'age_group'.
    Retries up to _MAX_TICKET_NUMBER_RETRIES times on ticket-number collision.
    """
    is_guest = user is None

    ticket = None
    for attempt in range(_MAX_TICKET_NUMBER_RETRIES):
        ticket_number = generate_ticket_number()
        try:
            ticket = Ticket.objects.create(
                ticket_number=ticket_number,
                category=category,
                owner=user,
                guest_name=guest_name if is_guest else '',
                guest_email=guest_email if is_guest else '',
                is_guest_purchase=is_guest,
                status=TICKET_ACTIVE,
                amount_paid=amount_paid or category.price,
                original_price=original_price or category.price,
                discount_percent=discount_percent,
                discount_amount=discount_amount or 0,
            )
            break
        except IntegrityError:
            if attempt == _MAX_TICKET_NUMBER_RETRIES - 1:
                raise
            continue

    # Generate and save QR code
    qr_path = get_qr_code_path(ticket_number)
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    generate_qr_code(ticket_number, save_path=qr_path)
    ticket.qr_code = f'qrcodes/{ticket_number}.png'
    ticket.save(update_fields=['qr_code'])

    # Create holders
    if holders:
        for h in holders:
            TicketHolder.objects.create(
                ticket=ticket,
                name=h['name'],
                age_group=h.get('age_group', 'adult'),
            )
    else:
        # Single ticket: holder is the purchaser
        name = user.get_full_name() if user else guest_name
        TicketHolder.objects.create(ticket=ticket, name=name, age_group='adult')

    return ticket
