import json
import csv
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Avg, Max, Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.utils import timezone, translation
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import (
    UserProfile, Category, Lesson, Vocabulary, UserProgress, SavedLesson,
    Quiz, Question, Answer, QuizAttempt, VideoCategory, Video,
    ForumPost, Comment, Like, Report, UserInteraction,
    Badge, UserBadge, UserStreak, UserPoints, Notification, DailyActivity,
    FeaturedCard, SiteSettings, VocabularyReview
)
from . import gamification
from .utils import safe_int, sanitize_string, validate_slug, generate_slug
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    ForumPostForm, CommentForm, ReportForm
)


# ============ HOME & DASHBOARD ============

# Default fallback cards when database is empty
DEFAULT_COMMON_SENTENCES = [
    {'title': 'Daily Communication', 'icon': 'fa-comment-dots', 'color': 'blue', 'link': '/lessons/?category=daily'},
    {'title': 'School Communication', 'icon': 'fa-graduation-cap', 'color': 'teal', 'link': '/lessons/?category=school'},
    {'title': 'Work Communication', 'icon': 'fa-briefcase', 'color': 'indigo', 'link': '/lessons/?category=work'},
]

CACHE_TIMEOUT = 300  # 5 minutes


def get_featured_cards(section):
    """Get featured cards with caching and fallback"""
    cache_key = f'featured_cards_{section}'
    cards = cache.get(cache_key)

    if cards is None:
        cards = list(FeaturedCard.objects.filter(section=section, is_active=True).values(
            'title', 'icon', 'color', 'link', 'description'
        ))
        cache.set(cache_key, cards, CACHE_TIMEOUT)

    # Fallback for common_sentences if empty
    if not cards and section == 'common_sentences':
        cards = DEFAULT_COMMON_SENTENCES

    return cards


@require_POST
def set_language(request):
    """Custom language switcher view"""
    language = request.POST.get('language', settings.LANGUAGE_CODE)
    next_url = request.POST.get('next', '/')

    # Validate language
    valid_languages = [lang[0] for lang in settings.LANGUAGES]
    if language not in valid_languages:
        language = settings.LANGUAGE_CODE

    # Activate the language
    translation.activate(language)

    # Create response with redirect
    response = HttpResponseRedirect(next_url)

    # Set language cookie
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=settings.LANGUAGE_COOKIE_AGE if hasattr(settings, 'LANGUAGE_COOKIE_AGE') else 365 * 24 * 60 * 60,
        path=settings.LANGUAGE_COOKIE_PATH if hasattr(settings, 'LANGUAGE_COOKIE_PATH') else '/',
    )

    # Also store in session
    request.session['_language'] = language

    return response


def home(request):
    # Cache homepage for 5 minutes
    cache_key = 'home_page_data'
    context = cache.get(cache_key)
    
    if context is None:
        categories = Category.objects.all()[:6]
        latest_lessons = Lesson.objects.filter(is_published=True)[:6]

        # Get dynamic featured cards with caching
        common_sentences = get_featured_cards('common_sentences')
        featured_cards = get_featured_cards('featured')

        context = {
            'categories': categories,
            'latest_lessons': latest_lessons,
            'common_sentences': common_sentences,
            'featured_cards': featured_cards,
        }
        # Cache for 5 minutes (300 seconds)
        cache.set(cache_key, context, 300)
    
    return render(request, 'signlang/home.html', context)


def about(request):
    return render(request, 'signlang/about.html')


def dictionary(request):
    """Dictionary page with all vocabulary A-Z"""
    search = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')

    # Get all vocabulary from published lessons
    vocabulary = Vocabulary.objects.filter(
        lesson__is_published=True
    ).select_related('lesson', 'lesson__category').order_by('word')

    # Apply search filter
    if search:
        vocabulary = vocabulary.filter(
            Q(word__icontains=search) |
            Q(meaning__icontains=search)
        )

    # Apply category filter
    if category_slug:
        vocabulary = vocabulary.filter(lesson__category__slug=category_slug)

    # Group by first letter
    vocab_by_letter = {}
    for vocab in vocabulary:
        if vocab.word and len(vocab.word) > 0:
            first_letter = vocab.word[0].upper()
            if not first_letter.isalpha():
                first_letter = '#'
        else:
            first_letter = '#'
        if first_letter not in vocab_by_letter:
            vocab_by_letter[first_letter] = []
        vocab_by_letter[first_letter].append(vocab)

    # Sort letters
    sorted_letters = sorted(vocab_by_letter.keys(), key=lambda x: (x == '#', x))

    # Get categories for filter
    categories = Category.objects.annotate(
        vocab_count=Count('lessons__vocabularies', filter=Q(lessons__is_published=True))
    ).filter(vocab_count__gt=0)

    return render(request, 'signlang/dictionary.html', {
        'vocab_by_letter': vocab_by_letter,
        'sorted_letters': sorted_letters,
        'total_count': vocabulary.count(),
        'search': search,
        'categories': categories,
        'selected_category': category_slug,
    })


def global_search(request):
    """Global search across lessons, videos, vocabulary, and forum posts"""
    query = request.GET.get('q', '').strip()
    results = {
        'lessons': [],
        'videos': [],
        'vocabulary': [],
        'forum': [],
        'total_count': 0
    }

    if query and len(query) >= 2:
        # Search Lessons
        lessons = Lesson.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query),
            is_published=True
        ).select_related('category')[:10]
        results['lessons'] = lessons

        # Search Videos
        videos = Video.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            is_published=True
        ).select_related('category')[:10]
        results['videos'] = videos

        # Search Vocabulary
        vocabulary = Vocabulary.objects.filter(
            Q(word__icontains=query) |
            Q(meaning__icontains=query) |
            Q(description__icontains=query),
            lesson__is_published=True
        ).select_related('lesson')[:10]
        results['vocabulary'] = vocabulary

        # Search Forum Posts
        forum_posts = ForumPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).select_related('author')[:10]
        results['forum'] = forum_posts

        results['total_count'] = (
            len(results['lessons']) +
            len(results['videos']) +
            len(results['vocabulary']) +
            len(results['forum'])
        )

    return render(request, 'signlang/search_results.html', {
        'query': query,
        'results': results
    })


def get_activity_calendar(user, weeks=52):
    """
    Generate activity calendar data for heatmap visualization.
    Returns data for the past `weeks` weeks, formatted for a GitHub-style heatmap.
    """
    today = timezone.now().date()
    # Start from the beginning of the week (Monday), going back `weeks` weeks
    start_date = today - timedelta(days=today.weekday() + (weeks * 7))

    # Get all daily activities for the user in this period
    activities = DailyActivity.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=today
    ).values('date', 'points_earned', 'lessons_completed', 'quizzes_passed')

    # Create a dict for quick lookup
    activity_map = {a['date']: a for a in activities}

    # Generate calendar data
    calendar_data = []
    current_date = start_date

    while current_date <= today:
        activity = activity_map.get(current_date)
        if activity:
            # Calculate intensity level (0-4) based on points
            points = activity['points_earned']
            if points == 0:
                level = 0
            elif points < 20:
                level = 1
            elif points < 50:
                level = 2
            elif points < 100:
                level = 3
            else:
                level = 4
        else:
            level = 0
            points = 0

        calendar_data.append({
            'date': current_date.isoformat(),
            'level': level,
            'points': points if activity else 0,
            'lessons': activity['lessons_completed'] if activity else 0,
            'quizzes': activity['quizzes_passed'] if activity else 0,
        })
        current_date += timedelta(days=1)

    # Calculate stats
    total_active_days = sum(1 for d in calendar_data if d['level'] > 0)
    total_points = sum(d['points'] for d in calendar_data)

    return {
        'data': calendar_data,
        'total_active_days': total_active_days,
        'total_points': total_points,
        'weeks': weeks,
    }


