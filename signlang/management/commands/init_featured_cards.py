from django.core.management.base import BaseCommand
from signlang.models import FeaturedCard


DEFAULT_CARDS = [
    # Common Sentences
    {
        'title': 'Daily Communication',
        'section': 'common_sentences',
        'icon': 'fa-comment-dots',
        'color': 'blue',
        'link': '/lessons/?category=daily',
        'order': 1,
    },
    {
        'title': 'School Communication',
        'section': 'common_sentences',
        'icon': 'fa-graduation-cap',
        'color': 'teal',
        'link': '/lessons/?category=school',
        'order': 2,
    },
    {
        'title': 'Work Communication',
        'section': 'common_sentences',
        'icon': 'fa-briefcase',
        'color': 'indigo',
        'link': '/lessons/?category=work',
        'order': 3,
    },
]


class Command(BaseCommand):
    help = 'Initialize default featured cards for home page'

    def handle(self, *args, **options):
        self.stdout.write('Creating default featured cards...')

        for card_data in DEFAULT_CARDS:
            card, created = FeaturedCard.objects.get_or_create(
                title=card_data['title'],
                section=card_data['section'],
                defaults=card_data
            )
            if created:
                self.stdout.write(f'  Created: {card.title}')
            else:
                self.stdout.write(f'  Already exists: {card.title}')

        self.stdout.write(self.style.SUCCESS('Featured cards initialized!'))
