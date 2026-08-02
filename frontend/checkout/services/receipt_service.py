from core.utils.email import send_ticket_email
from core.utils.pdf import save_ticket_pdf


def send_receipt(order):
    """Generate PDF and send email receipt after successful payment."""
    ticket = order.ticket
    save_ticket_pdf(ticket)
    send_ticket_email(ticket)
