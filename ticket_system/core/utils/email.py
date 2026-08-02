import os
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from core.utils.pdf import save_ticket_pdf


def send_ticket_email(ticket):
    """
    Send the purchased ticket as a PDF attachment to the customer's email.
    """
    recipient = ticket.owner.email if ticket.owner else ticket.guest_email
    if not recipient:
        return

    context = {
        'ticket': ticket,
        'event_name': settings.EVENT_NAME,
    }
    subject = f'Your Ticket – {settings.EVENT_NAME}'
    body = render_to_string('emails/ticket_confirmation.html', context)

    # Ensure the PDF exists
    pdf_path = save_ticket_pdf(ticket)

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.content_subtype = 'html'

    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            email.attach(f'{ticket.ticket_number}.pdf', f.read(), 'application/pdf')

    email.send(fail_silently=True)


def send_cancellation_email(ticket, refund_amount=None):
    """Notify the customer their ticket has been cancelled."""
    recipient = ticket.owner.email if ticket.owner else ticket.guest_email
    if not recipient:
        return

    context = {
        'ticket': ticket,
        'refund_amount': refund_amount,
        'event_name': settings.EVENT_NAME,
    }
    subject = f'Ticket Cancellation – {settings.EVENT_NAME}'
    body = render_to_string('emails/ticket_cancellation.html', context)

    email = EmailMessage(
        subject=subject, body=body,
        from_email=settings.DEFAULT_FROM_EMAIL, to=[recipient],
    )
    email.content_subtype = 'html'
    email.send(fail_silently=True)
