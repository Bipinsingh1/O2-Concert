from frontend.my_tickets.services.upgrade_service import upgrade_ticket


def admin_upgrade_ticket(ticket, new_category, admin_user) -> dict:
    return upgrade_ticket(ticket, new_category, admin_user)
