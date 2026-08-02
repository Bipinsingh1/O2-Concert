def is_admin(user):
    """Return True if the user has admin/staff privileges."""
    return user.is_authenticated and user.is_staff


def is_registered_customer(user):
    """Return True if the user is a registered (non-guest) customer."""
    return user.is_authenticated and not user.is_staff


def can_cancel_ticket(ticket, user):
    """
    Check whether a ticket can be cancelled at all.
    Admins bypass the 72-hour window restriction.
    Returns (allowed: bool, reason: str).
    """
    from core.constants import TICKET_ACTIVE
    if ticket.status != TICKET_ACTIVE:
        return False, 'This ticket has already been cancelled or amended and cannot be cancelled again.'

    # Admins can cancel at any time on behalf of customers
    if user.is_staff:
        return True, ''

    from core.utils.dates import is_within_cancellation_window
    if not is_within_cancellation_window():
        return False, 'Cancellations are no longer accepted — the event is less than 72 hours away.'

    return True, ''


def get_refund_eligibility(ticket, user):
    """
    Determine whether a refund will be issued if this ticket is cancelled.
    Separate from cancellability — a ticket can be cancelled without a refund.
    Returns (will_refund: bool, reason: str).
    """
    if getattr(ticket, 'is_guest_purchase', False) and not user.is_staff:
        return False, 'Guest purchases are not eligible for a refund.'
    if not ticket.category.is_refundable:
        return False, f'{ticket.category.name} tickets are non-refundable.'
    return True, ''


def can_amend_ticket(ticket):
    """Check whether a ticket can be amended/upgraded."""
    from core.constants import TICKET_ACTIVE, TICKET_AMENDABLE, TICKET_VIP
    if ticket.status != TICKET_ACTIVE:
        return False, 'Only active tickets can be upgraded.'
    if ticket.category.category_type == TICKET_VIP:
        return False, 'VIP is the highest tier — there is no upgrade available.'
    if not TICKET_AMENDABLE.get(ticket.category.category_type, False):
        return False, f'{ticket.category.name} tickets cannot be upgraded.'
    return True, ''
