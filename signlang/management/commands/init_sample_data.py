from django.core.management.base import BaseCommand
from signlang.models import Category, Lesson, Vocabulary, VideoCategory, Video


SAMPLE_CATEGORIES = [
    {
        'name': 'Greetings',
        'slug': 'greetings',
        'description': 'Learn basic greetings and introductions in sign language',
        'icon': 'fa-hand-wave',
        'order': 1,
    },
    {
        'name': 'Numbers',
        'slug': 'numbers',
        'description': 'Learn to count and express numbers in sign language',
        'icon': 'fa-hashtag',
        'order': 2,
    },
    {
        'name': 'Family',
        'slug': 'family',
        'description': 'Signs for family members and relationships',
        'icon': 'fa-users',
        'order': 3,
    },
    {
        'name': 'Daily Life',
        'slug': 'daily',
        'description': 'Common signs for everyday activities',
        'icon': 'fa-calendar-day',
        'order': 4,
    },
    {
        'name': 'School',
        'slug': 'school',
        'description': 'Signs for school and academic settings',
        'icon': 'fa-school',
        'order': 5,
    },
    {
        'name': 'Work',
        'slug': 'work',
        'description': 'Professional and workplace signs',
        'icon': 'fa-briefcase',
        'order': 6,
    },
]

SAMPLE_LESSONS = [
    # Greetings
    {
        'title': 'Hello and Goodbye',
        'slug': 'hello-goodbye',
        'category_slug': 'greetings',
        'description': 'Learn the most common greeting signs',
        'content': '''
## Introduction
In this lesson, you will learn the fundamental greeting signs used in everyday communication.

## Key Signs
1. **Hello** - Wave your hand with palm facing outward
2. **Goodbye** - Similar to hello, but with a closing motion
3. **Nice to meet you** - A warm greeting for first meetings

## Practice Tips
- Practice in front of a mirror
- Pay attention to facial expressions
- Greetings often include eye contact
        ''',
        'difficulty': 'easy',
        'order': 1,
        'vocabularies': [
            {'word': 'Hello', 'meaning': 'Xin chào', 'description': 'Basic greeting sign'},
            {'word': 'Goodbye', 'meaning': 'Tạm biệt', 'description': 'Farewell sign'},
            {'word': 'Nice to meet you', 'meaning': 'Rất vui được gặp bạn', 'description': 'Formal introduction'},
        ]
    },
    {
        'title': 'How Are You?',
        'slug': 'how-are-you',
        'category_slug': 'greetings',
        'description': 'Learn to ask and respond about well-being',
        'content': '''
## Introduction
Learn how to ask someone how they are doing and respond appropriately.

## Key Phrases
1. **How are you?** - Common conversation starter
2. **I am fine** - Positive response
3. **Thank you** - Expressing gratitude

## Cultural Note
In sign language, facial expressions are very important when expressing emotions.
        ''',
        'difficulty': 'easy',
        'order': 2,
        'vocabularies': [
            {'word': 'How are you?', 'meaning': 'Bạn khỏe không?', 'description': 'Question about well-being'},
            {'word': 'I am fine', 'meaning': 'Tôi khỏe', 'description': 'Positive response'},
            {'word': 'Thank you', 'meaning': 'Cảm ơn', 'description': 'Expression of gratitude'},
        ]
    },
    # Numbers
    {
        'title': 'Numbers 1-10',
        'slug': 'numbers-1-10',
        'category_slug': 'numbers',
        'description': 'Master counting from 1 to 10',
        'content': '''
## Introduction
Numbers are essential for everyday communication. Let's start with 1-10.

## Hand Positions
- Numbers 1-5 use one hand
- Numbers 6-10 typically combine hand positions

## Practice
Try counting objects around you using these signs!
        ''',
        'difficulty': 'easy',
        'order': 1,
        'vocabularies': [
            {'word': 'One', 'meaning': 'Một', 'description': 'Index finger up'},
            {'word': 'Two', 'meaning': 'Hai', 'description': 'Index and middle finger'},
            {'word': 'Three', 'meaning': 'Ba', 'description': 'Add ring finger'},
            {'word': 'Five', 'meaning': 'Năm', 'description': 'All fingers open'},
            {'word': 'Ten', 'meaning': 'Mười', 'description': 'Thumbs up, shake'},
        ]
    },
    # Family
    {
        'title': 'Immediate Family',
        'slug': 'immediate-family',
        'category_slug': 'family',
        'description': 'Signs for parents, siblings, and close family',
        'content': '''
## Introduction
Family signs are among the most commonly used in daily conversation.

## Key Signs
1. **Mother/Mom** - Thumb touches chin
2. **Father/Dad** - Thumb touches forehead
3. **Brother/Sister** - Variations of family signs

## Memory Tip
Male family members: signs near forehead
Female family members: signs near chin
        ''',
        'difficulty': 'easy',
        'order': 1,
        'vocabularies': [
            {'word': 'Mother', 'meaning': 'Mẹ', 'description': 'Thumb on chin, fingers spread'},
            {'word': 'Father', 'meaning': 'Bố', 'description': 'Thumb on forehead, fingers spread'},
            {'word': 'Brother', 'meaning': 'Anh/Em trai', 'description': 'Male sibling sign'},
            {'word': 'Sister', 'meaning': 'Chị/Em gái', 'description': 'Female sibling sign'},
        ]
    },
    # Daily Life
    {
        'title': 'Morning Routine',
        'slug': 'morning-routine',
        'category_slug': 'daily',
        'description': 'Signs for common morning activities',
        'content': '''
## Introduction
Start your day with these essential signs for morning routines.

## Activities
1. Wake up
2. Brush teeth
3. Eat breakfast
4. Go to school/work

## Practice Scenario
Try signing your entire morning routine!
        ''',
        'difficulty': 'medium',
        'order': 1,
        'vocabularies': [
            {'word': 'Wake up', 'meaning': 'Thức dậy', 'description': 'Opening eyes gesture'},
            {'word': 'Brush teeth', 'meaning': 'Đánh răng', 'description': 'Finger mimics toothbrush'},
            {'word': 'Eat', 'meaning': 'Ăn', 'description': 'Hand to mouth motion'},
            {'word': 'Go', 'meaning': 'Đi', 'description': 'Directional movement'},
        ]
    },
    # School
    {
        'title': 'Classroom Basics',
        'slug': 'classroom-basics',
        'category_slug': 'school',
        'description': 'Essential signs for the classroom',
        'content': '''
## Introduction
Learn signs commonly used in educational settings.

## Key Vocabulary
- Teacher
- Student
- Book
- Question
- Answer

## Useful Phrases
"I have a question"
"I understand"
"Please repeat"
        ''',
        'difficulty': 'medium',
        'order': 1,
        'vocabularies': [
            {'word': 'Teacher', 'meaning': 'Giáo viên', 'description': 'Knowledge sharing gesture'},
            {'word': 'Student', 'meaning': 'Học sinh', 'description': 'Learning gesture'},
            {'word': 'Book', 'meaning': 'Sách', 'description': 'Opening book motion'},
            {'word': 'Question', 'meaning': 'Câu hỏi', 'description': 'Questioning gesture'},
        ]
    },
]

