from datetime import datetime, date, time
from django.utils import timezone
from django.conf import settings


def get_event_date() -> date:
    return date.fromisoformat(settings.EVENT_DATE)


def get_sales_start_date() -> date:
    return date.fromisoformat(settings.TICKET_SALES_START)


def get_purchase_discount_percent(purchase_date: datetime | None = None) -> int:
    """
    Return the discount percentage for a given purchase datetime.
    Rules (registered customers only):
      July   → 10%
      August → 5%
      September → 10%
      After September → 0%
    """
    if purchase_date is None:
        purchase_date = timezone.now()
    month = purchase_date.month
    discount_map = getattr(settings, 'DISCOUNT_BY_MONTH', {7: 10, 8: 5, 9: 10})
    return discount_map.get(month, 0)


def is_within_cancellation_window() -> bool:
    """
    Returns True if we are still within the cancellation window
    (i.e. at least CANCELLATION_WINDOW_HOURS hours before the event).
    """
    event_dt = timezone.make_aware(
        datetime.combine(get_event_date(), time(19, 0))  # Doors open at 19:00
    )
    now = timezone.now()
    window_hours = getattr(settings, 'CANCELLATION_WINDOW_HOURS', 72)
    delta = event_dt - now
    return delta.total_seconds() / 3600 >= window_hours


def sales_are_open() -> bool:
    today = timezone.now().date()
    return today >= get_sales_start_date()