@login_required
def activity_calendar_api(request):
    """API endpoint for activity calendar data"""
    user = request.user
    weeks = safe_int(request.GET.get('weeks', 52), default=52)
    weeks = min(weeks, 52)  # Max 1 year

    calendar = get_activity_calendar(user, weeks)
    return JsonResponse(calendar)


@login_required
def dashboard(request):
    from django.db.models import Count, Q
    
    user = request.user

    # Ensure gamification records exist
    gamification.ensure_user_gamification(user)

    # Get user progress with optimization
    progress_list = UserProgress.objects.filter(user=user).select_related('lesson__category')
    
    # Use aggregate instead of multiple count() calls
    progress_stats = progress_list.aggregate(
        completed=Count('id', filter=Q(status='completed')),
        in_progress=Count('id', filter=Q(status='in_progress'))
    )
    completed_count = progress_stats['completed']
    in_progress_count = progress_stats['in_progress']
    
    total_lessons = Lesson.objects.filter(is_published=True).count()

    # Calculate progress percentage
    progress_percentage = (completed_count / total_lessons * 100) if total_lessons > 0 else 0

    # Get recommended lessons
    recommended_lessons = get_recommendations(user)

    # Get recent activity (already has select_related now)
    recent_progress = progress_list.order_by('-last_accessed')[:5]

    # Get saved lessons (optimized)
    saved_lessons = SavedLesson.objects.filter(user=user).select_related('lesson__category')[:5]

    # Get gamification data (these are OneToOne, so no optimization needed)
    user_points = user.points
    user_streak = user.streak
    recent_badges = UserBadge.objects.filter(user=user).select_related('badge')[:3]
    
    # Use aggregate for notification count
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()

    # Get activity calendar data (last 20 weeks for compact display)
    activity_calendar = get_activity_calendar(user, weeks=20)
    activity_calendar_json = json.dumps(activity_calendar['data'])

    context = {
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'total_lessons': total_lessons,
        'progress_percentage': round(progress_percentage, 1),
        'recommended_lessons': recommended_lessons,
        'recent_progress': recent_progress,
        'saved_lessons': saved_lessons,
        # Gamification data
        'user_points': user_points,
        'user_streak': user_streak,
        'recent_badges': recent_badges,
        'unread_notifications': unread_notifications,
        # Activity calendar
        'activity_calendar': activity_calendar,
        'activity_calendar_json': activity_calendar_json,
    }
    return render(request, 'signlang/dashboard.html', context)


def get_recommendations(user, limit=5):
    """
    Rule-based recommendation algorithm:
    1. Lessons from categories user hasn't completed
    2. Lessons matching user's skill level
    3. Avoid already completed lessons
    4. Prioritize categories user has shown interest in
    """
    completed_lesson_ids = UserProgress.objects.filter(
        user=user, status='completed'
    ).values_list('lesson_id', flat=True)

    # Get user's skill level
    try:
        skill_level = user.profile.skill_level
    except UserProfile.DoesNotExist:
        skill_level = 'beginner'

    # Map skill level to difficulty
    difficulty_map = {
        'beginner': ['easy'],
        'intermediate': ['easy', 'medium'],
        'advanced': ['easy', 'medium', 'hard'],
    }
    allowed_difficulties = difficulty_map.get(skill_level, ['easy'])

    # Get categories user has interacted with
    interacted_categories = UserInteraction.objects.filter(
        user=user
    ).values_list('lesson__category_id', flat=True).distinct()

    # Get lessons not completed, matching difficulty
    recommended = Lesson.objects.filter(
        is_published=True,
        difficulty__in=allowed_difficulties
    ).exclude(
        id__in=completed_lesson_ids
    )

    # Prioritize interacted categories
    if interacted_categories:
        recommended = recommended.annotate(
            priority=Count('id', filter=Q(category_id__in=interacted_categories))
        ).order_by('-priority', 'order')
    else:
        recommended = recommended.order_by('order')

    return recommended[:limit]


# ============ AUTHENTICATION ============

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile is auto-created by signal, but ensure it exists
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'signlang/auth/register.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)

    # Get user stats
    progress = UserProgress.objects.filter(user=request.user)
    stats = {
        'completed_lessons': progress.filter(status='completed').count(),
        'quiz_attempts': QuizAttempt.objects.filter(user=request.user).count(),
        'forum_posts': ForumPost.objects.filter(author=request.user).count(),
    }

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'stats': stats,
    }
    return render(request, 'signlang/auth/profile.html', context)


# ============ LESSONS ============

def category_list(request):
    categories = Category.objects.annotate(lesson_count=Count('lessons'))
    return render(request, 'signlang/lessons/category_list.html', {'categories': categories})


def lesson_list(request, category_slug=None):
    lessons = Lesson.objects.filter(is_published=True)
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        lessons = lessons.filter(category=category)

    # Filtering
    difficulty = request.GET.get('difficulty')
    if difficulty:
        lessons = lessons.filter(difficulty=difficulty)

    # Search
    search = request.GET.get('search')
    if search:
        lessons = lessons.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(lessons, 12)
    page = request.GET.get('page')
    lessons = paginator.get_page(page)

    context = {
        'lessons': lessons,
        'category': category,
        'categories': Category.objects.all(),
    }
    return render(request, 'signlang/lessons/lesson_list.html', context)


def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_published=True)
    vocabularies = lesson.vocabularies.all()

    # Track progress for logged in users
    user_progress = None
    is_saved = False
    learning_stats = None

    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )
        if created or user_progress.status == 'not_started':
            user_progress.status = 'in_progress'
            user_progress.save()

        # Track interaction
        UserInteraction.objects.create(
            user=request.user,
            lesson=lesson,
            interaction_type='view',
            weight=1.0
        )

        is_saved = SavedLesson.objects.filter(user=request.user, lesson=lesson).exists()

        # Calculate learning progress for auto-completion
        learning_stats = calculate_lesson_learning_progress(request.user, lesson)

        # Auto-complete lesson if criteria met
        if learning_stats['can_complete'] and user_progress.status != 'completed':
            user_progress.status = 'completed'
            user_progress.completed_at = timezone.now()
            user_progress.save()

            # Award points for completion
            gamification.on_lesson_complete(request.user, lesson)

    # Get related lessons
    related_lessons = Lesson.objects.filter(
        category=lesson.category,
        is_published=True
    ).exclude(id=lesson.id)[:4]

    context = {
        'lesson': lesson,
        'vocabularies': vocabularies,
        'user_progress': user_progress,
        'is_saved': is_saved,
        'related_lessons': related_lessons,
        'learning_stats': learning_stats,
    }
    return render(request, 'signlang/lessons/lesson_detail.html', context)


def calculate_lesson_learning_progress(user, lesson):
    """
    Calculate learning progress for a lesson based on actual activity.
    Returns stats about vocabulary mastery and quiz performance.
    """
    vocabularies = lesson.vocabularies.all()
    quiz = Quiz.objects.filter(lesson=lesson, is_active=True).first()

    stats = {
        'has_vocabulary': vocabularies.exists(),
        'has_quiz': quiz is not None,
        'vocab_mastery': 0,
        'vocab_reviewed': 0,
        'vocab_total': vocabularies.count(),
        'quiz_passed': False,
        'quiz_best_score': None,
        'overall_progress': 0,
        'can_complete': False,
    }

    if not stats['has_vocabulary'] and not stats['has_quiz']:
        # No content to track - require manual completion
        stats['can_complete'] = False
        stats['overall_progress'] = 0
        stats['requires_manual_complete'] = True
        return stats

    progress_parts = []

    # Calculate vocabulary mastery
    if stats['has_vocabulary']:
        reviews = VocabularyReview.objects.filter(
            user=user,
            vocabulary__lesson=lesson
        )
        stats['vocab_reviewed'] = reviews.filter(total_reviews__gt=0).count()

        if reviews.exists():
            total_mastery = sum(r.mastery_level for r in reviews)
            stats['vocab_mastery'] = total_mastery // reviews.count() if reviews.count() > 0 else 0

        # Vocabulary progress: need 70% average mastery
        vocab_progress = min(100, int(stats['vocab_mastery'] / 70 * 100))
        progress_parts.append(vocab_progress)

    # Calculate quiz progress
    if stats['has_quiz']:
        best_attempt = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz
        ).order_by('-score').first()

        if best_attempt:
            stats['quiz_best_score'] = best_attempt.score
            stats['quiz_passed'] = best_attempt.passed
            quiz_progress = 100 if best_attempt.passed else int(best_attempt.score / best_attempt.max_score * 100) if best_attempt.max_score > 0 else 0
        else:
            quiz_progress = 0

        progress_parts.append(quiz_progress)

    # Calculate overall progress
    if progress_parts:
        stats['overall_progress'] = sum(progress_parts) // len(progress_parts)

    # Determine if lesson can be marked complete
    # Criteria: 70%+ vocab mastery (if has vocab) AND passed quiz (if has quiz)
    vocab_ok = not stats['has_vocabulary'] or stats['vocab_mastery'] >= 70
    quiz_ok = not stats['has_quiz'] or stats['quiz_passed']
    stats['can_complete'] = vocab_ok and quiz_ok

    return stats


