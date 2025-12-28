"""
Gamification Service for Rhythm of Signs
Handles badges, points, streaks, and notifications
"""
from django.utils import timezone
from django.db.models import Count, Sum
from .models import (
    Badge, UserBadge, UserStreak, UserPoints, Notification, DailyActivity,
    UserProgress, QuizAttempt, SavedLesson, ForumPost, Comment
)


# ============================================
# POINT VALUES
# ============================================
POINTS = {
    'lesson_view': 5,
    'lesson_complete': 20,
    'quiz_pass': 30,
    'quiz_perfect': 50,  # 100% score
    'quiz_fail': 5,  # Encouragement points
    'flashcard_session': 10,
    'forum_post': 15,
    'forum_comment': 5,
    'daily_login': 10,
    'streak_bonus_7': 50,
    'streak_bonus_30': 200,
    'streak_bonus_100': 500,
}


# ============================================
# BADGE DEFINITIONS
# ============================================
DEFAULT_BADGES = [
    # Lesson Milestones
    {
        'name': 'First Steps',
        'description': 'Complete your first lesson',
        'badge_type': 'lesson',
        'icon': 'fa-book',
        'color': 'bronze',
        'points_reward': 25,
        'requirement_type': 'lessons_completed',
        'requirement_value': 1,
        'order': 1,
    },
    {
        'name': 'Getting Started',
        'description': 'Complete 5 lessons',
        'badge_type': 'lesson',
        'icon': 'fa-book',
        'color': 'bronze',
        'points_reward': 50,
        'requirement_type': 'lessons_completed',
        'requirement_value': 5,
        'order': 2,
    },
    {
        'name': 'Dedicated Learner',
        'description': 'Complete 10 lessons',
        'badge_type': 'lesson',
        'icon': 'fa-graduation-cap',
        'color': 'silver',
        'points_reward': 100,
        'requirement_type': 'lessons_completed',
        'requirement_value': 10,
        'order': 3,
    },
    {
        'name': 'Knowledge Seeker',
        'description': 'Complete 25 lessons',
        'badge_type': 'lesson',
        'icon': 'fa-brain',
        'color': 'gold',
        'points_reward': 250,
        'requirement_type': 'lessons_completed',
        'requirement_value': 25,
        'order': 4,
    },
    {
        'name': 'Master Student',
        'description': 'Complete 50 lessons',
        'badge_type': 'lesson',
        'icon': 'fa-crown',
        'color': 'platinum',
        'points_reward': 500,
        'requirement_type': 'lessons_completed',
        'requirement_value': 50,
        'order': 5,
    },

    # Quiz Achievements
    {
        'name': 'Quiz Taker',
        'description': 'Pass your first quiz',
        'badge_type': 'quiz',
        'icon': 'fa-star',
        'color': 'bronze',
        'points_reward': 25,
        'requirement_type': 'quizzes_passed',
        'requirement_value': 1,
        'order': 1,
    },
    {
        'name': 'Quiz Master',
        'description': 'Pass 10 quizzes',
        'badge_type': 'quiz',
        'icon': 'fa-trophy',
        'color': 'silver',
        'points_reward': 100,
        'requirement_type': 'quizzes_passed',
        'requirement_value': 10,
        'order': 2,
    },
    {
        'name': 'Perfect Score',
        'description': 'Get 100% on any quiz',
        'badge_type': 'quiz',
        'icon': 'fa-gem',
        'color': 'gold',
        'points_reward': 75,
        'requirement_type': 'perfect_quiz',
        'requirement_value': 1,
        'order': 3,
    },
    {
        'name': 'Quiz Champion',
        'description': 'Pass 25 quizzes',
        'badge_type': 'quiz',
        'icon': 'fa-medal',
        'color': 'gold',
        'points_reward': 250,
        'requirement_type': 'quizzes_passed',
        'requirement_value': 25,
        'order': 4,
    },

    # Streak Achievements
    {
        'name': 'On Fire',
        'description': 'Maintain a 3-day streak',
        'badge_type': 'streak',
        'icon': 'fa-fire',
        'color': 'bronze',
        'points_reward': 30,
        'requirement_type': 'streak_days',
        'requirement_value': 3,
        'order': 1,
    },
    {
        'name': 'Week Warrior',
        'description': 'Maintain a 7-day streak',
        'badge_type': 'streak',
        'icon': 'fa-fire',
        'color': 'silver',
        'points_reward': 75,
        'requirement_type': 'streak_days',
        'requirement_value': 7,
        'order': 2,
    },
    {
        'name': 'Consistency King',
        'description': 'Maintain a 30-day streak',
        'badge_type': 'streak',
        'icon': 'fa-fire',
        'color': 'gold',
        'points_reward': 300,
        'requirement_type': 'streak_days',
        'requirement_value': 30,
        'order': 3,
    },
    {
        'name': 'Unstoppable',
        'description': 'Maintain a 100-day streak',
        'badge_type': 'streak',
        'icon': 'fa-fire',
        'color': 'diamond',
        'points_reward': 1000,
        'requirement_type': 'streak_days',
        'requirement_value': 100,
        'order': 4,
    },

    # Special Achievements
    {
        'name': 'Social Butterfly',
        'description': 'Create your first forum post',
        'badge_type': 'special',
        'icon': 'fa-comments',
        'color': 'bronze',
        'points_reward': 20,
        'requirement_type': 'forum_posts',
        'requirement_value': 1,
        'order': 1,
    },
    {
        'name': 'Bookworm',
        'description': 'Save 10 lessons to your collection',
        'badge_type': 'special',
        'icon': 'fa-bookmark',
        'color': 'silver',
        'points_reward': 50,
        'requirement_type': 'saved_lessons',
        'requirement_value': 10,
        'order': 2,
    },
    {
        'name': 'Early Bird',
        'description': 'Complete a lesson before 8 AM',
        'badge_type': 'special',
        'icon': 'fa-sun',
        'color': 'gold',
        'points_reward': 40,
        'requirement_type': 'early_learner',
        'requirement_value': 1,
        'order': 3,
    },
    {
        'name': 'Night Owl',
        'description': 'Complete a lesson after 10 PM',
        'badge_type': 'special',
        'icon': 'fa-moon',
        'color': 'silver',
        'points_reward': 40,
        'requirement_type': 'night_learner',
        'requirement_value': 1,
        'order': 4,
    },
    {
        'name': 'Explorer',
        'description': 'Study lessons from 5 different categories',
        'badge_type': 'special',
        'icon': 'fa-compass',
        'color': 'gold',
        'points_reward': 100,
        'requirement_type': 'categories_explored',
        'requirement_value': 5,
        'order': 5,
    },
]


