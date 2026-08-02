from django.core.management.base import BaseCommand
from frontend.ticket_sales.models import TicketCategory
from core.constants import (
    TICKET_RESTRICTED, TICKET_STANDARD, TICKET_VIP, TICKET_GROUP,
    TICKET_PRICES, TICKET_REFUNDABLE, TICKET_AMENDABLE,
    VIP_INVENTORY, OTHER_INVENTORY,
)


class Command(BaseCommand):
    help = 'Seed the database with ticket categories for the O2 Arena event'

    def handle(self, *args, **options):
        categories = [
            {
                'category_type': TICKET_RESTRICTED,
                'name': 'Single Adult Restricted',
                'description': 'Restricted view. Non-refundable and non-amendable.',
                'price': TICKET_PRICES[TICKET_RESTRICTED],
                'is_refundable': TICKET_REFUNDABLE[TICKET_RESTRICTED],
                'is_amendable': TICKET_AMENDABLE[TICKET_RESTRICTED],
                'total_available': OTHER_INVENTORY // 3,
            },
            {
                'category_type': TICKET_STANDARD,
                'name': 'Single Adult Standard',
                'description': 'Standard seating. Refundable and amendable for a fee.',
                'price': TICKET_PRICES[TICKET_STANDARD],
                'is_refundable': TICKET_REFUNDABLE[TICKET_STANDARD],
                'is_amendable': TICKET_AMENDABLE[TICKET_STANDARD],
                'total_available': OTHER_INVENTORY // 3,
            },
            {
                'category_type': TICKET_VIP,
                'name': 'Single Adult VIP',
                'description': 'VIP experience. Non-refundable but amendable for a fee.',
                'price': TICKET_PRICES[TICKET_VIP],
                'is_refundable': TICKET_REFUNDABLE[TICKET_VIP],
                'is_amendable': TICKET_AMENDABLE[TICKET_VIP],
                'total_available': VIP_INVENTORY,
            },
            {
                'category_type': TICKET_GROUP,
                'name': 'Group Standard',
                'description': 'Up to 5 people (adults and/or children). Refundable and amendable.',
                'price': TICKET_PRICES[TICKET_GROUP],
                'is_refundable': TICKET_REFUNDABLE[TICKET_GROUP],
                'is_amendable': TICKET_AMENDABLE[TICKET_GROUP],
                'total_available': OTHER_INVENTORY // 3,
            },
        ]

        for cat_data in categories:
            obj, created = TicketCategory.objects.update_or_create(
                category_type=cat_data['category_type'],
                defaults=cat_data,
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status}: {obj.name}'))

        self.stdout.write(self.style.SUCCESS('Ticket categories seeded successfully.'))
