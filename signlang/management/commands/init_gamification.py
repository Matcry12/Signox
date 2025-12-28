from django.core.management.base import BaseCommand
from signlang.gamification import initialize_badges, ensure_user_gamification
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initialize gamification system with default badges and user records'

    def handle(self, *args, **options):
        self.stdout.write('Initializing gamification system...')

        # Create default badges
        self.stdout.write('Creating default badges...')
        initialize_badges()
        self.stdout.write(self.style.SUCCESS('Default badges created!'))

        # Initialize gamification for existing users
        self.stdout.write('Initializing user gamification records...')
        users = User.objects.all()
        for user in users:
            ensure_user_gamification(user)
        self.stdout.write(self.style.SUCCESS(f'Initialized {users.count()} users!'))

        self.stdout.write(self.style.SUCCESS('Gamification system initialized successfully!'))
