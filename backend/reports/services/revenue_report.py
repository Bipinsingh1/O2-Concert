from django.db.models import Sum
from frontend.checkout.models import Payment, Refund
from core.constants import PAYMENT_SUCCEEDED, PAYMENT_REFUNDED


def get_revenue_report() -> dict:
    # Total revenue = all payments that were successfully charged,
    # including ones later refunded (we still received that money initially).
    total_revenue = Payment.objects.filter(
        status__in=[PAYMENT_SUCCEEDED, PAYMENT_REFUNDED]
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total refunded = sum of all Refund records (partial refunds after 20% fee)
    total_refunded = Refund.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Net = what we actually kept after paying out refunds
    net_revenue = total_revenue - total_refunded

    return {
        'total_revenue': total_revenue,
        'total_refunded': total_refunded,
        'net_revenue': net_revenue,
    }
