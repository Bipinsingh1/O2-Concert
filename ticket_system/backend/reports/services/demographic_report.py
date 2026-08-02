from django.db.models import Count
from frontend.ticket_sales.models import Ticket, TicketHolder
from core.constants import TICKET_ACTIVE


def get_demographic_report() -> dict:
    # Only count active (paid) tickets — cancelled tickets are excluded
    active_tickets = Ticket.objects.filter(status=TICKET_ACTIVE)

    guest_count = active_tickets.filter(is_guest_purchase=True).count()
    registered_count = active_tickets.filter(is_guest_purchase=False).count()

    # Only count attendees on active tickets
    age_groups = (
        TicketHolder.objects
        .filter(ticket__status=TICKET_ACTIVE)
        .values('age_group')
        .annotate(count=Count('id'))
    )

    return {
        'guest_purchases': guest_count,
        'registered_purchases': registered_count,
        'age_groups': list(age_groups),
    }