def initialize_badges():
    """Create default badges if they don't exist"""
    for badge_data in DEFAULT_BADGES:
        Badge.objects.get_or_create(
            name=badge_data['name'],
            defaults=badge_data
        )


# ============================================
# USER INITIALIZATION
# ============================================
def ensure_user_gamification(user):
    """Ensure user has streak and points records"""
    UserStreak.objects.get_or_create(user=user)
    UserPoints.objects.get_or_create(user=user)


# ============================================
# POINTS SYSTEM
# ============================================
def award_points(user, amount, source='other'):
    """Award points to user and check for level up"""
    ensure_user_gamification(user)
    user_points = user.points

    old_level = user_points.level
    user_points.add_points(amount, source)
    new_level = user_points.level

    # Track points in daily activity for heatmap
    update_daily_activity(user, 'points', amount)

    # Check for level up
    if new_level > old_level:
        create_notification(
            user=user,
            notification_type='level_up',
            title=f'Level Up! You are now Level {new_level}',
            message=f'Congratulations! You\'ve reached the rank of {user_points.level_title}!',
            icon='fa-arrow-up',
            color='success'
        )

    return amount


# ============================================
# STREAK SYSTEM
# ============================================
def update_user_streak(user):
    """Update user's streak and award streak bonuses"""
    ensure_user_gamification(user)
    streak = user.streak

    old_streak = streak.current_streak
    new_streak = streak.update_streak()

    # Award streak milestone bonuses
    streak_milestones = {
        7: POINTS['streak_bonus_7'],
        30: POINTS['streak_bonus_30'],
        100: POINTS['streak_bonus_100'],
    }

    for milestone, bonus in streak_milestones.items():
        if old_streak < milestone <= new_streak:
            award_points(user, bonus, 'streak')
            create_notification(
                user=user,
                notification_type='streak',
                title=f'{milestone}-Day Streak!',
                message=f'Amazing! You\'ve maintained a {milestone}-day learning streak! +{bonus} XP',
                icon='fa-fire',
                color='warning'
            )

    # Check for streak badges
    check_badges(user, 'streak_days', new_streak)

    return new_streak


