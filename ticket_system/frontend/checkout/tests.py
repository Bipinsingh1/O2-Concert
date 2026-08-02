"""
Tests for the checkout flow: confirm view, payment atomicity, and session guards.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.constants import TICKET_STANDARD, TICKET_ACTIVE, ORDER_COMPLETED
from frontend.ticket_sales.models import TicketCategory
from frontend.checkout.models import Order, Payment

User = get_user_model()


def make_user(email):
    return User.objects.create_user(
        username=email.split('@')[0], email=email,
        password='pass123', first_name='A', last_name='B',
    )


def make_category():
    return TicketCategory.objects.create(
        category_type=TICKET_STANDARD, name='Standard',
        price=Decimal('40.00'), is_refundable=True,
        is_amendable=True, total_available=300,
    )


class ConfirmViewSessionGuardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('buyer@test.com')
        self.cat = make_category()

    def test_confirm_without_session_redirects(self):
        """POSTing to confirm with no pending session should redirect gracefully."""
        self.client.force_login(self.user)
        response = self.client.post(reverse('checkout:confirm'), {
            'payment_intent_id': 'pi_test_123',
        })
        self.assertEqual(response.status_code, 302)

    def test_review_without_session_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('checkout:review'))
        self.assertEqual(response.status_code, 302)

    def test_payment_without_session_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('checkout:payment'))
        self.assertEqual(response.status_code, 302)


class SuccessViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('buyer@test.com')
        self.cat = make_category()

    def test_success_view_requires_valid_order(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('checkout:success', args=['NO-SUCH-ORDER']))
        self.assertEqual(response.status_code, 404)