@login_required
def save_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    saved, created = SavedLesson.objects.get_or_create(user=request.user, lesson=lesson)

    if not created:
        saved.delete()
        messages.info(request, 'Lesson removed from saved.')
    else:
        UserInteraction.objects.create(
            user=request.user,
            lesson=lesson,
            interaction_type='save',
            weight=1.5
        )
        messages.success(request, 'Lesson saved!')

    return redirect('lesson_detail', slug=lesson.slug)


@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.status = 'completed'
    progress.completed_at = timezone.now()
    progress.save()

    UserInteraction.objects.create(
        user=request.user,
        lesson=lesson,
        interaction_type='complete',
        weight=2.0
    )

    # Gamification: Award points and check badges
    gamification.on_lesson_complete(request.user, lesson)

    messages.success(request, 'Lesson marked as completed! +20 XP')
    return redirect('lesson_detail', slug=lesson.slug)


@login_required
def flashcard_mode(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, is_published=True)
    vocabularies = lesson.vocabularies.all()

    # Get or create review records for each vocabulary
    vocab_data = []
    for vocab in vocabularies:
        review = VocabularyReview.get_or_create_for_vocabulary(request.user, vocab)
        vocab_data.append({
            'id': vocab.id,
            'word': vocab.word,
            'meaning': vocab.meaning,
            'description': vocab.description,
            'image': vocab.image.url if vocab.image else None,
            'video': vocab.video.url if vocab.video else None,
            'review': {
                'mastery': review.mastery_level,
                'interval': review.interval,
                'repetitions': review.repetitions,
                'is_due': review.is_due,
                'next_review': review.next_review.isoformat() if review.next_review else None,
            }
        })

    # Calculate lesson mastery
    total_mastery = sum(v['review']['mastery'] for v in vocab_data)
    avg_mastery = total_mastery // len(vocab_data) if vocab_data else 0

    # Serialize vocab_data to JSON for JavaScript
    vocab_json = json.dumps(vocab_data)

    context = {
        'lesson': lesson,
        'vocabularies': vocab_data,
        'vocabularies_json': vocab_json,
        'avg_mastery': avg_mastery,
        'total_cards': len(vocab_data),
        'due_cards': sum(1 for v in vocab_data if v['review']['is_due']),
    }
    return render(request, 'signlang/lessons/flashcard.html', context)


@login_required
@require_POST
def flashcard_rate(request):
    """API endpoint to rate a flashcard (Anki-style)"""
    try:
        data = json.loads(request.body)
        vocab_id = data.get('vocabulary_id')
        rating = data.get('rating')  # 1=Again, 2=Hard, 3=Good, 4=Easy

        if not vocab_id or not rating:
            return JsonResponse({'error': 'Missing vocabulary_id or rating'}, status=400)

        rating = int(rating)
        if rating not in [1, 2, 3, 4]:
            return JsonResponse({'error': 'Rating must be 1-4'}, status=400)

        vocabulary = get_object_or_404(Vocabulary, id=vocab_id)
        review = VocabularyReview.get_or_create_for_vocabulary(request.user, vocabulary)

        # Process the rating
        next_interval = review.process_rating(rating)

        # Update daily activity
        gamification.update_daily_activity(request.user, 'flashcard')

        # Award points for reviewing (small amount)
        if rating >= 3:  # Good or Easy
            gamification.award_points(request.user, 2, 'lesson')

        return JsonResponse({
            'success': True,
            'next_interval': next_interval,
            'mastery': review.mastery_level,
            'next_review': review.next_review.isoformat() if review.next_review else None,
            'message': f'Next review in {next_interval} day{"s" if next_interval != 1 else ""}'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============ QUIZ ============

@login_required
def quiz_list(request):
    from django.db.models import Exists, OuterRef
    
    quizzes = Quiz.objects.filter(is_active=True).select_related('lesson')

    # Get user's attempts with best (highest) score
    user_attempts = QuizAttempt.objects.filter(user=request.user).values(
        'quiz_id'
    ).annotate(
        best_score=Max('score'),
        max_score=Max('max_score'),
        attempts=Count('id'),
        has_passed=Exists(
            QuizAttempt.objects.filter(
                user=request.user,
                quiz_id=OuterRef('quiz_id'),
                passed=True
            )
        )
    )
    attempts_dict = {a['quiz_id']: a for a in user_attempts}

    context = {
        'quizzes': quizzes,
        'attempts_dict': attempts_dict,
    }
    return render(request, 'signlang/quiz/quiz_list.html', context)


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.prefetch_related('answers').all()

    # Get user's attempt history for this quiz
    user_attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz
    ).order_by('-started_at')
    # Get best attempt (highest score)
    best_attempt = user_attempts.order_by('-score').first()

    if request.method == 'POST':
        score = 0
        max_score = 0
        results = []

        for question in questions:
            max_score += question.points
            selected_answer_id = request.POST.get(f'question_{question.id}')

            if selected_answer_id:
                try:
                    selected_answer = Answer.objects.get(id=selected_answer_id)
                    is_correct = selected_answer.is_correct
                    if is_correct:
                        score += question.points
                except Answer.DoesNotExist:
                    is_correct = False
                    selected_answer = None
            else:
                is_correct = False
                selected_answer = None

            correct_answer = question.answers.filter(is_correct=True).first()
            results.append({
                'question': question,
                'selected': selected_answer,
                'correct': correct_answer,
                'is_correct': is_correct,
            })

        # Calculate percentage and pass status
        percentage = (score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= quiz.passing_score

        # Save attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            max_score=max_score,
            passed=passed,
            completed_at=timezone.now()
        )

        # Track interaction (only if quiz has a lesson)
        if quiz.lesson:
            UserInteraction.objects.create(
                user=request.user,
                lesson=quiz.lesson,
                interaction_type='quiz_pass' if passed else 'quiz_fail',
                weight=2.5 if passed else 0.5
            )

        # Gamification: Award points and check badges
        gamification.on_quiz_complete(request.user, attempt)

        # Refresh attempt history after new attempt
        user_attempts = QuizAttempt.objects.filter(
            user=request.user,
            quiz=quiz
        ).order_by('-started_at')
        best_attempt = user_attempts.order_by('-score').first()

        # Check if this is a new personal best
        is_new_best = (attempt.id == best_attempt.id) if best_attempt else True

        context = {
            'quiz': quiz,
            'results': results,
            'score': score,
            'max_score': max_score,
            'percentage': round(percentage, 1),
            'passed': passed,
            'attempt': attempt,
            'is_new_best': is_new_best,
            'best_attempt': best_attempt,
            'user_attempts': user_attempts[:10],  # Last 10 attempts
            'total_attempts': user_attempts.count(),
        }
        return render(request, 'signlang/quiz/quiz_result.html', context)

    context = {
        'quiz': quiz,
        'questions': questions,
        'user_attempts': user_attempts[:5],  # Show recent attempts on quiz page
        'best_attempt': best_attempt,
        'total_attempts': user_attempts.count(),
    }
    return render(request, 'signlang/quiz/quiz_detail.html', context)


# ============ VIDEO LIBRARY ============

def video_list(request):
    videos = Video.objects.filter(is_published=True)
    categories = VideoCategory.objects.annotate(video_count=Count('videos'))

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        videos = videos.filter(difficulty=difficulty)

    # Search
    search = request.GET.get('search')
    if search:
        videos = videos.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(videos, 12)
    page = request.GET.get('page')
    videos = paginator.get_page(page)

    context = {
        'videos': videos,
        'categories': categories,
    }
    return render(request, 'signlang/videos/video_list.html', context)


def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug, is_published=True)

    # Increment view count
    video.view_count += 1
    video.save(update_fields=['view_count'])

    # Related videos
    related_videos = Video.objects.filter(
        category=video.category,
        is_published=True
    ).exclude(id=video.id)[:4]

    context = {
        'video': video,
        'related_videos': related_videos,
    }
    return render(request, 'signlang/videos/video_detail.html', context)


