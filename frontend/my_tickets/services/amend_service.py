from core.permissions import can_amend_ticket


def get_valid_upgrade_categories(ticket):
    """Return categories the ticket can be upgraded to, filtered by live remaining inventory."""
    from frontend.ticket_sales.models import TicketCategory
    from core.constants import TICKET_UPGRADE_PATHS
    upgrade_types = TICKET_UPGRADE_PATHS.get(ticket.category.category_type, [])
    # Use the `remaining` property (shared-pool aware) rather than the DB field
    candidates = TicketCategory.objects.filter(category_type__in=upgrade_types)
    return [cat for cat in candidates if cat.remaining > 0]
