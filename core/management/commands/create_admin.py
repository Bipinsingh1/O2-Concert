from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a default admin (staff) user for development'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return
        User.objects.create_superuser(
            username='admin',
            email='admin@o2arena.com',
            password='Admin1234!',
            first_name='Arena',
            last_name='Admin',
        )
        self.stdout.write(self.style.SUCCESS('Admin user created: admin / Admin1234!'))