# ============ FORUM ============

def forum_list(request):
    posts = ForumPost.objects.select_related('author').annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    ).order_by('-created_at')

    # Search
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
    }
    return render(request, 'signlang/forum/forum_list.html', context)


def forum_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.select_related('author').all()

    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, post=post).exists()

    comment_form = CommentForm()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('forum_detail', post_id=post.id)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    }
    return render(request, 'signlang/forum/forum_detail.html', context)


@login_required
def forum_create(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Gamification: Award points for posting
            gamification.on_forum_post(request.user)

            messages.success(request, 'Post created successfully! +15 XP')
            return redirect('forum_detail', post_id=post.id)
    else:
        form = ForumPostForm()

    return render(request, 'signlang/forum/forum_create.html', {'form': form})


@login_required
def forum_edit(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)

    if request.method == 'POST':
        form = ForumPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('forum_detail', post_id=post.id)
    else:
        form = ForumPostForm(instance=post)

    return render(request, 'signlang/forum/forum_edit.html', {'form': form, 'post': post})


@login_required
def forum_delete(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('forum_list')

    return render(request, 'signlang/forum/forum_delete.html', {'post': post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'count': post.likes.count()
        })

    return redirect('forum_detail', post_id=post.id)


@login_required
def report_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.post = post
            report.save()
            messages.success(request, 'Report submitted. Thank you!')
            return redirect('forum_detail', post_id=post.id)
    else:
        form = ReportForm()

    return render(request, 'signlang/forum/report.html', {'form': form, 'post': post})


# ============ API ENDPOINTS ============

@login_required
def api_update_progress(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )

        time_spent = safe_int(request.POST.get('time_spent'), default=0)
        if time_spent > 0:
            progress.time_spent += time_spent
            progress.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def saved_lessons(request):
    saved = SavedLesson.objects.filter(user=request.user).select_related('lesson')
    return render(request, 'signlang/lessons/saved_lessons.html', {'saved_lessons': saved})


# ============ GAMIFICATION VIEWS ============

@login_required
def achievements(request):
    """Display user achievements and badges"""
    user = request.user
    gamification.ensure_user_gamification(user)

    # Get all badges grouped by type
    all_badges = Badge.objects.filter(is_active=True)
    earned_badges = UserBadge.objects.filter(user=user).select_related('badge')
    earned_badge_ids = earned_badges.values_list('badge_id', flat=True)

    # Group badges by type
    badge_groups = {}
    for badge in all_badges:
        if badge.badge_type not in badge_groups:
            badge_groups[badge.badge_type] = []
        badge_groups[badge.badge_type].append({
            'badge': badge,
            'earned': badge.id in earned_badge_ids,
            'earned_at': earned_badges.filter(badge=badge).first().earned_at if badge.id in earned_badge_ids else None
        })

    # Get user stats
    stats = gamification.get_user_stats(user)

    # Mark badges as seen
    gamification.mark_badges_seen(user)

    context = {
        'badge_groups': badge_groups,
        'stats': stats,
        'earned_count': len(earned_badge_ids),
        'total_count': all_badges.count(),
    }
    return render(request, 'signlang/gamification/achievements.html', context)


def leaderboard(request):
    """Display leaderboard rankings"""
    period = request.GET.get('period', 'all')

    # Get leaderboard data
    leaders = gamification.get_leaderboard(period=period, limit=50)

    # Get current user's rank if logged in
    user_rank = None
    user_points = None
    if request.user.is_authenticated:
        gamification.ensure_user_gamification(request.user)
        user_rank = gamification.get_user_rank(request.user, period)
        user_points = request.user.points

    context = {
        'leaders': leaders,
        'period': period,
        'user_rank': user_rank,
        'user_points': user_points,
    }
    return render(request, 'signlang/gamification/leaderboard.html', context)


@login_required
def notifications_view(request):
    """Display user notifications"""
    notifications = Notification.objects.filter(user=request.user)[:50]

    if request.method == 'POST':
        # Mark all as read
        gamification.mark_notifications_read(request.user)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')

    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'signlang/gamification/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')


@login_required
def api_notifications(request):
    """API endpoint for notifications (for navbar dropdown)"""
    notifications = gamification.get_unread_notifications(request.user, limit=5)
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'icon': n.icon,
        'color': n.color,
        'link': n.link,
        'created_at': n.created_at.isoformat(),
    } for n in notifications]

    return JsonResponse({
        'notifications': data,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })


@login_required
@require_POST
def use_streak_freeze(request):
    """Use a streak freeze to protect the streak"""
    user = request.user
    gamification.ensure_user_gamification(user)

    streak = user.streak
    if streak.use_freeze():
        messages.success(request, f'Streak freeze activated! Your {streak.current_streak}-day streak is protected for today. You have {streak.freeze_count} freeze(s) remaining.')
    else:
        messages.error(request, 'Unable to use streak freeze. You may have no freezes remaining or your streak is already protected.')

    return redirect('my_stats')


@login_required
def my_stats(request):
    """Detailed user statistics page"""
    user = request.user
    gamification.ensure_user_gamification(user)

    stats = gamification.get_user_stats(user)

    # Get activity history (last 30 days)
    from datetime import timedelta
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    daily_activities = DailyActivity.objects.filter(
        user=user,
        date__gte=thirty_days_ago
    ).order_by('date')

    # Get quiz performance
    quiz_attempts = QuizAttempt.objects.filter(user=user).order_by('-started_at')[:10]

    context = {
        'stats': stats,
        'daily_activities': daily_activities,
        'quiz_attempts': quiz_attempts,
        'today': timezone.now().date(),
    }
    return render(request, 'signlang/gamification/my_stats.html', context)


# ============ CUSTOM ADMIN PANEL ============

from .decorators import teacher_or_staff_required
from django.db.models import Sum


@teacher_or_staff_required
def admin_dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'total_lessons': Lesson.objects.count(),
        'total_videos': Video.objects.count(),
        'total_posts': ForumPost.objects.count(),
        'total_categories': Category.objects.count(),
        'total_quizzes': Quiz.objects.count(),
        'pending_reports': Report.objects.filter(status='pending').count(),
    }
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_posts = ForumPost.objects.order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
    }
    return render(request, 'signlang/admin/dashboard.html', context)


# Category Management
@teacher_or_staff_required
def admin_category_list(request):
    categories = Category.objects.annotate(lesson_count=Count('lessons'))
    return render(request, 'signlang/admin/category_list.html', {'categories': categories})


