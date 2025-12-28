from django.core.management.base import BaseCommand
from django.utils.text import slugify
from signlang.models import VideoCategory, Video


class Command(BaseCommand):
    help = 'Initialize sample videos for existing video categories'

    def handle(self, *args, **options):
        # Sample video data for each category
        # Using placeholder descriptions - videos can be uploaded later
        video_data = {
            'market': [
                {
                    'title': 'Buying Vegetables at the Market',
                    'description': 'Learn essential sign language phrases for buying vegetables. '
                                 'This video covers signs for common vegetables like carrots, '
                                 'tomatoes, lettuce, and how to ask about prices and quantities.',
                    'difficulty': 'easy',
                },
                {
                    'title': 'Asking for Prices',
                    'description': 'Master the art of price negotiation in sign language. '
                                 'Learn how to ask "How much?", understand number signs for prices, '
                                 'and common responses from vendors.',
                    'difficulty': 'easy',
                },
                {
                    'title': 'Bargaining and Negotiating',
                    'description': 'Advanced market communication skills. Learn signs for '
                                 '"too expensive", "discount", "cheaper", and polite negotiation phrases.',
                    'difficulty': 'medium',
                },
                {
                    'title': 'Fruit Shopping Vocabulary',
                    'description': 'Complete guide to fruit-related signs. Learn signs for '
                                 'apples, bananas, oranges, mangoes, and how to describe freshness.',
                    'difficulty': 'easy',
                },
            ],
            'hospital': [
                {
                    'title': 'Describing Pain and Symptoms',
                    'description': 'Essential medical signs for describing your symptoms. '
                                 'Learn signs for headache, stomachache, fever, cough, and how '
                                 'to indicate pain levels and duration.',
                    'difficulty': 'medium',
                },
                {
                    'title': 'Emergency Signs',
                    'description': 'Critical emergency vocabulary in sign language. '
                                 'Learn signs for "help", "emergency", "ambulance", "hospital", '
                                 'and how to communicate urgency.',
                    'difficulty': 'medium',
                },
                {
                    'title': 'At the Pharmacy',
                    'description': 'Navigate pharmacy visits with confidence. Learn signs for '
                                 'common medications, dosage instructions, and how to ask for '
                                 'specific medicine.',
                    'difficulty': 'medium',
                },
                {
                    'title': 'Doctor Appointment Dialogue',
                    'description': 'Complete dialogue practice for medical appointments. '
                                 'Learn how to explain medical history, current symptoms, '
                                 'and understand doctor instructions.',
                    'difficulty': 'hard',
                },
            ],
            'transportation': [
                {
                    'title': 'Taking a Bus',
                    'description': 'Essential bus travel signs. Learn how to ask about routes, '
                                 'bus stops, fares, and common phrases for public transportation.',
                    'difficulty': 'easy',
                },
                {
                    'title': 'Asking for Directions',
                    'description': 'Navigation vocabulary in sign language. Learn directional signs '
                                 'like left, right, straight, and how to ask "Where is...?"',
                    'difficulty': 'easy',
                },
                {
                    'title': 'At the Train Station',
                    'description': 'Train travel vocabulary and phrases. Learn signs for '
                                 'platform, ticket, schedule, departure, and arrival.',
                    'difficulty': 'medium',
                },
                {
                    'title': 'Taxi and Ride Services',
                    'description': 'Modern transportation signs. Learn how to communicate '
                                 'with taxi drivers, give destination addresses, and discuss fares.',
                    'difficulty': 'medium',
                },
            ],
        }

        created_count = 0
        skipped_count = 0

        for category_slug, videos in video_data.items():
            try:
                category = VideoCategory.objects.get(slug=category_slug)
            except VideoCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Category "{category_slug}" not found, skipping...'
                ))
                continue

            for video_info in videos:
                # Generate slug from title
                base_slug = slugify(video_info['title'])
                slug = base_slug
                counter = 1

                # Ensure unique slug
                while Video.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Check if video with same title already exists in category
                if Video.objects.filter(category=category, title=video_info['title']).exists():
                    self.stdout.write(self.style.WARNING(
                        f'Video "{video_info["title"]}" already exists, skipping...'
                    ))
                    skipped_count += 1
                    continue

                # Create video
                video = Video.objects.create(
                    title=video_info['title'],
                    slug=slug,
                    category=category,
                    description=video_info['description'],
                    difficulty=video_info['difficulty'],
                    is_published=True,
                    view_count=0
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created video: {video.title} ({category.name})'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary:\n'
            f'  - Created {created_count} videos\n'
            f'  - Skipped {skipped_count} existing videos'
        ))

        if created_count > 0:
            self.stdout.write(self.style.NOTICE(
                '\nNote: Videos are created with metadata only. '
                'Upload actual video files through the admin panel.'
            ))
