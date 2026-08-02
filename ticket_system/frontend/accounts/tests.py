from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsTestCase(TestCase):
    def test_register_user(self):
        response = self.client.post('/accounts/register/', {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)
