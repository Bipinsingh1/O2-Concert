from django.db import transaction
from frontend.checkout.models import Order
from frontend.ticket_sales.models import TicketCategory, Ticket
from frontend.ticket_sales.services.discount_service import calculate_discounted_price
from frontend.ticket_sales.services.purchase_service import create_ticket
from core.utils.ticket_number import generate_order_number
from core.constants import (
    TICKET_VIP, VIP_INVENTORY, OTHER_INVENTORY,
    NON_VIP_CATEGORY_TYPES, TICKET_ACTIVE,
)


class InsufficientInventoryError(Exception):
    pass


def _check_inventory(category, quantity: int):
    """
    Verify enough stock remains. Must be called inside @transaction.atomic
    with the category row already locked via select_for_update().
    Raises InsufficientInventoryError when the purchase would exceed the cap.
    """
    if category.category_type == TICKET_VIP:
        sold = Ticket.objects.filter(
            category=category, status=TICKET_ACTIVE
        ).count()
        if sold + quantity > VIP_INVENTORY:
            raise InsufficientInventoryError('Not enough VIP tickets remaining.')
    else:
        # Lock all non-VIP category rows so concurrent purchases queue up
        # and the shared-pool count stays consistent for the duration of
        # this transaction.
        list(TicketCategory.objects.select_for_update().filter(
            category_type__in=NON_VIP_CATEGORY_TYPES
        ))
        non_vip_sold = Ticket.objects.filter(
            status=TICKET_ACTIVE,
            category__category_type__in=NON_VIP_CATEGORY_TYPES,
        ).count()
        if non_vip_sold + quantity > OTHER_INVENTORY:
            raise InsufficientInventoryError('Not enough tickets remaining in this pool.')


def _create_one_order(pending, category, user, pricing) -> Order:
    """Create a single Ticket + Order pair from pending session data."""
    holders = pending.get('members', [])
    ticket = create_ticket(
        category=category,
        user=user,
        guest_name=pending.get('guest_name', ''),
        guest_email=pending.get('guest_email', ''),
        amount_paid=pricing['final_price'],
        original_price=pricing['original_price'],
        discount_percent=pricing['discount_percent'],
        discount_amount=pricing['discount_amount'],
        holders=holders if holders else None,
    )
    order = Order.objects.create(
        order_number=generate_order_number(),
        user=user,
        guest_email=pending.get('guest_email', ''),
        ticket=ticket,
        subtotal=pricing['original_price'],
        discount_amount=pricing['discount_amount'],
        total_amount=pricing['final_price'],
    )
    return order


@transaction.atomic
def build_order_from_session(request) -> Order | None:
    """Create a single order from session (used for group tickets)."""
    pending = request.session.get('pending_ticket')
    if not pending:
        return None
    try:
        category = TicketCategory.objects.select_for_update().get(pk=pending['category_id'])
    except TicketCategory.DoesNotExist:
        return None
    try:
        _check_inventory(category, 1)
    except InsufficientInventoryError:
        return None
    user = request.user if request.user.is_authenticated else None
    pricing = calculate_discounted_price(category.price, user)
    return _create_one_order(pending, category, user, pricing)


@transaction.atomic
def build_orders_from_session(request) -> list:
    """Create N orders from session based on quantity. Returns list of Orders."""
    pending = request.session.get('pending_ticket')
    if not pending:
        return []
    try:
        category = TicketCategory.objects.select_for_update().get(pk=pending['category_id'])
    except TicketCategory.DoesNotExist:
        return []
    quantity = max(1, int(pending.get('quantity', 1)))
    try:
        _check_inventory(category, quantity)
    except InsufficientInventoryError:
        return []
    user = request.user if request.user.is_authenticated else None
    pricing = calculate_discounted_price(category.price, user)
    return [_create_one_order(pending, category, user, pricing) for _ in range(quantity)]
