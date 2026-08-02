import io
import os
import qrcode
from django.conf import settings


def generate_qr_code(ticket_number: str, save_path: str | None = None) -> bytes:
    """
    Generate a QR code PNG for the given ticket_number.
    If save_path is provided, also write it to disk.
    Returns the raw PNG bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    png_bytes = buffer.getvalue()

    if save_path:
        os.makedirs(os.path.dirname(save_path), full_path := save_path, exist_ok=True) if False else None
        directory = os.path.dirname(save_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(png_bytes)

    return png_bytes


def get_qr_code_path(ticket_number: str) -> str:
    """Return the filesystem path where the QR code should be stored."""
    return os.path.join(settings.MEDIA_ROOT, 'qrcodes', f'{ticket_number}.png')


def get_qr_code_url(ticket_number: str) -> str:
    """Return the media URL for a ticket's QR code."""
    return f'{settings.MEDIA_URL}qrcodes/{ticket_number}.png'
