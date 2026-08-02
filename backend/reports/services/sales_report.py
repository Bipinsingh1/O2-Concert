from django.db.models import Count, Q
from frontend.ticket_sales.models import Ticket, TicketCategory
from core.constants import TICKET_ACTIVE, TICKET_CANCELLED, TICKET_VIP, VIP_INVENTORY, OTHER_INVENTORY


def get_sales_volume_report() -> dict:
    categories = TicketCategory.objects.annotate(
        active=Count('tickets', filter=Q(tickets__status=TICKET_ACTIVE)),
        cancelled=Count('tickets', filter=Q(tickets__status=TICKET_CANCELLED)),
    )

    # Non-VIP tickets share a single pool of OTHER_INVENTORY (900)
    non_vip_sold = Ticket.objects.filter(
        status=TICKET_ACTIVE,
        category__category_type__in=['restricted', 'standard', 'group'],
    ).count()
    shared_pool_remaining = max(0, OTHER_INVENTORY - non_vip_sold)

    by_category = []
    for cat in categories:
        if cat.category_type == TICKET_VIP:
            pool_total = VIP_INVENTORY
            remaining = max(0, VIP_INVENTORY - cat.active)
        else:
            pool_total = OTHER_INVENTORY   # all three non-VIP share 900
            remaining = shared_pool_remaining
        by_category.append({
            'name': cat.name,
            'category_type': cat.category_type,
            'pool_total': pool_total,
            'remaining': remaining,
            'active': cat.active,
            'cancelled': cat.cancelled,
            'is_shared_pool': cat.category_type != TICKET_VIP,
        })

    total_sold = Ticket.objects.filter(status=TICKET_ACTIVE).count()
    total_cancelled = Ticket.objects.filter(status=TICKET_CANCELLED).count()

    return {
        'by_category': by_category,
        'total_sold': total_sold,
        'total_cancelled': total_cancelled,
        'other_inventory': OTHER_INVENTORY,
        'vip_inventory': VIP_INVENTORY,
    }
