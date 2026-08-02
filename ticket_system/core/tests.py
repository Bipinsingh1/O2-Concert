"""
Tests for core permissions, decorators, and discount logic.
"""
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.constants import (
    TICKET_STANDARD, TICKET_VIP, TICKET_RESTRICTED, TICKET_GROUP,
    TICKET_ACTIVE, TICKET_CANCELLED,
)
from core.permissions import can_cancel_ticket, get_refund_eligibility, can_amend_ticket
from frontend.ticket_sales.models import TicketCategory, Ticket

User = get_user_model()


def make_user(email, is_staff=False, is_active=True):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='Test',
        last_name='User',
        is_staff=is_staff,
        is_active=is_active,
    )


def make_category(cat_type, price, refundable=True, amendable=True):
    names = {
        TICKET_STANDARD: 'Standard', TICKET_VIP: 'VIP',
        TICKET_RESTRICTED: 'Restricted', TICKET_GROUP: 'Group',
    }
    return TicketCategory.objects.create(
        category_type=cat_type, name=names[cat_type],
        price=Decimal(str(price)), is_refundable=refundable,
        is_amendable=amendable, total_available=100,
    )


def make_ticket(number, category, owner=None, guest=False, status=TICKET_ACTIVE, amount=None):
    return Ticket.objects.create(
        ticket_number=number,
        category=category,
        owner=owner,
        guest_name='Guest User' if guest else '',
        guest_email='guest@test.com' if guest else '',
        is_guest_purchase=guest,
        status=status,
        amount_paid=amount or category.price,
        original_price=category.price,
    )


class CancellationPermissionTests(TestCase):
    def setUp(self):
        self.user = make_user('customer@test.com')
        self.staff = make_user('staff@test.com', is_staff=True)
        self.cat = make_category(TICKET_STANDARD, '40.00')
        self.ticket = make_ticket('T-STD-001', self.cat, owner=self.user)

    def test_can_cancel_active_ticket_within_window(self):
        with patch('core.utils.dates.is_within_cancellation_window', return_value=True):
            can, reason = can_cancel_ticket(self.ticket, self.user)
        self.assertTrue(can)
        self.assertEqual(reason, '')

    def test_cannot_cancel_outside_window(self):
        with patch('core.utils.dates.is_within_cancellation_window', return_value=False):
            can, reason = can_cancel_ticket(self.ticket, self.user)
        self.assertFalse(can)
        self.assertIn('72 hours', reason)

    def test_admin_bypasses_window(self):
        with patch('core.utils.dates.is_within_cancellation_window', return_value=False):
            can, _ = can_cancel_ticket(self.ticket, self.staff)
        self.assertTrue(can)

    def test_cannot_cancel_already_cancelled_ticket(self):
        self.ticket.status = TICKET_CANCELLED
        self.ticket.save()
        can, reason = can_cancel_ticket(self.ticket, self.user)
        self.assertFalse(can)
        self.assertIn('already been cancelled', reason)


class RefundEligibilityTests(TestCase):
    def setUp(self):
        self.user = make_user('customer@test.com')
        self.std_cat = make_category(TICKET_STANDARD, '40.00', refundable=True)
        self.vip_cat = make_category(TICKET_VIP, '250.00', refundable=False)
        self.res_cat = make_category(TICKET_RESTRICTED, '30.00', refundable=False)

    def test_refundable_category_registered_user(self):
        ticket = make_ticket('T-STD-001', self.std_cat, owner=self.user)
        will_refund, _ = get_refund_eligibility(ticket, self.user)
        self.assertTrue(will_refund)

    def test_non_refundable_category(self):
        ticket = make_ticket('T-VIP-001', self.vip_cat, owner=self.user)
        will_refund, reason = get_refund_eligibility(ticket, self.user)
        self.assertFalse(will_refund)
        self.assertIn('non-refundable', reason)

    def test_guest_purchase_not_refundable(self):
        ticket = make_ticket('T-GUEST-001', self.std_cat, guest=True)
        will_refund, _ = get_refund_eligibility(ticket, self.user)
        self.assertFalse(will_refund)


class AmendPermissionTests(TestCase):
    def setUp(self):
        self.user = make_user('customer@test.com')
        self.std_cat = make_category(TICKET_STANDARD, '40.00', amendable=True)
        self.vip_cat = make_category(TICKET_VIP, '250.00', amendable=False)
        self.res_cat = make_category(TICKET_RESTRICTED, '30.00', amendable=False)

    def test_can_amend_active_standard_ticket(self):
        ticket = make_ticket('T-STD-001', self.std_cat, owner=self.user)
        can, _ = can_amend_ticket(ticket)
        self.assertTrue(can)

    def test_cannot_amend_vip_ticket(self):
        ticket = make_ticket('T-VIP-001', self.vip_cat, owner=self.user)
        can, reason = can_amend_ticket(ticket)
        self.assertFalse(can)
        self.assertIn('highest tier', reason)

    def test_cannot_amend_cancelled_ticket(self):
        ticket = make_ticket('T-STD-002', self.std_cat, owner=self.user, status=TICKET_CANCELLED)
        can, reason = can_amend_ticket(ticket)
        self.assertFalse(can)
        self.assertIn('active', reason)

    def test_cannot_amend_restricted_ticket(self):
        ticket = make_ticket('T-RES-001', self.res_cat, owner=self.user)
        can, reason = can_amend_ticket(ticket)
        self.assertFalse(can)


class AdminDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = make_user('customer@test.com')
        self.staff = make_user('staff@test.com', is_staff=True)
        self.inactive_staff = make_user('inactive@test.com', is_staff=True, is_active=False)

    def test_non_staff_redirected(self):
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, 302)

    def test_staff_can_access(self):
        self.client.force_login(self.staff)
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_inactive_staff_blocked(self):
        self.client.force_login(self.inactive_staff)
        response = self.client.get('/admin/dashboard/')
        self.assertNotEqual(response.status_code, 200)
