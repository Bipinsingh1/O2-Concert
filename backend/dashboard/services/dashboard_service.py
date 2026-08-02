from django.core.cache import cache
from django.db.models import Sum, Count, Q
from frontend.ticket_sales.models import Ticket, TicketCategory
from frontend.checkout.models import Order, Payment
from django.contrib.auth import get_user_model
from core.constants import (
    TICKET_ACTIVE, TICKET_CANCELLED, ORDER_COMPLETED,
    PAYMENT_SUCCEEDED, PAYMENT_REFUNDED,
    TICKET_VIP, VIP_INVENTORY, OTHER_INVENTORY,
    NON_VIP_CATEGORY_TYPES,
)

User = get_user_model()


DASHBOARD_CACHE_KEY = 'dashboard_stats'
DASHBOARD_CACHE_TTL = 30  # seconds


def get_dashboard_stats() -> dict:
    cached = cache.get(DASHBOARD_CACHE_KEY)
    if cached is not None:
        return cached

    # Single query for all ticket counts
    ticket_counts = Ticket.objects.aggregate(
        total=Count('id', filter=Q(status=TICKET_ACTIVE)),
        cancelled=Count('id', filter=Q(status=TICKET_CANCELLED)),
        guests=Count('id', filter=Q(status=TICKET_ACTIVE, is_guest_purchase=True)),
        non_vip_sold=Count(
            'id',
            filter=Q(status=TICKET_ACTIVE, category__category_type__in=NON_VIP_CATEGORY_TYPES),
        ),
    )
    total_tickets = ticket_counts['total']
    cancelled_tickets = ticket_counts['cancelled']
    guest_purchases = ticket_counts['guests']
    non_vip_sold = ticket_counts['non_vip_sold']

    # Include refunded payments — money was received even if later partially returned
    total_revenue = Payment.objects.filter(
        status__in=[PAYMENT_SUCCEEDED, PAYMENT_REFUNDED]
    ).aggregate(total=Sum('amount'))['total'] or 0

    registered_customers = User.objects.filter(is_staff=False).count()
    shared_pool_remaining = max(0, OTHER_INVENTORY - non_vip_sold)

    categories = TicketCategory.objects.annotate(
        sold=Count('tickets', filter=Q(tickets__status=TICKET_ACTIVE))
    )
    by_category = []
    for cat in categories:
        if cat.category_type == TICKET_VIP:
            pool_total = VIP_INVENTORY
            remaining = max(0, VIP_INVENTORY - cat.sold)
        else:
            pool_total = OTHER_INVENTORY
            remaining = shared_pool_remaining
        by_category.append({
            'name': cat.name,
            'category_type': cat.category_type,
            'pool_total': pool_total,
            'remaining': remaining,
            'sold': cat.sold,
            'is_shared_pool': cat.category_type != TICKET_VIP,
        })

    recent_orders = list(
        Order.objects.filter(status=ORDER_COMPLETED)
        .select_related('user', 'ticket__category')
        .order_by('-created_at')[:10]
    )

    result = {
        'total_tickets': total_tickets,
        'cancelled_tickets': cancelled_tickets,
        'total_revenue': total_revenue,
        'registered_customers': registered_customers,
        'guest_purchases': guest_purchases,
        'by_category': by_category,
        'recent_orders': recent_orders,
    }
    cache.set(DASHBOARD_CACHE_KEY, result, timeout=DASHBOARD_CACHE_TTL)
    return result
