from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# ============================================
# CONSTANTS
# ============================================
LEVEL_THRESHOLDS = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500, 6600, 7800, 9100, 10500]
LEVEL_TITLES = [
    'Newcomer', 'Learner', 'Student', 'Practitioner', 'Skilled',
    'Proficient', 'Advanced', 'Expert', 'Master', 'Grandmaster',
    'Legend', 'Champion', 'Elite', 'Virtuoso', 'Sage'
]


class UserProfile(models.Model):
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='beginner')
    is_teacher = models.BooleanField(default=False, help_text='Teachers can access the management panel')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def can_manage(self):
        """Check if user can access management panel (staff or teacher)"""
        return self.user.is_staff or self.is_teacher


# Signal to auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile automatically when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons')
    description = models.TextField()
    content = models.TextField()
    video_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='lessons/thumbnails/', blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='easy', db_index=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'created_at']

    def __str__(self):
        return self.title


class Vocabulary(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabularies')
    word = models.CharField(max_length=100)
    meaning = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='vocabulary/images/', blank=True, null=True)
    video = models.FileField(upload_to='vocabulary/videos/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Vocabularies"
        ordering = ['order']

    def __str__(self):
        return self.word


class UserProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', db_index=True)
    score = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)  # in seconds
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name_plural = "User Progress"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-last_accessed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class SavedLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} saved {self.lesson.title}"


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.IntegerField(default=70)
    time_limit = models.IntegerField(default=0)  # 0 = no limit, otherwise in minutes
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    image = models.ImageField(upload_to='quiz/questions/', blank=True, null=True)
    video = models.FileField(upload_to='quiz/videos/', blank=True, null=True)
    order = models.IntegerField(default=0)
    points = models.IntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True, help_text="Explanation shown after quiz (why this answer is correct/incorrect)")

    def __str__(self):
        return self.answer_text


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['user', '-started_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.max_score})"


class VideoCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Video Categories"

    def __str__(self):
        return self.name


class Video(models.Model):
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, related_name='videos')
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='easy')
    view_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='forum/images/', blank=True, null=True)
    video = models.FileField(upload_to='forum/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Report(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.post.title}"


class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('complete', 'Complete'),
        ('quiz_pass', 'Quiz Pass'),
        ('quiz_fail', 'Quiz Fail'),
        ('save', 'Save'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    weight = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.lesson.title}"


# ============================================
# GAMIFICATION MODELS
# ============================================

class Badge(models.Model):
    """Defines available badges/achievements"""
    BADGE_TYPES = [
        ('lesson', 'Lesson Milestone'),
        ('quiz', 'Quiz Achievement'),
        ('streak', 'Streak Achievement'),
        ('special', 'Special Achievement'),
    ]

    BADGE_ICONS = [
        ('fa-star', 'Star'),
        ('fa-trophy', 'Trophy'),
        ('fa-medal', 'Medal'),
        ('fa-award', 'Award'),
        ('fa-crown', 'Crown'),
        ('fa-fire', 'Fire'),
        ('fa-bolt', 'Lightning'),
        ('fa-gem', 'Gem'),
        ('fa-book', 'Book'),
        ('fa-graduation-cap', 'Graduation Cap'),
        ('fa-certificate', 'Certificate'),
        ('fa-rocket', 'Rocket'),
        ('fa-heart', 'Heart'),
        ('fa-shield', 'Shield'),
        ('fa-brain', 'Brain'),
    ]

    BADGE_COLORS = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    icon = models.CharField(max_length=30, choices=BADGE_ICONS, default='fa-star')
    color = models.CharField(max_length=20, choices=BADGE_COLORS, default='bronze')
    points_reward = models.IntegerField(default=0)  # XP awarded when earned
    requirement_type = models.CharField(max_length=50)  # e.g., 'lessons_completed', 'quiz_score', 'streak_days'
    requirement_value = models.IntegerField(default=1)  # e.g., 5 for "complete 5 lessons"
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['badge_type', 'order', 'requirement_value']

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Tracks which badges a user has earned"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)  # For notification display

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


class UserStreak(models.Model):
    """Tracks daily learning streaks"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    streak_started_at = models.DateField(null=True, blank=True)
    # Streak Freeze fields
    freeze_count = models.IntegerField(default=2)  # Available freezes
    freeze_used_date = models.DateField(null=True, blank=True)  # Last date freeze was used
    freeze_last_reset = models.DateField(null=True, blank=True)  # Last monthly reset

    def __str__(self):
        return f"{self.user.username}'s Streak: {self.current_streak} days"

    def reset_monthly_freeze(self):
        """Reset freeze count monthly"""
        today = timezone.now().date()
        if self.freeze_last_reset is None or (today.month != self.freeze_last_reset.month or today.year != self.freeze_last_reset.year):
            self.freeze_count = 2
            self.freeze_last_reset = today
            self.save()

    def use_freeze(self):
        """Use a streak freeze to protect the streak"""
        self.reset_monthly_freeze()  # Check if we need to reset

        if self.freeze_count > 0:
            self.freeze_count -= 1
            self.freeze_used_date = timezone.now().date()
            self.save()
            return True
        return False

    def update_streak(self):
        """Update streak based on today's activity"""
        today = timezone.now().date()
        self.reset_monthly_freeze()  # Check monthly reset

        if self.last_activity_date is None:
            # First activity ever
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = today
            self.streak_started_at = today
        elif self.last_activity_date == today:
            # Already logged activity today
            pass
        elif self.last_activity_date == today - timedelta(days=1):
            # Consecutive day - extend streak
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.last_activity_date = today
        elif self.freeze_used_date == today - timedelta(days=1):
            # Freeze was used yesterday, streak is protected
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.last_activity_date = today
        else:
            # Streak broken - reset
            self.current_streak = 1
            self.last_activity_date = today
            self.streak_started_at = today

        self.save()
        return self.current_streak

    @property
    def can_use_freeze_today(self):
        """Check if freeze can be used today"""
        today = timezone.now().date()
        # Check if monthly reset is needed (read-only check, no save)
        needs_reset = self.freeze_last_reset is None or (
            today.month != self.freeze_last_reset.month or
            today.year != self.freeze_last_reset.year
        )
        available_freezes = 2 if needs_reset else self.freeze_count
        # Can use if: have freezes, streak exists, didn't study today, didn't use freeze today
        return (
            available_freezes > 0 and
            self.current_streak > 0 and
            self.last_activity_date != today and
            self.freeze_used_date != today
        )


class UserPoints(models.Model):
    """Tracks XP/points for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    weekly_points = models.IntegerField(default=0)
    monthly_points = models.IntegerField(default=0)
    last_weekly_reset = models.DateField(null=True, blank=True)
    last_monthly_reset = models.DateField(null=True, blank=True)

    # Point sources tracking
    points_from_lessons = models.IntegerField(default=0)
    points_from_quizzes = models.IntegerField(default=0)
    points_from_streaks = models.IntegerField(default=0)
    points_from_badges = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "User Points"

    def __str__(self):
        return f"{self.user.username}: {self.total_points} XP"

    def add_points(self, amount, source='other'):
        """Add points and track source"""
        self.total_points += amount
        self.weekly_points += amount
        self.monthly_points += amount

        if source == 'lesson':
            self.points_from_lessons += amount
        elif source == 'quiz':
            self.points_from_quizzes += amount
        elif source == 'streak':
            self.points_from_streaks += amount
        elif source == 'badge':
            self.points_from_badges += amount

        self.save()

    def reset_weekly(self):
        """Reset weekly points (call this via management command or signal)"""
        self.weekly_points = 0
        self.last_weekly_reset = timezone.now().date()
        self.save()

    def reset_monthly(self):
        """Reset monthly points"""
        self.monthly_points = 0
        self.last_monthly_reset = timezone.now().date()
        self.save()

    @property
    def level(self):
        """Calculate user level based on total points (1-indexed)"""
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if self.total_points < threshold:
                return max(1, i)  # Minimum level is 1
        return len(LEVEL_THRESHOLDS)

    @property
    def level_title(self):
        """Get title based on level"""
        level_index = min(self.level - 1, len(LEVEL_TITLES) - 1)
        return LEVEL_TITLES[max(0, level_index)]

    @property
    def points_to_next_level(self):
        """Points needed for next level"""
        current_level = self.level
        if current_level >= len(LEVEL_THRESHOLDS):
            return 0
        return LEVEL_THRESHOLDS[current_level] - self.total_points

    @property
    def level_progress_percent(self):
        """Progress percentage towards next level"""
        current_level = self.level
        if current_level >= len(LEVEL_THRESHOLDS):
            return 100
        prev_threshold = LEVEL_THRESHOLDS[current_level - 1] if current_level > 1 else 0
        next_threshold = LEVEL_THRESHOLDS[current_level] if current_level < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
        progress = self.total_points - prev_threshold
        needed = next_threshold - prev_threshold
        return int((progress / needed) * 100) if needed > 0 else 100


class Notification(models.Model):
    """User notifications for achievements, milestones, etc."""
    NOTIFICATION_TYPES = [
        ('badge', 'Badge Earned'),
        ('level_up', 'Level Up'),
        ('streak', 'Streak Milestone'),
        ('achievement', 'Achievement'),
        ('reminder', 'Learning Reminder'),
        ('system', 'System Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    icon = models.CharField(max_length=30, default='fa-bell')
    color = models.CharField(max_length=20, default='primary')
    link = models.CharField(max_length=255, blank=True)  # Relative or absolute URL
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class DailyActivity(models.Model):
    """Tracks daily activity for streak calculations and analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    lessons_viewed = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    quizzes_taken = models.IntegerField(default=0)
    quizzes_passed = models.IntegerField(default=0)
    flashcards_reviewed = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# ============================================
# SPACED REPETITION / FLASHCARD MODELS
# ============================================

class VocabularyReview(models.Model):
    """
    Tracks vocabulary learning progress using simplified SM-2 algorithm.
    Supports Anki-style buttons: Again (1), Hard (2), Good (3), Easy (4)
    """
    RATING_CHOICES = [
        (1, 'Again'),   # Complete failure, reset
        (2, 'Hard'),    # Correct but difficult
        (3, 'Good'),    # Correct with some effort
        (4, 'Easy'),    # Perfect recall
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary_reviews')
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='reviews')

    # SM-2 algorithm fields
    ease_factor = models.FloatField(default=2.5)  # E-Factor (1.3 to 2.5+)
    interval = models.IntegerField(default=0)  # Days until next review
    repetitions = models.IntegerField(default=0)  # Successful reps in a row
    next_review = models.DateField(null=True, blank=True)  # When to show again
    last_reviewed = models.DateTimeField(null=True, blank=True)

    # Stats
    total_reviews = models.IntegerField(default=0)
    correct_reviews = models.IntegerField(default=0)  # Rating >= 3
    last_rating = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'vocabulary']
        ordering = ['next_review']

    def __str__(self):
        return f"{self.user.username} - {self.vocabulary.word}"

    def process_rating(self, rating):
        """
        Process a rating (1-4) and update SM-2 parameters.
        Based on SM-2 algorithm with simplifications.
        """
        self.total_reviews += 1
        self.last_rating = rating
        self.last_reviewed = timezone.now()

        if rating >= 3:
            self.correct_reviews += 1

        if rating == 1:  # Again - complete reset
            self.repetitions = 0
            self.interval = 0
            self.next_review = timezone.now().date()  # Review again today
        elif rating == 2:  # Hard - extend slightly
            self.repetitions = 0
            self.interval = max(1, int(self.interval * 0.5))
            self.next_review = timezone.now().date() + timedelta(days=self.interval)
            # Decrease ease factor
            self.ease_factor = max(1.3, self.ease_factor - 0.15)
        elif rating == 3:  # Good - normal progression
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 3
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.repetitions += 1
            self.next_review = timezone.now().date() + timedelta(days=self.interval)
        else:  # Easy (4) - accelerated progression
            if self.repetitions == 0:
                self.interval = 4
            else:
                self.interval = int(self.interval * self.ease_factor * 1.3)
            self.repetitions += 1
            self.next_review = timezone.now().date() + timedelta(days=self.interval)
            # Increase ease factor
            self.ease_factor = min(3.0, self.ease_factor + 0.1)

        self.save()
        return self.interval

    @property
    def is_due(self):
        """Check if this card is due for review"""
        if self.next_review is None:
            return True
        return timezone.now().date() >= self.next_review

    @property
    def mastery_level(self):
        """Calculate mastery level (0-100%) based on repetitions and ease"""
        if self.total_reviews == 0:
            return 0
        # Base on correct rate and repetitions
        correct_rate = (self.correct_reviews / self.total_reviews) * 100
        rep_bonus = min(20, self.repetitions * 5)  # Up to 20% bonus for reps
        return min(100, int(correct_rate * 0.8 + rep_bonus))

    @classmethod
    def get_due_cards(cls, user, lesson=None, limit=20):
        """Get vocabulary cards due for review"""
        today = timezone.now().date()
        queryset = cls.objects.filter(
            user=user
        ).filter(
            models.Q(next_review__lte=today) | models.Q(next_review__isnull=True)
        ).select_related('vocabulary', 'vocabulary__lesson')

        if lesson:
            queryset = queryset.filter(vocabulary__lesson=lesson)

        return queryset[:limit]

    @classmethod
    def get_or_create_for_vocabulary(cls, user, vocabulary):
        """Get or create a review record for a vocabulary item"""
        review, created = cls.objects.get_or_create(
            user=user,
            vocabulary=vocabulary,
            defaults={'next_review': timezone.now().date()}
        )
        return review