@teacher_or_staff_required
def admin_category_create(request):
    if request.method == 'POST':
        name = sanitize_string(request.POST.get('name'), max_length=100)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)
        description = sanitize_string(request.POST.get('description', ''))
        icon = sanitize_string(request.POST.get('icon', ''), max_length=50)
        order = safe_int(request.POST.get('order'), default=0)

        # Validation
        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'signlang/admin/category_form.html', {'action': 'Create'})

        # Always generate valid ASCII slug (from user input or name)
        slug = generate_slug(slug_input) if slug_input else generate_slug(name)

        if Category.objects.filter(slug=slug).exists():
            messages.error(request, 'A category with this slug already exists.')
            return render(request, 'signlang/admin/category_form.html', {'action': 'Create'})

        Category.objects.create(
            name=name, slug=slug, description=description,
            icon=icon, order=order
        )
        messages.success(request, 'Category created successfully!')
        return redirect('admin_category_list')

    return render(request, 'signlang/admin/category_form.html', {'action': 'Create'})


@teacher_or_staff_required
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = sanitize_string(request.POST.get('name'), max_length=100)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)

        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'signlang/admin/category_form.html', {
                'category': category, 'action': 'Edit'
            })

        # Always generate valid ASCII slug (from user input or name)
        slug = generate_slug(slug_input) if slug_input else generate_slug(name)

        # Check slug uniqueness (excluding current category)
        if Category.objects.filter(slug=slug).exclude(id=category_id).exists():
            messages.error(request, 'A category with this slug already exists.')
            return render(request, 'signlang/admin/category_form.html', {
                'category': category, 'action': 'Edit'
            })

        category.name = name
        category.slug = slug
        category.description = sanitize_string(request.POST.get('description', ''))
        category.icon = sanitize_string(request.POST.get('icon', ''), max_length=50)
        category.order = safe_int(request.POST.get('order'), default=0)
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_category_list')

    return render(request, 'signlang/admin/category_form.html', {
        'category': category, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted!')
        return redirect('admin_category_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Category',
        'item_name': category.name,
        'cancel_url': '/manage/categories/'
    })


# Lesson Management
@teacher_or_staff_required
def admin_lesson_list(request):
    lessons = Lesson.objects.select_related('category').order_by('-created_at')

    # Search
    search = request.GET.get('search')
    if search:
        lessons = lessons.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(lessons, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'signlang/admin/lesson_list.html', {
        'lessons': page_obj,
        'page_obj': page_obj
    })


@teacher_or_staff_required
def admin_lesson_create(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)
        category_id = safe_int(request.POST.get('category'))
        description = sanitize_string(request.POST.get('description'))
        content = request.POST.get('content', '')
        video_url = sanitize_string(request.POST.get('video_url', ''), max_length=200)
        difficulty = request.POST.get('difficulty', 'easy')
        order = safe_int(request.POST.get('order'), default=0)
        is_published = request.POST.get('is_published') == 'on'

        # Validation
        if not title:
            messages.error(request, 'Lesson title is required.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'categories': categories, 'action': 'Create'
            })

        if not category_id:
            messages.error(request, 'Please select a category.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'categories': categories, 'action': 'Create'
            })

        # Always generate valid ASCII slug (from user input or title)
        slug = generate_slug(slug_input) if slug_input else generate_slug(title)

        if Lesson.objects.filter(slug=slug).exists():
            messages.error(request, 'A lesson with this slug already exists.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'categories': categories, 'action': 'Create'
            })

        lesson = Lesson.objects.create(
            title=title,
            slug=slug,
            category_id=category_id,
            description=description,
            content=content,
            video_url=video_url,
            difficulty=difficulty if difficulty in ['easy', 'medium', 'hard'] else 'easy',
            order=order,
            is_published=is_published,
        )
        if request.FILES.get('thumbnail'):
            lesson.thumbnail = request.FILES['thumbnail']
            lesson.save()
        messages.success(request, 'Lesson created successfully!')
        return redirect('admin_lesson_list')

    return render(request, 'signlang/admin/lesson_form.html', {
        'categories': categories, 'action': 'Create'
    })


@teacher_or_staff_required
def admin_lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)
        category_id = safe_int(request.POST.get('category'))
        difficulty = request.POST.get('difficulty', 'easy')

        # Validation
        if not title:
            messages.error(request, 'Lesson title is required.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'lesson': lesson, 'categories': categories, 'action': 'Edit'
            })

        if not category_id:
            messages.error(request, 'Please select a category.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'lesson': lesson, 'categories': categories, 'action': 'Edit'
            })

        # Always generate valid ASCII slug (from user input or title)
        slug = generate_slug(slug_input) if slug_input else generate_slug(title)

        # Check slug uniqueness (excluding current lesson)
        if Lesson.objects.filter(slug=slug).exclude(id=lesson_id).exists():
            messages.error(request, 'A lesson with this slug already exists.')
            return render(request, 'signlang/admin/lesson_form.html', {
                'lesson': lesson, 'categories': categories, 'action': 'Edit'
            })

        lesson.title = title
        lesson.slug = slug
        lesson.category_id = category_id
        lesson.description = sanitize_string(request.POST.get('description'))
        lesson.content = request.POST.get('content', '')
        lesson.video_url = sanitize_string(request.POST.get('video_url', ''), max_length=200)
        lesson.difficulty = difficulty if difficulty in ['easy', 'medium', 'hard'] else 'easy'
        lesson.order = safe_int(request.POST.get('order'), default=0)
        lesson.is_published = request.POST.get('is_published') == 'on'
        if request.FILES.get('thumbnail'):
            lesson.thumbnail = request.FILES['thumbnail']
        lesson.save()
        messages.success(request, 'Lesson updated successfully!')
        return redirect('admin_lesson_list')

    return render(request, 'signlang/admin/lesson_form.html', {
        'lesson': lesson, 'categories': categories, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted!')
        return redirect('admin_lesson_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Lesson',
        'item_name': lesson.title,
        'cancel_url': '/manage/lessons/'
    })


# Video Category Management
@teacher_or_staff_required
def admin_video_category_list(request):
    categories = VideoCategory.objects.annotate(video_count=Count('videos'))
    return render(request, 'signlang/admin/video_category_list.html', {'categories': categories})


@teacher_or_staff_required
def admin_video_category_create(request):
    if request.method == 'POST':
        name = sanitize_string(request.POST.get('name'), max_length=100)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)

        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'signlang/admin/video_category_form.html', {'action': 'Create'})

        # Always generate valid ASCII slug (from user input or name)
        slug = generate_slug(slug_input) if slug_input else generate_slug(name)

        if VideoCategory.objects.filter(slug=slug).exists():
            messages.error(request, 'A video category with this slug already exists.')
            return render(request, 'signlang/admin/video_category_form.html', {'action': 'Create'})

        VideoCategory.objects.create(
            name=name,
            slug=slug,
            description=sanitize_string(request.POST.get('description', '')),
            icon=sanitize_string(request.POST.get('icon', ''), max_length=50),
        )
        messages.success(request, 'Video category created!')
        return redirect('admin_video_category_list')
    return render(request, 'signlang/admin/video_category_form.html', {'action': 'Create'})


@teacher_or_staff_required
def admin_video_category_edit(request, category_id):
    category = get_object_or_404(VideoCategory, id=category_id)
    if request.method == 'POST':
        name = sanitize_string(request.POST.get('name'), max_length=100)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)

        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'signlang/admin/video_category_form.html', {
                'category': category, 'action': 'Edit'
            })

        # Always generate valid ASCII slug (from user input or name)
        slug = generate_slug(slug_input) if slug_input else generate_slug(name)

        if VideoCategory.objects.filter(slug=slug).exclude(id=category_id).exists():
            messages.error(request, 'A video category with this slug already exists.')
            return render(request, 'signlang/admin/video_category_form.html', {
                'category': category, 'action': 'Edit'
            })

        category.name = name
        category.slug = slug
        category.description = sanitize_string(request.POST.get('description', ''))
        category.icon = sanitize_string(request.POST.get('icon', ''), max_length=50)
        category.save()
        messages.success(request, 'Video category updated!')
        return redirect('admin_video_category_list')
    return render(request, 'signlang/admin/video_category_form.html', {
        'category': category, 'action': 'Edit'
    })


