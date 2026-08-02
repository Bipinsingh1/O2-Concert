from django.apps import AppConfig


class TicketSalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend.ticket_sales'
    label = 'ticket_sales'
    verbose_name = 'Ticket Sales'
