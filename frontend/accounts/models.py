from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
    """Extended user model for O2 Arena ticket system."""
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def __str__(self):
        return self.email

    @property
    def is_registered_customer(self):
        return self.is_authenticated and not self.is_staff