# ============================================
# HOME PAGE CONTENT MODELS
# ============================================

class FeaturedCard(models.Model):
    """Dynamic cards for home page sections (e.g., Common Sentences)"""
    CARD_COLORS = [
        ('blue', 'Blue'),
        ('teal', 'Teal'),
        ('indigo', 'Indigo'),
        ('purple', 'Purple'),
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('pink', 'Pink'),
    ]

    ICON_CHOICES = [
        ('fa-comment-dots', 'Comment Dots'),
        ('fa-graduation-cap', 'Graduation Cap'),
        ('fa-briefcase', 'Briefcase'),
        ('fa-home', 'Home'),
        ('fa-heart', 'Heart'),
        ('fa-users', 'Users'),
        ('fa-book', 'Book'),
        ('fa-star', 'Star'),
        ('fa-music', 'Music'),
        ('fa-utensils', 'Food/Utensils'),
        ('fa-plane', 'Travel/Plane'),
        ('fa-hospital', 'Hospital/Medical'),
        ('fa-shopping-cart', 'Shopping'),
        ('fa-futbol', 'Sports'),
        ('fa-palette', 'Art/Palette'),
        ('fa-car', 'Car/Transport'),
        ('fa-phone', 'Phone'),
        ('fa-calendar', 'Calendar'),
        ('fa-clock', 'Clock/Time'),
        ('fa-map-marker-alt', 'Location'),
    ]

    SECTION_CHOICES = [
        ('common_sentences', 'Common Sentences'),
        ('featured', 'Featured Content'),
        ('quick_links', 'Quick Links'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, help_text="Short description (optional)")
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, default='common_sentences')
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='fa-comment-dots')
    color = models.CharField(max_length=20, choices=CARD_COLORS, default='blue')
    link = models.CharField(max_length=255, help_text="URL or path (e.g., /lessons/?category=daily)")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['section', 'order']
        verbose_name = "Featured Card"
        verbose_name_plural = "Featured Cards"

    def __str__(self):
        return f"{self.title} ({self.section})"


# Signal to clear cache when FeaturedCard changes
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache as django_cache


def clear_featured_card_cache(sender, instance, **kwargs):
    """Clear featured card cache when a card is saved or deleted"""
    # Clear cache for the specific section
    django_cache.delete(f'featured_cards_{instance.section}')
    # Also clear all section caches to be safe
    for section_key, _ in FeaturedCard.SECTION_CHOICES:
        django_cache.delete(f'featured_cards_{section_key}')


post_save.connect(clear_featured_card_cache, sender=FeaturedCard)
post_delete.connect(clear_featured_card_cache, sender=FeaturedCard)


class SiteSettings(models.Model):
    """Global site settings manageable from admin"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.key

    @classmethod
    def get(cls, key, default=''):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
