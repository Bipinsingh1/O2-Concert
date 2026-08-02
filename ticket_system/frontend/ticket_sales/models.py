from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from core.constants import TICKET_TYPES, TICKET_STATUSES, AGE_GROUPS, TICKET_ACTIVE, NON_VIP_CATEGORY_TYPES
import logging

logger = logging.getLogger(__name__)


class TicketCategory(TimeStampedModel):
    """Defines the 4 ticket types available for the event."""
    category_type = models.CharField(max_length=20, choices=TICKET_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_refundable = models.BooleanField(default=False)
    is_amendable = models.BooleanField(default=False)
    total_available = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ticket Category'
        verbose_name_plural = 'Ticket Categories'
        ordering = ['price']

    def __str__(self):
        return self.name

    @property
    def sold_count(self):
        # Use annotated value when available (set by annotate_remaining helper)
        if 'sold' in self.__dict__:
            return self.__dict__['sold']
        return self.tickets.filter(status=TICKET_ACTIVE).count()

    @property
    def remaining(self):
        # Use pre-computed value when available (set by annotate_remaining helper)
        # avoids N+1 queries on list pages
        if '_remaining_cache' in self.__dict__:
            return self.__dict__['_remaining_cache']
        from core.constants import TICKET_VIP, VIP_INVENTORY, OTHER_INVENTORY
        if self.category_type == TICKET_VIP:
            return max(0, VIP_INVENTORY - self.sold_count)
        # Restricted, Standard and Group share a single pool of 900 tickets
        from django.apps import apps
        Ticket = apps.get_model('ticket_sales', 'Ticket')
        non_vip_sold = Ticket.objects.filter(
            status=TICKET_ACTIVE,
            category__category_type__in=NON_VIP_CATEGORY_TYPES,
        ).count()
        return max(0, OTHER_INVENTORY - non_vip_sold)

    @property
    def is_available(self):
        return self.remaining > 0


class Ticket(TimeStampedModel):
    """An individual ticket purchased for the event."""
    ticket_number = models.CharField(max_length=30, unique=True, db_index=True)
    category = models.ForeignKey(TicketCategory, on_delete=models.PROTECT, related_name='tickets')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tickets',
    )
    # Guest fields (used when owner is null)
    guest_name = models.CharField(max_length=200, blank=True)
    guest_email = models.EmailField(blank=True)
    is_guest_purchase = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=TICKET_STATUSES, default=TICKET_ACTIVE, db_index=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return self.ticket_number

    @property
    def customer_name(self):
        if self.owner:
            return self.owner.get_full_name()
        return self.guest_name or 'Guest'

    @property
    def customer_email(self):
        return self.owner.email if self.owner else self.guest_email


class WaitlistEntry(models.Model):
    """A customer waiting for a ticket to become available via cancellation."""
    category = models.ForeignKey(
        TicketCategory, on_delete=models.CASCADE, related_name='waitlist'
    )
    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='waitlist_entries',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        unique_together = [('category', 'email')]
        ordering = ['created_at']

    def __str__(self):
        return f'{self.email} → {self.category.name}'


class TicketHolder(models.Model):
    """Named attendee on a ticket (especially group tickets)."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='holders')
    name = models.CharField(max_length=200)
    age_group = models.CharField(max_length=10, choices=AGE_GROUPS, default='adult')

    def __str__(self):
        return f'{self.name} ({self.age_group})'
