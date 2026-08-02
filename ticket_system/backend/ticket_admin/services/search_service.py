from frontend.ticket_sales.models import Ticket


def search_tickets(query: str):
    """Search tickets by ticket number, customer email, or customer name."""
    if not query:
        return Ticket.objects.none()
    return Ticket.objects.filter(
        __import__('django.db.models', fromlist=['Q']).Q(ticket_number__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(owner__email__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(owner__first_name__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(owner__last_name__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(guest_email__icontains=query) |
        __import__('django.db.models', fromlist=['Q']).Q(guest_name__icontains=query)
    ).select_related('category', 'owner').order_by('-purchase_date')
