from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from core.constants import ORDER_STATUSES, PAYMENT_STATUSES, ORDER_PENDING, PAYMENT_PENDING
from frontend.ticket_sales.models import Ticket


class Order(TimeStampedModel):
    order_number = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders',
    )
    guest_email = models.EmailField(blank=True)
    ticket = models.OneToOneField(Ticket, on_delete=models.PROTECT, related_name='order', null=True, blank=True)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default=ORDER_PENDING, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number


class Payment(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default=PAYMENT_PENDING)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'Payment for {self.order.order_number}'


class Refund(TimeStampedModel):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='refunds')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.TextField(blank=True)
    stripe_refund_id = models.CharField(max_length=200, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    def __str__(self):
        return f'Refund £{self.amount} for {self.payment.order.order_number}'