# Video Management
@teacher_or_staff_required
def admin_video_list(request):
    videos = Video.objects.select_related('category').order_by('-created_at')

    # Search
    search = request.GET.get('search')
    if search:
        videos = videos.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(videos, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'signlang/admin/video_list.html', {
        'videos': page_obj,
        'page_obj': page_obj
    })


@teacher_or_staff_required
def admin_video_create(request):
    categories = VideoCategory.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)
        category_id = safe_int(request.POST.get('category'))
        difficulty = request.POST.get('difficulty', 'easy')

        # Validation
        errors = []
        if not title:
            errors.append('Video title is required.')
        if not category_id:
            errors.append('Please select a category.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/video_form.html', {
                'categories': categories, 'action': 'Create'
            })

        # Always generate valid ASCII slug (from user input or title)
        slug = generate_slug(slug_input) if slug_input else generate_slug(title)

        if Video.objects.filter(slug=slug).exists():
            messages.error(request, 'A video with this slug already exists.')
            return render(request, 'signlang/admin/video_form.html', {
                'categories': categories, 'action': 'Create'
            })

        video = Video.objects.create(
            title=title,
            slug=slug,
            category_id=category_id,
            description=sanitize_string(request.POST.get('description', '')),
            video_url=sanitize_string(request.POST.get('video_url', ''), max_length=500),
            difficulty=difficulty if difficulty in ['easy', 'medium', 'hard'] else 'easy',
            is_published=request.POST.get('is_published') == 'on',
        )
        if request.FILES.get('video_file'):
            video.video_file = request.FILES['video_file']
        if request.FILES.get('thumbnail'):
            video.thumbnail = request.FILES['thumbnail']
        video.save()
        messages.success(request, 'Video created successfully!')
        return redirect('admin_video_list')

    return render(request, 'signlang/admin/video_form.html', {
        'categories': categories, 'action': 'Create'
    })


@teacher_or_staff_required
def admin_video_edit(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    categories = VideoCategory.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        slug_input = sanitize_string(request.POST.get('slug'), max_length=50)
        category_id = safe_int(request.POST.get('category'))
        difficulty = request.POST.get('difficulty', 'easy')

        # Validation
        errors = []
        if not title:
            errors.append('Video title is required.')
        if not category_id:
            errors.append('Please select a category.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/video_form.html', {
                'video': video, 'categories': categories, 'action': 'Edit'
            })

        # Always generate valid ASCII slug (from user input or title)
        slug = generate_slug(slug_input) if slug_input else generate_slug(title)

        # Check slug uniqueness (excluding current video)
        if Video.objects.filter(slug=slug).exclude(id=video_id).exists():
            messages.error(request, 'A video with this slug already exists.')
            return render(request, 'signlang/admin/video_form.html', {
                'video': video, 'categories': categories, 'action': 'Edit'
            })

        video.title = title
        video.slug = slug
        video.category_id = category_id
        video.description = sanitize_string(request.POST.get('description', ''))
        video.video_url = sanitize_string(request.POST.get('video_url', ''), max_length=500)
        video.difficulty = difficulty if difficulty in ['easy', 'medium', 'hard'] else 'easy'
        video.is_published = request.POST.get('is_published') == 'on'
        if request.FILES.get('video_file'):
            video.video_file = request.FILES['video_file']
        if request.FILES.get('thumbnail'):
            video.thumbnail = request.FILES['thumbnail']
        video.save()
        messages.success(request, 'Video updated successfully!')
        return redirect('admin_video_list')

    return render(request, 'signlang/admin/video_form.html', {
        'video': video, 'categories': categories, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_video_delete(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted!')
        return redirect('admin_video_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Video',
        'item_name': video.title,
        'cancel_url': '/manage/videos/'
    })


# Quiz Management
@teacher_or_staff_required
def admin_quiz_list(request):
    quizzes = Quiz.objects.select_related('lesson').annotate(
        question_count=Count('questions')
    ).order_by('-id')

    # Search
    search = request.GET.get('search')
    if search:
        quizzes = quizzes.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Pagination
    paginator = Paginator(quizzes, 15)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'signlang/admin/quiz_list.html', {
        'quizzes': page_obj,
        'page_obj': page_obj
    })


@teacher_or_staff_required
def admin_quiz_create(request):
    lessons = Lesson.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        lesson_id = safe_int(request.POST.get('lesson'))

        # Validation
        errors = []
        if not title:
            errors.append('Quiz title is required.')
        if not lesson_id:
            errors.append('Please select a lesson.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/quiz_form.html', {
                'lessons': lessons, 'action': 'Create'
            })

        quiz = Quiz.objects.create(
            title=title,
            lesson_id=lesson_id,
            description=sanitize_string(request.POST.get('description', '')),
            passing_score=safe_int(request.POST.get('passing_score'), default=70),
            time_limit=safe_int(request.POST.get('time_limit'), default=0),
            is_active=request.POST.get('is_active') == 'on',
        )
        messages.success(request, 'Quiz created! Now add questions.')
        return redirect('admin_quiz_edit', quiz_id=quiz.id)

    return render(request, 'signlang/admin/quiz_form.html', {
        'lessons': lessons, 'action': 'Create'
    })


@teacher_or_staff_required
def admin_quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('answers').all()
    lessons = Lesson.objects.all()

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=200)
        lesson_id = safe_int(request.POST.get('lesson'))

        # Validation
        errors = []
        if not title:
            errors.append('Quiz title is required.')
        if not lesson_id:
            errors.append('Please select a lesson.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/quiz_form.html', {
                'quiz': quiz, 'questions': questions, 'lessons': lessons, 'action': 'Edit'
            })

        quiz.title = title
        quiz.lesson_id = lesson_id
        quiz.description = sanitize_string(request.POST.get('description', ''))
        quiz.passing_score = safe_int(request.POST.get('passing_score'), default=70)
        quiz.time_limit = safe_int(request.POST.get('time_limit'), default=0)
        quiz.is_active = request.POST.get('is_active') == 'on'
        quiz.save()
        messages.success(request, 'Quiz updated!')
        return redirect('admin_quiz_list')

    return render(request, 'signlang/admin/quiz_form.html', {
        'quiz': quiz, 'questions': questions, 'lessons': lessons, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        question_text = sanitize_string(request.POST.get('question_text'))

        # Validation
        if not question_text:
            messages.error(request, 'Question text is required.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'action': 'Add'
            })

        # Check if at least one answer is provided
        has_answer = any(request.POST.get(f'answer_{i}') for i in range(1, 5))
        if not has_answer:
            messages.error(request, 'At least one answer is required.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'action': 'Add'
            })

        # Check if a correct answer is selected
        correct_answer = request.POST.get('correct_answer')
        if not correct_answer or not request.POST.get(f'answer_{correct_answer}'):
            messages.error(request, 'Please select which answer is correct.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'action': 'Add'
            })

        question = Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            question_type=request.POST.get('question_type', 'multiple_choice'),
            points=safe_int(request.POST.get('points'), default=1),
            order=safe_int(request.POST.get('order'), default=0),
        )
        # Handle file uploads
        if request.FILES.get('image'):
            question.image = request.FILES['image']
        if request.FILES.get('video'):
            question.video = request.FILES['video']
        question.save()

        # Create answers
        for i in range(1, 5):
            answer_text = request.POST.get(f'answer_{i}')
            if answer_text:
                Answer.objects.create(
                    question=question,
                    answer_text=sanitize_string(answer_text),
                    is_correct=(request.POST.get('correct_answer') == str(i)),
                    explanation=sanitize_string(request.POST.get(f'explanation_{i}', ''))
                )
        messages.success(request, 'Question added!')
        return redirect('admin_quiz_edit', quiz_id=quiz.id)

    return render(request, 'signlang/admin/question_form.html', {
        'quiz': quiz, 'action': 'Add'
    })