SAMPLE_VIDEO_CATEGORIES = [
    {'name': 'At the Market', 'slug': 'market', 'description': 'Shopping scenarios', 'icon': 'fa-shopping-cart'},
    {'name': 'At the Hospital', 'slug': 'hospital', 'description': 'Medical situations', 'icon': 'fa-hospital'},
    {'name': 'Transportation', 'slug': 'transportation', 'description': 'Getting around', 'icon': 'fa-bus'},
]


class Command(BaseCommand):
    help = 'Initialize sample data for testing (categories, lessons, vocabularies)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if data exists',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        # Create categories
        self.stdout.write('Creating categories...')
        for cat_data in SAMPLE_CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created: {cat.name}')
            else:
                self.stdout.write(f'  Exists: {cat.name}')

        # Create lessons with vocabularies
        self.stdout.write('\nCreating lessons...')
        for lesson_data in SAMPLE_LESSONS:
            category = Category.objects.get(slug=lesson_data['category_slug'])
            vocabularies = lesson_data.pop('vocabularies', [])
            lesson_data.pop('category_slug')

            lesson, created = Lesson.objects.get_or_create(
                slug=lesson_data['slug'],
                defaults={**lesson_data, 'category': category}
            )

            if created:
                self.stdout.write(f'  Created: {lesson.title}')
                # Create vocabularies
                for i, vocab_data in enumerate(vocabularies):
                    Vocabulary.objects.create(
                        lesson=lesson,
                        order=i + 1,
                        **vocab_data
                    )
                    self.stdout.write(f'    + Vocab: {vocab_data["word"]}')
            else:
                self.stdout.write(f'  Exists: {lesson.title}')

        # Create video categories
        self.stdout.write('\nCreating video categories...')
        for vcat_data in SAMPLE_VIDEO_CATEGORIES:
            vcat, created = VideoCategory.objects.get_or_create(
                slug=vcat_data['slug'],
                defaults=vcat_data
            )
            if created:
                self.stdout.write(f'  Created: {vcat.name}')
            else:
                self.stdout.write(f'  Exists: {vcat.name}')

        self.stdout.write(self.style.SUCCESS('\nSample data initialized!'))
        self.stdout.write(f'  Categories: {Category.objects.count()}')
        self.stdout.write(f'  Lessons: {Lesson.objects.count()}')
        self.stdout.write(f'  Vocabularies: {Vocabulary.objects.count()}')
        self.stdout.write(f'  Video Categories: {VideoCategory.objects.count()}')
