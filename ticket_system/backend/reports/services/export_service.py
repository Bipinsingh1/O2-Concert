import csv
from frontend.ticket_sales.models import Ticket


class _EchoBuffer:
    """A write-only buffer that returns what is written — used for streaming CSV."""
    def write(self, value):
        return value


def generate_ticket_rows():
    """
    Generator that yields CSV-encoded rows one at a time.
    Use with StreamingHttpResponse to avoid loading all tickets into memory.
    """
    buffer = _EchoBuffer()
    writer = csv.writer(buffer)
    yield writer.writerow([
        'Ticket Number', 'Category', 'Status', 'Customer Name',
        'Customer Email', 'Guest Purchase', 'Amount Paid',
        'Discount %', 'Purchase Date',
    ])
    qs = (
        Ticket.objects
        .select_related('category', 'owner')
        .order_by('-purchase_date')
        .iterator(chunk_size=500)
    )
    for ticket in qs:
        yield writer.writerow([
            ticket.ticket_number,
            ticket.category.name,
            ticket.status,
            ticket.customer_name,
            ticket.customer_email,
            'Yes' if ticket.is_guest_purchase else 'No',
            f'£{ticket.amount_paid:.2f}',
            f'{ticket.discount_percent}%',
            ticket.purchase_date.strftime('%Y-%m-%d %H:%M'),
        ])