@teacher_or_staff_required
def admin_question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted!')
    return redirect('admin_quiz_edit', quiz_id=quiz_id)


@teacher_or_staff_required
def admin_question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz
    answers = list(question.answers.all())

    if request.method == 'POST':
        question_text = sanitize_string(request.POST.get('question_text'))

        # Validation
        if not question_text:
            messages.error(request, 'Question text is required.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'question': question, 'answers': answers, 'action': 'Edit'
            })

        # Check if at least one answer is provided
        has_answer = any(request.POST.get(f'answer_{i}') for i in range(1, 5))
        if not has_answer:
            messages.error(request, 'At least one answer is required.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'question': question, 'answers': answers, 'action': 'Edit'
            })

        # Check if a correct answer is selected
        correct_answer = request.POST.get('correct_answer')
        if not correct_answer or not request.POST.get(f'answer_{correct_answer}'):
            messages.error(request, 'Please select which answer is correct.')
            return render(request, 'signlang/admin/question_form.html', {
                'quiz': quiz, 'question': question, 'answers': answers, 'action': 'Edit'
            })

        question.question_text = question_text
        question.question_type = request.POST.get('question_type', 'multiple_choice')
        question.points = safe_int(request.POST.get('points'), default=1)
        question.order = safe_int(request.POST.get('order'), default=0)
        if request.FILES.get('image'):
            question.image = request.FILES['image']
        if request.FILES.get('video'):
            question.video = request.FILES['video']
        question.save()

        # Update answers
        question.answers.all().delete()
        for i in range(1, 5):
            answer_text = request.POST.get(f'answer_{i}')
            if answer_text:
                Answer.objects.create(
                    question=question,
                    answer_text=sanitize_string(answer_text),
                    is_correct=(request.POST.get('correct_answer') == str(i)),
                    explanation=sanitize_string(request.POST.get(f'explanation_{i}', ''))
                )
        messages.success(request, 'Question updated!')
        return redirect('admin_quiz_edit', quiz_id=quiz.id)

    return render(request, 'signlang/admin/question_form.html', {
        'quiz': quiz, 'question': question, 'answers': answers, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted!')
        return redirect('admin_quiz_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Quiz',
        'item_name': quiz.title,
        'cancel_url': '/manage/quizzes/'
    })


@teacher_or_staff_required
def admin_video_category_delete(request, category_id):
    category = get_object_or_404(VideoCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Video category deleted!')
        return redirect('admin_video_category_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Video Category',
        'item_name': category.name,
        'cancel_url': '/manage/video-categories/'
    })


# Vocabulary Management
@teacher_or_staff_required
def admin_vocabulary_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    vocabularies = lesson.vocabularies.all()
    return render(request, 'signlang/admin/vocabulary_list.html', {
        'lesson': lesson, 'vocabularies': vocabularies
    })


@teacher_or_staff_required
def admin_vocabulary_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        word = sanitize_string(request.POST.get('word'), max_length=100)
        meaning = sanitize_string(request.POST.get('meaning'), max_length=255)

        # Validation
        errors = []
        if not word:
            errors.append('Word is required.')
        if not meaning:
            errors.append('Meaning is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/vocabulary_form.html', {
                'lesson': lesson, 'action': 'Add'
            })

        vocab = Vocabulary.objects.create(
            lesson=lesson,
            word=word,
            meaning=meaning,
            description=sanitize_string(request.POST.get('description', '')),
            order=safe_int(request.POST.get('order'), default=0),
        )
        if request.FILES.get('image'):
            vocab.image = request.FILES['image']
        if request.FILES.get('video'):
            vocab.video = request.FILES['video']
        vocab.save()
        messages.success(request, 'Vocabulary added!')
        return redirect('admin_vocabulary_list', lesson_id=lesson.id)

    return render(request, 'signlang/admin/vocabulary_form.html', {
        'lesson': lesson, 'action': 'Add'
    })


@teacher_or_staff_required
def admin_vocabulary_edit(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)

    if request.method == 'POST':
        word = sanitize_string(request.POST.get('word'), max_length=100)
        meaning = sanitize_string(request.POST.get('meaning'), max_length=255)

        # Validation
        errors = []
        if not word:
            errors.append('Word is required.')
        if not meaning:
            errors.append('Meaning is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/vocabulary_form.html', {
                'vocab': vocab, 'lesson': vocab.lesson, 'action': 'Edit'
            })

        vocab.word = word
        vocab.meaning = meaning
        vocab.description = sanitize_string(request.POST.get('description', ''))
        vocab.order = safe_int(request.POST.get('order'), default=0)
        if request.FILES.get('image'):
            vocab.image = request.FILES['image']
        if request.FILES.get('video'):
            vocab.video = request.FILES['video']
        vocab.save()
        messages.success(request, 'Vocabulary updated!')
        return redirect('admin_vocabulary_list', lesson_id=vocab.lesson.id)

    return render(request, 'signlang/admin/vocabulary_form.html', {
        'vocab': vocab, 'lesson': vocab.lesson, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_vocabulary_delete(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id)
    lesson_id = vocab.lesson.id
    if request.method == 'POST':
        vocab.delete()
        messages.success(request, 'Vocabulary deleted!')
    return redirect('admin_vocabulary_list', lesson_id=lesson_id)


# User Management
@teacher_or_staff_required
def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')

    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'signlang/admin/user_list.html', {
        'users': page_obj,
        'page_obj': page_obj
    })


@teacher_or_staff_required
@require_POST
def admin_toggle_teacher(request, user_id):
    """Toggle teacher status for a user (staff only)"""
    # Only staff can make teachers
    if not request.user.is_staff:
        messages.error(request, 'Only administrators can manage teacher roles.')
        return redirect('admin_user_list')

    user = get_object_or_404(User, id=user_id)

    # Don't allow changing own status or superuser status
    if user == request.user:
        messages.error(request, 'You cannot change your own role.')
        return redirect('admin_user_list')

    if user.is_superuser:
        messages.error(request, 'Cannot change superuser roles.')
        return redirect('admin_user_list')

    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_teacher = not profile.is_teacher
    profile.save()

    if profile.is_teacher:
        messages.success(request, f'{user.username} is now a teacher.')
    else:
        messages.success(request, f'{user.username} is no longer a teacher.')

    return redirect('admin_user_list')


# Report Management
@teacher_or_staff_required
def admin_report_list(request):
    reports = Report.objects.select_related('post', 'reporter').order_by('-created_at')

    # Filter by status
    status = request.GET.get('status')
    if status:
        reports = reports.filter(status=status)

    # Pagination
    paginator = Paginator(reports, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'signlang/admin/report_list.html', {
        'reports': page_obj,
        'page_obj': page_obj
    })


@teacher_or_staff_required
def admin_report_resolve(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'resolve':
            report.status = 'resolved'
            report.save()
        elif action == 'delete_post':
            report.post.delete()
            report.status = 'resolved'
            report.save()
        messages.success(request, 'Report handled!')
    return redirect('admin_report_list')


# ============ FEATURED CARD MANAGEMENT ============

@teacher_or_staff_required
def admin_featured_card_list(request):
    cards = FeaturedCard.objects.all().order_by('section', 'order')
    return render(request, 'signlang/admin/featured_card_list.html', {'cards': cards})


@teacher_or_staff_required
def admin_featured_card_create(request):
    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=100)
        description = sanitize_string(request.POST.get('description', ''), max_length=200)
        section = request.POST.get('section', 'common_sentences')
        icon = request.POST.get('icon', 'fa-comment-dots')
        color = request.POST.get('color', 'blue')
        link = sanitize_string(request.POST.get('link', ''), max_length=255)
        order = safe_int(request.POST.get('order'), default=0)
        is_active = request.POST.get('is_active') == 'on'

        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not link:
            errors.append('Link URL is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/featured_card_form.html', {'action': 'Create'})

        FeaturedCard.objects.create(
            title=title,
            description=description,
            section=section,
            icon=icon,
            color=color,
            link=link,
            order=order,
            is_active=is_active
        )
        messages.success(request, 'Featured card created!')
        return redirect('admin_featured_card_list')

    return render(request, 'signlang/admin/featured_card_form.html', {'action': 'Create'})


@teacher_or_staff_required
def admin_featured_card_edit(request, card_id):
    card = get_object_or_404(FeaturedCard, id=card_id)

    if request.method == 'POST':
        title = sanitize_string(request.POST.get('title'), max_length=100)
        link = sanitize_string(request.POST.get('link', ''), max_length=255)

        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not link:
            errors.append('Link URL is required.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signlang/admin/featured_card_form.html', {
                'card': card, 'action': 'Edit'
            })

        card.title = title
        card.description = sanitize_string(request.POST.get('description', ''), max_length=200)
        card.section = request.POST.get('section', 'common_sentences')
        card.icon = request.POST.get('icon', 'fa-comment-dots')
        card.color = request.POST.get('color', 'blue')
        card.link = link
        card.order = safe_int(request.POST.get('order'), default=0)
        card.is_active = request.POST.get('is_active') == 'on'

        card.save()
        messages.success(request, 'Featured card updated!')
        return redirect('admin_featured_card_list')

    return render(request, 'signlang/admin/featured_card_form.html', {
        'card': card, 'action': 'Edit'
    })


@teacher_or_staff_required
def admin_featured_card_delete(request, card_id):
    card = get_object_or_404(FeaturedCard, id=card_id)
    if request.method == 'POST':
        card.delete()
        messages.success(request, 'Featured card deleted!')
        return redirect('admin_featured_card_list')
    return render(request, 'signlang/admin/delete_confirm.html', {
        'item_type': 'Featured Card',
        'item_name': card.title,
        'cancel_url': '/manage/featured-cards/'
    })


# ============ CSV EXPORT ============

@teacher_or_staff_required
def export_users_csv(request):
    """Export users with their stats to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    response.write('\ufeff')  # UTF-8 BOM for Excel

    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Email', 'First Name', 'Last Name',
        'Date Joined', 'Last Login', 'Is Staff', 'Is Active',
        'Level', 'Total XP', 'Lessons Completed', 'Quizzes Passed', 'Current Streak'
    ])

    users = User.objects.all().order_by('-date_joined')
    for user in users:
        # Get user stats
        try:
            points = UserPoints.objects.get(user=user)
            level = points.level
            total_xp = points.total_points
        except UserPoints.DoesNotExist:
            level = 1
            total_xp = 0

        try:
            streak = UserStreak.objects.get(user=user)
            current_streak = streak.current_streak
        except UserStreak.DoesNotExist:
            current_streak = 0

        lessons_completed = UserProgress.objects.filter(user=user, status='completed').count()
        quizzes_passed = QuizAttempt.objects.filter(user=user, passed=True).count()

        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.date_joined.strftime('%Y-%m-%d %H:%M'),
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
            'Yes' if user.is_staff else 'No',
            'Yes' if user.is_active else 'No',
            level,
            total_xp,
            lessons_completed,
            quizzes_passed,
            current_streak
        ])

    return response


@teacher_or_staff_required
def export_progress_csv(request):
    """Export user progress data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_progress_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Email', 'Lesson', 'Category', 'Difficulty',
        'Status', 'Score', 'Time Spent (min)', 'Started At', 'Completed At'
    ])

    progress_list = UserProgress.objects.all().select_related(
        'user', 'lesson', 'lesson__category'
    ).order_by('-last_accessed')

    for progress in progress_list:
        writer.writerow([
            progress.user.username,
            progress.user.email,
            progress.lesson.title,
            progress.lesson.category.name if progress.lesson.category else '',
            progress.lesson.get_difficulty_display(),
            progress.get_status_display(),
            progress.score or 0,
            progress.time_spent or 0,
            progress.started_at.strftime('%Y-%m-%d %H:%M') if progress.started_at else '',
            progress.completed_at.strftime('%Y-%m-%d %H:%M') if progress.completed_at else ''
        ])

    return response