# ============================================
# DAILY ACTIVITY TRACKING
# ============================================
def update_daily_activity(user, activity_type, value=1):
    """Update daily activity tracking"""
    today = timezone.now().date()
    activity, created = DailyActivity.objects.get_or_create(
        user=user,
        date=today
    )

    if activity_type == 'lesson_view':
        activity.lessons_viewed += value
    elif activity_type == 'lesson_complete':
        activity.lessons_completed += value
    elif activity_type == 'quiz_taken':
        activity.quizzes_taken += value
    elif activity_type == 'quiz_passed':
        activity.quizzes_passed += value
    elif activity_type == 'flashcard':
        activity.flashcards_reviewed += value
    elif activity_type == 'points':
        activity.points_earned += value
    elif activity_type == 'time':
        activity.time_spent_minutes += value

    activity.save()
    return activity


# ============================================
# BADGE CHECKING
# ============================================
def check_badges(user, requirement_type, value):
    """Check if user has earned any new badges"""
    badges = Badge.objects.filter(
        requirement_type=requirement_type,
        requirement_value__lte=value,
        is_active=True
    ).exclude(
        earned_by__user=user
    )

    for badge in badges:
        award_badge(user, badge)


def award_badge(user, badge):
    """Award a badge to user"""
    user_badge, created = UserBadge.objects.get_or_create(
        user=user,
        badge=badge
    )

    if created:
        # Award points for earning badge
        if badge.points_reward > 0:
            award_points(user, badge.points_reward, 'badge')

        # Create notification
        create_notification(
            user=user,
            notification_type='badge',
            title=f'Badge Earned: {badge.name}',
            message=f'{badge.description}. +{badge.points_reward} XP',
            icon=badge.icon,
            color=badge.color,
            link='/achievements/'
        )

        return True
    return False


def check_all_badges(user):
    """Check all badge types for a user"""
    # Count completed lessons
    completed_lessons = UserProgress.objects.filter(
        user=user,
        status='completed'
    ).count()
    check_badges(user, 'lessons_completed', completed_lessons)

    # Count passed quizzes
    passed_quizzes = QuizAttempt.objects.filter(
        user=user,
        passed=True
    ).count()
    check_badges(user, 'quizzes_passed', passed_quizzes)

    # Check for perfect quizzes
    perfect_quizzes = QuizAttempt.objects.filter(
        user=user,
        score=100
    ).count()
    check_badges(user, 'perfect_quiz', perfect_quizzes)

    # Check saved lessons
    saved = SavedLesson.objects.filter(user=user).count()
    check_badges(user, 'saved_lessons', saved)

    # Check forum posts
    forum_posts = ForumPost.objects.filter(author=user).count()
    check_badges(user, 'forum_posts', forum_posts)

    # Check categories explored
    categories = UserProgress.objects.filter(
        user=user,
        status='completed'
    ).values('lesson__category').distinct().count()
    check_badges(user, 'categories_explored', categories)

    # Check streak
    try:
        streak = user.streak.current_streak
        check_badges(user, 'streak_days', streak)
    except UserStreak.DoesNotExist:
        pass


# ============================================
# EVENT HANDLERS
# ============================================
def on_lesson_view(user, lesson):
    """Handle lesson view event"""
    ensure_user_gamification(user)
    update_user_streak(user)
    award_points(user, POINTS['lesson_view'], 'lesson')
    update_daily_activity(user, 'lesson_view')


def on_lesson_complete(user, lesson):
    """Handle lesson completion event"""
    ensure_user_gamification(user)
    update_user_streak(user)
    award_points(user, POINTS['lesson_complete'], 'lesson')
    update_daily_activity(user, 'lesson_complete')

    # Check for time-based badges
    hour = timezone.now().hour
    if hour < 8:
        check_badges(user, 'early_learner', 1)
    elif hour >= 22:
        check_badges(user, 'night_learner', 1)

    # Check lesson count badges
    completed = UserProgress.objects.filter(user=user, status='completed').count()
    check_badges(user, 'lessons_completed', completed)

    # Check category exploration
    categories = UserProgress.objects.filter(
        user=user,
        status='completed'
    ).values('lesson__category').distinct().count()
    check_badges(user, 'categories_explored', categories)


