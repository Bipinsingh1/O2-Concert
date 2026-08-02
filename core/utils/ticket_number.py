import uuid
import hashlib


def generate_ticket_number():
    """Generate a unique ticket number: O2-XXXXXXXXXXXXXXXX (16 hex chars)."""
    raw = uuid.uuid4().hex.upper()
    return f'O2-{raw[:16]}'


def generate_order_number():
    """Generate a unique order number: ORD-XXXXXXXXXX."""
    raw = uuid.uuid4().hex.upper()
    return f'ORD-{raw[:10]}'
