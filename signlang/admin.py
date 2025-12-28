from django.contrib import admin
from .models import (
    UserProfile, Category, Lesson, Vocabulary, UserProgress, SavedLesson,
    Quiz, Question, Answer, QuizAttempt, VideoCategory, Video,
    ForumPost, Comment, Like, Report, UserInteraction,
    Badge, UserBadge, UserStreak, UserPoints, Notification, DailyActivity,
    FeaturedCard, SiteSettings
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_level', 'created_at']
    list_filter = ['skill_level']
    search_fields = ['user__username', 'user__email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class VocabularyInline(admin.TabularInline):
    model = Vocabulary
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'is_published', 'created_at']
    list_filter = ['category', 'difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [VocabularyInline]
    ordering = ['category', 'order']


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ['word', 'meaning', 'lesson', 'order']
    list_filter = ['lesson__category']
    search_fields = ['word', 'meaning']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'score', 'last_accessed']
    list_filter = ['status']
    search_fields = ['user__username', 'lesson__title']


@admin.register(SavedLesson)
class SavedLessonAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'saved_at']
    search_fields = ['user__username', 'lesson__title']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'lesson__title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points']
    list_filter = ['question_type', 'quiz']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'question', 'is_correct']
    list_filter = ['is_correct']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'max_score', 'passed', 'completed_at']
    list_filter = ['passed', 'quiz']
    search_fields = ['user__username']


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'view_count', 'is_published']
    list_filter = ['category', 'difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['title', 'content', 'author__username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    search_fields = ['content', 'author__username']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['post', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason']
    actions = ['mark_reviewed', 'mark_resolved']

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_reviewed.short_description = "Mark selected as reviewed"

    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_resolved.short_description = "Mark selected as resolved"


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'interaction_type', 'weight', 'created_at']
    list_filter = ['interaction_type']
    search_fields = ['user__username', 'lesson__title']


# ============ GAMIFICATION ADMIN ============

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'color', 'points_reward', 'requirement_type', 'requirement_value', 'is_active']
    list_filter = ['badge_type', 'color', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['badge_type', 'order']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'badge_type')
        }),
        ('Appearance', {
            'fields': ('icon', 'color')
        }),
        ('Requirements', {
            'fields': ('requirement_type', 'requirement_value', 'points_reward')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at', 'is_new']
    list_filter = ['badge', 'is_new']
    search_fields = ['user__username', 'badge__name']
    date_hierarchy = 'earned_at'


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    search_fields = ['user__username']
    ordering = ['-current_streak']


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'level', 'weekly_points', 'monthly_points']
    search_fields = ['user__username']
    ordering = ['-total_points']
    readonly_fields = ['level', 'level_title']

    def level(self, obj):
        return obj.level
    level.short_description = 'Level'

    def level_title(self, obj):
        return obj.level_title
    level_title.short_description = 'Title'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__username', 'title', 'message']
    date_hierarchy = 'created_at'


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'lessons_viewed', 'lessons_completed', 'quizzes_passed', 'points_earned']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'


# ============ HOME PAGE CONTENT ADMIN ============

@admin.register(FeaturedCard)
class FeaturedCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'color', 'icon', 'order', 'is_active']
    list_filter = ['section', 'color', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['section', 'order']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'section', 'link')
        }),
        ('Appearance', {
            'fields': ('icon', 'color')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description']
    search_fields = ['key', 'description']
    ordering = ['key']