@teacher_or_staff_required
def export_quiz_results_csv(request):
    """Export quiz results to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quiz_results_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Email', 'Quiz', 'Lesson', 'Score', 'Max Score',
        'Percentage', 'Passed', 'Completed At'
    ])

    attempts = QuizAttempt.objects.all().select_related(
        'user', 'quiz', 'quiz__lesson'
    ).order_by('-completed_at')

    for attempt in attempts:
        percentage = round(attempt.score / attempt.max_score * 100, 1) if attempt.max_score > 0 else 0
        writer.writerow([
            attempt.user.username,
            attempt.user.email,
            attempt.quiz.title,
            attempt.quiz.lesson.title if attempt.quiz.lesson else '',
            attempt.score,
            attempt.max_score,
            f'{percentage}%',
            'Yes' if attempt.passed else 'No',
            attempt.completed_at.strftime('%Y-%m-%d %H:%M') if attempt.completed_at else ''
        ])

    return response


@teacher_or_staff_required
def export_lessons_csv(request):
    """Export lessons to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lessons_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Slug', 'Category', 'Difficulty', 'Is Published',
        'Vocabulary Count', 'Has Quiz', 'Total Completions', 'Created At'
    ])

    lessons = Lesson.objects.all().select_related('category').order_by('category__name', 'title')

    for lesson in lessons:
        vocab_count = lesson.vocabularies.count()
        has_quiz = Quiz.objects.filter(lesson=lesson, is_active=True).exists()
        completions = UserProgress.objects.filter(lesson=lesson, status='completed').count()

        writer.writerow([
            lesson.title,
            lesson.slug,
            lesson.category.name if lesson.category else '',
            lesson.get_difficulty_display(),
            'Yes' if lesson.is_published else 'No',
            vocab_count,
            'Yes' if has_quiz else 'No',
            completions,
            lesson.created_at.strftime('%Y-%m-%d %H:%M') if lesson.created_at else ''
        ])

    return response


@teacher_or_staff_required
def export_vocabulary_csv(request):
    """Export vocabulary to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vocabulary_export.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Word', 'Meaning', 'Lesson', 'Category', 'Has Image', 'Has Video', 'Order'
    ])

    vocabulary = Vocabulary.objects.all().select_related(
        'lesson', 'lesson__category'
    ).order_by('lesson__category__name', 'lesson__title', 'order')

    for vocab in vocabulary:
        writer.writerow([
            vocab.word,
            vocab.meaning,
            vocab.lesson.title if vocab.lesson else '',
            vocab.lesson.category.name if vocab.lesson and vocab.lesson.category else '',
            'Yes' if vocab.image else 'No',
            'Yes' if vocab.video_url else 'No',
            vocab.order
        ])

    return response


# ============ AI CHATBOT ============

@login_required
@require_POST
def chatbot_api(request):
    """AI Chatbot API endpoint using Groq"""

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Check if API key is configured
        api_key = settings.GROQ_API_KEY
        if not api_key:
            return JsonResponse({
                'response': 'Chatbot is not configured. Please set GROQ_API_KEY environment variable.'
            })

        try:
            from groq import Groq
            client = Groq(api_key=api_key)

            # System prompt for sign language assistant
            system_prompt = """You are a helpful assistant for Signox, a sign language learning platform.
You help users learn about sign language, answer questions about lessons, and provide guidance on their learning journey.
Keep responses concise and friendly. If asked about specific signs, describe them clearly.
You can answer in Vietnamese or English based on the user's language.
Focus on being encouraging and supportive of learners."""

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                max_tokens=500,
                temperature=0.7,
            )

            response = chat_completion.choices[0].message.content
            return JsonResponse({'response': response})

        except Exception as e:
            return JsonResponse({
                'response': f'Sorry, I encountered an error. Please try again later.'
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
