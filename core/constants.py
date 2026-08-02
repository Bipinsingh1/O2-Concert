from decimal import Decimal

# ── Ticket Categories ─────────────────────────────────────────────────────────
TICKET_RESTRICTED = 'restricted'
TICKET_STANDARD = 'standard'
TICKET_VIP = 'vip'
TICKET_GROUP = 'group'

TICKET_TYPES = [
    (TICKET_RESTRICTED, 'Single Adult Restricted'),
    (TICKET_STANDARD, 'Single Adult Standard'),
    (TICKET_VIP, 'Single Adult VIP'),
    (TICKET_GROUP, 'Group Standard'),
]

TICKET_PRICES = {
    TICKET_RESTRICTED: Decimal('30.00'),
    TICKET_STANDARD: Decimal('40.00'),
    TICKET_VIP: Decimal('250.00'),
    TICKET_GROUP: Decimal('120.00'),
}

TICKET_REFUNDABLE = {
    TICKET_RESTRICTED: False,
    TICKET_STANDARD: True,
    TICKET_VIP: False,
    TICKET_GROUP: True,
}

TICKET_AMENDABLE = {
    TICKET_RESTRICTED: False,
    TICKET_STANDARD: True,
    TICKET_VIP: False,  # VIP is the top tier — no upgrade path exists
    TICKET_GROUP: True,
}

# Upgrade path: key can be upgraded to any value in its list
TICKET_UPGRADE_PATHS = {
    TICKET_RESTRICTED: [TICKET_STANDARD, TICKET_VIP, TICKET_GROUP],
    TICKET_STANDARD: [TICKET_VIP],
    TICKET_GROUP: [TICKET_VIP],
    TICKET_VIP: [],  # Cannot upgrade VIP
}

# Non-VIP types share a single pool of OTHER_INVENTORY seats
NON_VIP_CATEGORY_TYPES = [TICKET_RESTRICTED, TICKET_STANDARD, TICKET_GROUP]

# ── Inventory ─────────────────────────────────────────────────────────────────
VIP_INVENTORY = 100
OTHER_INVENTORY = 900

# ── Order / Payment Status ────────────────────────────────────────────────────
ORDER_PENDING = 'pending'
ORDER_COMPLETED = 'completed'
ORDER_CANCELLED = 'cancelled'
ORDER_REFUNDED = 'refunded'
ORDER_STATUSES = [
    (ORDER_PENDING, 'Pending'),
    (ORDER_COMPLETED, 'Completed'),
    (ORDER_CANCELLED, 'Cancelled'),
    (ORDER_REFUNDED, 'Refunded'),
]

PAYMENT_PENDING = 'pending'
PAYMENT_SUCCEEDED = 'succeeded'
PAYMENT_FAILED = 'failed'
PAYMENT_REFUNDED = 'refunded'
PAYMENT_STATUSES = [
    (PAYMENT_PENDING, 'Pending'),
    (PAYMENT_SUCCEEDED, 'Succeeded'),
    (PAYMENT_FAILED, 'Failed'),
    (PAYMENT_REFUNDED, 'Refunded'),
]

# ── Ticket Status ─────────────────────────────────────────────────────────────
TICKET_ACTIVE = 'active'
TICKET_CANCELLED = 'cancelled'
TICKET_AMENDED = 'amended'       # legacy — no longer set by upgrade flow; kept for DB compatibility
TICKET_CHECKED_IN = 'checked_in' # ticket has been scanned at the door
TICKET_STATUSES = [
    (TICKET_ACTIVE, 'Active'),
    (TICKET_CANCELLED, 'Cancelled'),
    (TICKET_AMENDED, 'Amended'),
    (TICKET_CHECKED_IN, 'Checked In'),
]

# ── Age Groups ────────────────────────────────────────────────────────────────
AGE_ADULT = 'adult'
AGE_CHILD = 'child'
AGE_GROUPS = [
    (AGE_ADULT, 'Adult'),
    (AGE_CHILD, 'Child'),
]

GROUP_MAX_MEMBERS = 5

# ── Discount Rules ────────────────────────────────────────────────────────────
DISCOUNT_BY_MONTH = {7: 10, 8: 5, 9: 10}
REFUND_FEE_PERCENT = Decimal('20')
CANCELLATION_WINDOW_HOURS = 72

# ── Event ─────────────────────────────────────────────────────────────────────
EVENT_NAME = 'Dua Lipa Live at The O2'
EVENT_DATE_STR = '2026-11-30'
SALES_START_DATE_STR = '2026-07-01'
VENUE_NAME = 'The O2 Arena, London'
