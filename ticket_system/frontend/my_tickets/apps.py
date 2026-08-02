from django.apps import AppConfig


class MyTicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend.my_tickets'
    label = 'my_tickets'
    verbose_name = 'My Tickets'
