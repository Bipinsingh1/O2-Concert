from frontend.ticket_sales.models import Ticket
from core.constants import TICKET_ACTIVE


def get_user_tickets(user):
    return Ticket.objects.filter(owner=user).select_related('category').prefetch_related('holders')
