from decimal import Decimal
from django.utils import timezone
from core.utils.dates import get_purchase_discount_percent
from core.utils.helpers import apply_discount


def calculate_discounted_price(price: Decimal, user=None) -> dict:
    """
    Apply purchase-date discount for registered users.
    Returns a dict with: original_price, discount_percent, discount_amount, final_price.
    """
    if user is None or not user.is_authenticated or user.is_staff:
        return {
            'original_price': price,
            'discount_percent': 0,
            'discount_amount': Decimal('0.00'),
            'final_price': price,
        }

    now = timezone.now()
    discount_percent = get_purchase_discount_percent(now)
    final_price = apply_discount(price, discount_percent)
    discount_amount = price - final_price

    return {
        'original_price': price,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'final_price': final_price,
    }
