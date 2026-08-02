from frontend.my_tickets.services.cancel_service import cancel_ticket


def admin_cancel_ticket(ticket, admin_user) -> dict:
    """Admin cancels a ticket on behalf of a customer."""
    return cancel_ticket(ticket, admin_user)
