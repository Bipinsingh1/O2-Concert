from django.db.models import Case, Count, IntegerField, Q, Value, When
from frontend.ticket_sales.models import TicketCategory
from core.constants import (
    TICKET_ACTIVE,
    TICKET_GROUP,
    TICKET_RESTRICTED,
    TICKET_STANDARD,
    TICKET_VIP,
    VIP_INVENTORY,
    OTHER_INVENTORY,
    NON_VIP_CATEGORY_TYPES,
)


def annotate_remaining(queryset=None):
    """
    Return all TicketCategory instances with `.remaining` and `.sold_count`
    pre-computed using 1 query (+ 0 extra per category).

    Each category instance gets:
      - `sold`              — annotated integer (active tickets for that category)
      - `_remaining_cache`  — set on __dict__ so the property picks it up
    """
    cats = list(
        (queryset or TicketCategory.objects).annotate(
            sold=Count('tickets', filter=Q(tickets__status=TICKET_ACTIVE))
        )
    )
    non_vip_sold = sum(c.sold for c in cats if c.category_type != TICKET_VIP)
    shared_remaining = max(0, OTHER_INVENTORY - non_vip_sold)
    for cat in cats:
        if cat.category_type == TICKET_VIP:
            cat.__dict__['_remaining_cache'] = max(0, VIP_INVENTORY - cat.sold)
        else:
            cat.__dict__['_remaining_cache'] = shared_remaining
    return cats


def get_available_categories():
    """Return all ticket categories with remaining counts pre-computed (no N+1)."""
    display_order = Case(
        When(category_type=TICKET_RESTRICTED, then=Value(1)),
        When(category_type=TICKET_STANDARD, then=Value(2)),
        When(category_type=TICKET_GROUP, then=Value(3)),
        When(category_type=TICKET_VIP, then=Value(4)),
        default=Value(5),
        output_field=IntegerField(),
    )
    categories = TicketCategory.objects.order_by(display_order)
    return annotate_remaining(categories)


def is_ticket_available(category_type: str, quantity: int = 1) -> tuple[bool, str]:
    """Check if the requested quantity of a category is available."""
    try:
        cat = TicketCategory.objects.get(category_type=category_type)
    except TicketCategory.DoesNotExist:
        return False, 'Ticket category not found.'
    if cat.remaining < quantity:
        return False, f'Only {cat.remaining} ticket(s) remaining for {cat.name}.'
    return True, ''