def on_quiz_complete(user, quiz_attempt):
    """Handle quiz completion event"""
    ensure_user_gamification(user)
    update_user_streak(user)
    update_daily_activity(user, 'quiz_taken')

    if quiz_attempt.passed:
        update_daily_activity(user, 'quiz_passed')

        if quiz_attempt.max_score > 0 and quiz_attempt.score == quiz_attempt.max_score:
            # Perfect score (100%)
            award_points(user, POINTS['quiz_perfect'], 'quiz')
            # Count perfect quizzes where score equals max_score
            from django.db.models import F
            perfect_count = QuizAttempt.objects.filter(
                user=user,
                score=F('max_score')
            ).exclude(max_score=0).count()
            check_badges(user, 'perfect_quiz', perfect_count)
        else:
            award_points(user, POINTS['quiz_pass'], 'quiz')

        passed_count = QuizAttempt.objects.filter(user=user, passed=True).count()
        check_badges(user, 'quizzes_passed', passed_count)
    else:
        award_points(user, POINTS['quiz_fail'], 'quiz')


def on_flashcard_session(user, lesson):
    """Handle flashcard practice session"""
    ensure_user_gamification(user)
    update_user_streak(user)
    award_points(user, POINTS['flashcard_session'], 'lesson')
    update_daily_activity(user, 'flashcard')


def on_forum_post(user):
    """Handle forum post creation"""
    ensure_user_gamification(user)
    award_points(user, POINTS['forum_post'], 'other')
    post_count = ForumPost.objects.filter(author=user).count()
    check_badges(user, 'forum_posts', post_count)


def on_forum_comment(user):
    """Handle forum comment"""
    ensure_user_gamification(user)
    award_points(user, POINTS['forum_comment'], 'other')


def on_save_lesson(user):
    """Handle lesson save event"""
    saved_count = SavedLesson.objects.filter(user=user).count()
    check_badges(user, 'saved_lessons', saved_count)


# ============================================
# NOTIFICATIONS
# ============================================
def create_notification(user, notification_type, title, message, icon='fa-bell', color='primary', link=''):
    """Create a notification for user"""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        icon=icon,
        color=color,
        link=link
    )


def get_unread_notifications(user, limit=10):
    """Get unread notifications for user"""
    return Notification.objects.filter(
        user=user,
        is_read=False
    )[:limit]


def mark_notifications_read(user, notification_ids=None):
    """Mark notifications as read"""
    qs = Notification.objects.filter(user=user)
    if notification_ids:
        qs = qs.filter(id__in=notification_ids)
    qs.update(is_read=True)


def mark_badges_seen(user):
    """Mark new badges as seen"""
    UserBadge.objects.filter(user=user, is_new=True).update(is_new=False)


# ============================================
# LEADERBOARD
# ============================================
def get_leaderboard(period='all', limit=20):
    """Get leaderboard data"""
    if period == 'weekly':
        field = 'weekly_points'
    elif period == 'monthly':
        field = 'monthly_points'
    else:
        field = 'total_points'

    return UserPoints.objects.select_related('user', 'user__profile').order_by(
        f'-{field}'
    )[:limit]


def get_user_rank(user, period='all'):
    """Get user's rank in leaderboard"""
    try:
        user_points = user.points
        if period == 'weekly':
            points = user_points.weekly_points
            higher = UserPoints.objects.filter(weekly_points__gt=points).count()
        elif period == 'monthly':
            points = user_points.monthly_points
            higher = UserPoints.objects.filter(monthly_points__gt=points).count()
        else:
            points = user_points.total_points
            higher = UserPoints.objects.filter(total_points__gt=points).count()
        return higher + 1
    except UserPoints.DoesNotExist:
        return None


# ============================================
# STATISTICS
# ============================================
def get_user_stats(user):
    """Get comprehensive user statistics"""
    ensure_user_gamification(user)

    stats = {
        'points': user.points,
        'streak': user.streak,
        'badges_earned': UserBadge.objects.filter(user=user).count(),
        'badges_total': Badge.objects.filter(is_active=True).count(),
        'lessons_completed': UserProgress.objects.filter(user=user, status='completed').count(),
        'quizzes_passed': QuizAttempt.objects.filter(user=user, passed=True).count(),
        'rank': get_user_rank(user),
        'recent_badges': UserBadge.objects.filter(user=user).select_related('badge')[:5],
    }

    return stats
