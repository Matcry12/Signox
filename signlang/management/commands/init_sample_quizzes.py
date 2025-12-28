from django.core.management.base import BaseCommand
from signlang.models import Lesson, Quiz, Question, Answer


class Command(BaseCommand):
    help = 'Initialize sample quizzes for existing lessons'

    def handle(self, *args, **options):
        # Sample quiz data for each lesson
        quiz_data = {
            'Hello and Goodbye': {
                'title': 'Greeting Signs Quiz',
                'description': 'Test your knowledge of greeting signs!',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'Which hand gesture represents "Hello" in sign language?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Open palm waving side to side', True),
                            ('Closed fist raised up', False),
                            ('Both hands crossed', False),
                            ('Pointing finger', False),
                        ]
                    },
                    {
                        'text': 'Waving goodbye uses the same motion as saying hello.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                    {
                        'text': 'What is the sign for "Nice to meet you"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Touch chest then extend hand outward', True),
                            ('Wave both hands', False),
                            ('Shake your own hands together', False),
                            ('Point to yourself then the other person', False),
                        ]
                    },
                    {
                        'text': 'How do you sign "Good morning" in Vietnamese Sign Language?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Sign for "good" + sign for "morning sun rising"', True),
                            ('Just wave hello', False),
                            ('Clap twice', False),
                            ('Touch your head', False),
                        ]
                    },
                ]
            },
            'How Are You?': {
                'title': 'Asking About Feelings Quiz',
                'description': 'Learn how to ask and respond to "How are you?"',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'What is the sign for "How are you?"',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Point to person, then sign question with raised eyebrows', True),
                            ('Wave hello twice', False),
                            ('Shake hands in air', False),
                            ('Cross arms and bow', False),
                        ]
                    },
                    {
                        'text': 'The sign for "I\'m fine" involves touching your chest.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                    {
                        'text': 'How do you sign "I\'m tired"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Both hands drooping down from shoulders', True),
                            ('Jumping motion', False),
                            ('Clapping hands', False),
                            ('Waving arms', False),
                        ]
                    },
                ]
            },
            'Numbers 1-10': {
                'title': 'Counting Signs Quiz',
                'description': 'Can you recognize number signs from 1 to 10?',
                'passing_score': 80,
                'questions': [
                    {
                        'text': 'Which finger do you hold up for the number 1?',
                        'type': 'multiple_choice',
                        'points': 1,
                        'answers': [
                            ('Index finger', True),
                            ('Thumb', False),
                            ('Pinky finger', False),
                            ('Middle finger', False),
                        ]
                    },
                    {
                        'text': 'The number 5 is shown with all fingers extended on one hand.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                    {
                        'text': 'How do you sign the number 10?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Show both hands with all fingers (5+5)', True),
                            ('Hold up 10 fingers one by one', False),
                            ('Make a circle with hands', False),
                            ('Clap 10 times', False),
                        ]
                    },
                    {
                        'text': 'For number 3, which fingers are typically used?',
                        'type': 'multiple_choice',
                        'points': 1,
                        'answers': [
                            ('Thumb, index, and middle finger', True),
                            ('Index, middle, and ring finger', False),
                            ('Last three fingers', False),
                            ('Any three fingers', False),
                        ]
                    },
                    {
                        'text': 'Number 0 is signed the same as the letter O.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                ]
            },
            'Immediate Family': {
                'title': 'Family Members Quiz',
                'description': 'Identify signs for family members',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'Where is the sign for "mother" typically made?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Near the chin/cheek area', True),
                            ('Above the head', False),
                            ('On the shoulder', False),
                            ('On the stomach', False),
                        ]
                    },
                    {
                        'text': 'The sign for "father" is made in the same location as "mother".',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('False', True),
                            ('True', False),
                        ]
                    },
                    {
                        'text': 'How do you sign "brother"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Male sign + sibling sign at forehead level', True),
                            ('Wave at someone', False),
                            ('Point to yourself', False),
                            ('Cross your arms', False),
                        ]
                    },
                    {
                        'text': 'What is the sign for "baby"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Cradle arms and rock back and forth', True),
                            ('Pat your head', False),
                            ('Clap hands together', False),
                            ('Make small circles', False),
                        ]
                    },
                ]
            },
            'Morning Routine': {
                'title': 'Daily Activities Quiz',
                'description': 'Test your knowledge of morning routine signs',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'What is the sign for "wake up"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Open eyes motion with fingers near eyes', True),
                            ('Stretch arms above head', False),
                            ('Clap hands', False),
                            ('Wave goodbye', False),
                        ]
                    },
                    {
                        'text': 'The sign for "brush teeth" mimics the actual action.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                    {
                        'text': 'How do you sign "eat breakfast"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Eat sign + morning sign', True),
                            ('Just point to mouth', False),
                            ('Rub stomach', False),
                            ('Clap then eat', False),
                        ]
                    },
                ]
            },
            'Classroom Basics': {
                'title': 'School Signs Quiz',
                'description': 'Learn classroom-related signs',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'What is the sign for "teacher"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Teaching motion from forehead outward + person sign', True),
                            ('Just point to someone', False),
                            ('Clap hands together', False),
                            ('Wave at the board', False),
                        ]
                    },
                    {
                        'text': 'The sign for "book" looks like opening a book.',
                        'type': 'true_false',
                        'points': 1,
                        'answers': [
                            ('True', True),
                            ('False', False),
                        ]
                    },
                    {
                        'text': 'How do you sign "study"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Wiggle fingers toward open palm (like reading)', True),
                            ('Tap head twice', False),
                            ('Draw in the air', False),
                            ('Close your eyes', False),
                        ]
                    },
                    {
                        'text': 'What is the sign for "homework"?',
                        'type': 'multiple_choice',
                        'points': 2,
                        'answers': [
                            ('Home sign + work sign', True),
                            ('Just the book sign', False),
                            ('Writing motion', False),
                            ('Pointing to a desk', False),
                        ]
                    },
                ]
            },
        }

        created_quizzes = 0
        created_questions = 0
        created_answers = 0

        for lesson_title, quiz_info in quiz_data.items():
            try:
                lesson = Lesson.objects.get(title=lesson_title)
            except Lesson.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Lesson "{lesson_title}" not found, skipping...'))
                continue

            # Check if quiz already exists
            if Quiz.objects.filter(lesson=lesson, title=quiz_info['title']).exists():
                self.stdout.write(self.style.WARNING(f'Quiz "{quiz_info["title"]}" already exists, skipping...'))
                continue

            # Create quiz
            quiz = Quiz.objects.create(
                lesson=lesson,
                title=quiz_info['title'],
                description=quiz_info['description'],
                passing_score=quiz_info['passing_score'],
                is_active=True
            )
            created_quizzes += 1
            self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.title}'))

            # Create questions and answers
            for order, q_data in enumerate(quiz_info['questions'], 1):
                question = Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['text'],
                    question_type=q_data['type'],
                    points=q_data['points'],
                    order=order
                )
                created_questions += 1

                for answer_text, is_correct in q_data['answers']:
                    Answer.objects.create(
                        question=question,
                        answer_text=answer_text,
                        is_correct=is_correct
                    )
                    created_answers += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary:\n'
            f'  - Created {created_quizzes} quizzes\n'
            f'  - Created {created_questions} questions\n'
            f'  - Created {created_answers} answers'
        ))
