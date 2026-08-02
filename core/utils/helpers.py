from decimal import Decimal, ROUND_HALF_UP


def apply_discount(price: Decimal, discount_percent: int) -> Decimal:
    """Apply a percentage discount to a price and return the discounted amount."""
    if discount_percent <= 0:
        return price
    discount = price * Decimal(discount_percent) / Decimal('100')
    discounted = price - discount
    return discounted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_refund_amount(amount_paid: Decimal, fee_percent: Decimal = Decimal('20')) -> Decimal:
    """Calculate refund after deducting the cancellation fee."""
    fee = amount_paid * fee_percent / Decimal('100')
    refund = amount_paid - fee
    return refund.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_currency(amount: Decimal) -> str:
    return f'£{amount:,.2f}'
