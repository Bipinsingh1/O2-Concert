"""
Tests for discount logic, ticket availability, and category remaining counts.
"""
from decimal import Decimal
from unittest.mock import patch
from datetime import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.constants import (
    TICKET_STANDARD, TICKET_VIP, TICKET_RESTRICTED, TICKET_GROUP,
    TICKET_ACTIVE, VIP_INVENTORY, OTHER_INVENTORY,
)
from frontend.ticket_sales.models import TicketCategory, Ticket
from frontend.ticket_sales.services.discount_service import calculate_discounted_price

User = get_user_model()


def make_user(email, is_staff=False):
    return User.objects.create_user(
        username=email.split('@')[0], email=email,
        password='pass123', first_name='A', last_name='B', is_staff=is_staff,
    )


def make_category(cat_type, price='40.00'):
    names = {
        TICKET_STANDARD: 'Standard', TICKET_VIP: 'VIP',
        TICKET_RESTRICTED: 'Restricted', TICKET_GROUP: 'Group',
    }
    return TicketCategory.objects.create(
        category_type=cat_type, name=names[cat_type],
        price=Decimal(price), is_refundable=True,
        is_amendable=True, total_available=100,
    )


class DiscountServiceTests(TestCase):
    def setUp(self):
        self.user = make_user('customer@test.com')
        self.staff = make_user('staff@test.com', is_staff=True)
        self.price = Decimal('40.00')

    def _discount_in_month(self, month):
        fake_now = timezone.make_aware(datetime(2026, month, 15))
        with patch('frontend.ticket_sales.services.discount_service.timezone') as mock_tz:
            mock_tz.now.return_value = fake_now
            return calculate_discounted_price(self.price, self.user)

    def test_guest_gets_no_discount(self):
        result = calculate_discounted_price(self.price, None)
        self.assertEqual(result['discount_percent'], 0)
        self.assertEqual(result['final_price'], self.price)

    def test_staff_gets_no_discount(self):
        result = calculate_discounted_price(self.price, self.staff)
        self.assertEqual(result['discount_percent'], 0)

    def test_july_discount_10_percent(self):
        result = self._discount_in_month(7)
        self.assertEqual(result['discount_percent'], 10)
        self.assertEqual(result['final_price'], Decimal('36.00'))

    def test_august_discount_5_percent(self):
        result = self._discount_in_month(8)
        self.assertEqual(result['discount_percent'], 5)
        self.assertEqual(result['final_price'], Decimal('38.00'))

    def test_september_discount_10_percent(self):
        result = self._discount_in_month(9)
        self.assertEqual(result['discount_percent'], 10)
        self.assertEqual(result['final_price'], Decimal('36.00'))

    def test_october_no_discount(self):
        result = self._discount_in_month(10)
        self.assertEqual(result['discount_percent'], 0)
        self.assertEqual(result['final_price'], self.price)

    def test_discount_amount_correct(self):
        result = self._discount_in_month(7)
        self.assertEqual(result['discount_amount'], Decimal('4.00'))
        self.assertEqual(result['original_price'], self.price)


class TicketAvailabilityTests(TestCase):
    def setUp(self):
        self.std_cat = make_category(TICKET_STANDARD)
        self.vip_cat = make_category(TICKET_VIP, '250.00')
        self.res_cat = make_category(TICKET_RESTRICTED, '30.00')

    def _make_ticket(self, cat, n):
        return Ticket.objects.create(
            ticket_number=f'T-{cat.category_type.upper()}-{n:04d}',
            category=cat, status=TICKET_ACTIVE,
            amount_paid=cat.price, original_price=cat.price,
        )

    def test_category_is_available_when_stock_exists(self):
        self.assertTrue(self.std_cat.is_available)

    def test_vip_remaining_decreases_with_sold_tickets(self):
        for i in range(5):
            self._make_ticket(self.vip_cat, i)
        self.assertEqual(self.vip_cat.remaining, VIP_INVENTORY - 5)

    def test_non_vip_share_pool(self):
        """Standard and Restricted tickets draw from the same 900-seat pool."""
        for i in range(10):
            self._make_ticket(self.std_cat, i)
        for i in range(5):
            self._make_ticket(self.res_cat, i)
        # Both categories should reflect the shared pool depletion
        self.assertEqual(self.std_cat.remaining, OTHER_INVENTORY - 15)
        self.assertEqual(self.res_cat.remaining, OTHER_INVENTORY - 15)

    def test_category_unavailable_when_pool_full(self):
        """Simulate the non-VIP pool being exhausted."""
        # Use bulk_create for speed — no signals/QR needed
        Ticket.objects.bulk_create([
            Ticket(
                ticket_number=f'T-STD-{i:05d}',
                category=self.std_cat,
                status=TICKET_ACTIVE,
                amount_paid=self.std_cat.price,
                original_price=self.std_cat.price,
            )
            for i in range(OTHER_INVENTORY)
        ])
        self.assertFalse(self.std_cat.is_available)
        self.assertEqual(self.std_cat.remaining, 0)
