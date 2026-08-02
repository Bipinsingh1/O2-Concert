from django.apps import AppConfig


class TicketAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.ticket_admin'
    label = 'ticket_admin'
    verbose_name = 'Ticket Administration'
