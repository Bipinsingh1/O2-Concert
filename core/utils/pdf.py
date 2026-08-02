import io
import os
from decimal import Decimal
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.conf import settings


def generate_ticket_pdf(ticket) -> bytes:
    """
    Generate a PDF ticket for the given Ticket instance.
    Returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6, alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=13, textColor=colors.HexColor('#e94560'),
        spaceAfter=4, alignment=TA_CENTER,
    )
    normal_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=11, spaceAfter=4,
    )

    elements = []

    # Header
    elements.append(Paragraph('THE O2 ARENA', title_style))
    elements.append(Paragraph(settings.EVENT_NAME, subtitle_style))
    elements.append(Spacer(1, 0.5 * cm))

    # Ticket info table
    holders = list(ticket.holders.all())
    holder_names = ', '.join(h.name for h in holders) if holders else (
        ticket.owner.get_full_name() if ticket.owner else ticket.guest_name or 'N/A'
    )

    data = [
        ['Ticket Number', ticket.ticket_number],
        ['Ticket Type', ticket.category.name],
        ['Event Date', '30 November 2026'],
        ['Venue', 'The O2 Arena, London'],
        ['Date of Purchase', ticket.purchase_date.strftime('%d %B %Y %H:%M')],
        ['Amount Paid', f'£{ticket.amount_paid:.2f}'],
        ['Holder(s)', holder_names],
    ]

    table = Table(data, colWidths=[5 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f5f5f5')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.8 * cm))

    # QR code
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'{ticket.ticket_number}.png')
    if os.path.exists(qr_path):
        qr_img = Image(qr_path, width=4 * cm, height=4 * cm)
        qr_img.hAlign = 'CENTER'
        elements.append(qr_img)

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph('Scan the QR code at the venue entrance.', ParagraphStyle(
        'Footer', parent=styles['Normal'], fontSize=9,
        textColor=colors.grey, alignment=TA_CENTER,
    )))

    doc.build(elements)
    return buffer.getvalue()


def save_ticket_pdf(ticket) -> str:
    """Save PDF to media/generated_tickets/ and return the file path."""
    directory = os.path.join(settings.MEDIA_ROOT, 'generated_tickets')
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f'{ticket.ticket_number}.pdf')
    pdf_bytes = generate_ticket_pdf(ticket)
    with open(path, 'wb') as f:
        f.write(pdf_bytes)
    return path
