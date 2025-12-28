"""
Management command to reset weekly and monthly points.
Should be run via cron job:
- Weekly reset: Every Monday at 00:00
- Monthly reset: First day of each month at 00:00

Example crontab entries:
0 0 * * 1 cd /path/to/project && python manage.py reset_points --weekly
0 0 1 * * cd /path/to/project && python manage.py reset_points --monthly
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from signlang.models import UserPoints


class Command(BaseCommand):
    help = 'Reset weekly and/or monthly points for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weekly',
            action='store_true',
            help='Reset weekly points',
        )
        parser.add_argument(
            '--monthly',
            action='store_true',
            help='Reset monthly points',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reset both weekly and monthly points',
        )
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Automatically determine what needs to be reset based on date',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        reset_weekly = options.get('weekly', False)
        reset_monthly = options.get('monthly', False)
        reset_all = options.get('all', False)
        auto_mode = options.get('auto', False)

        if auto_mode:
            # Monday = 0 in weekday()
            if today.weekday() == 0:
                reset_weekly = True
                self.stdout.write('Auto-detected: Monday - resetting weekly points')
            # First day of month
            if today.day == 1:
                reset_monthly = True
                self.stdout.write('Auto-detected: First of month - resetting monthly points')

        if reset_all:
            reset_weekly = True
            reset_monthly = True

        if not reset_weekly and not reset_monthly:
            self.stdout.write(self.style.WARNING(
                'No reset option specified. Use --weekly, --monthly, --all, or --auto'
            ))
            return

        user_points = UserPoints.objects.all()
        count = user_points.count()

        if reset_weekly:
            self.stdout.write(f'Resetting weekly points for {count} users...')
            for points in user_points:
                points.reset_weekly()
            self.stdout.write(self.style.SUCCESS(f'Weekly points reset for {count} users'))

        if reset_monthly:
            self.stdout.write(f'Resetting monthly points for {count} users...')
            for points in user_points:
                points.reset_monthly()
            self.stdout.write(self.style.SUCCESS(f'Monthly points reset for {count} users'))

        self.stdout.write(self.style.SUCCESS('Points reset complete!'))
