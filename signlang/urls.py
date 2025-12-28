from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home & Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('search/', views.global_search, name='global_search'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('set-language/', views.set_language, name='set_language'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='signlang/auth/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Password Reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='signlang/auth/password_reset.html',
             email_template_name='signlang/auth/password_reset_email.html',
             subject_template_name='signlang/auth/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='signlang/auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='signlang/auth/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='signlang/auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Lessons
    path('categories/', views.category_list, name='category_list'),
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/category/<slug:category_slug>/', views.lesson_list, name='lesson_list_by_category'),
    path('lessons/saved/', views.saved_lessons, name='saved_lessons'),
    path('lesson/<slug:slug>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<slug:slug>/flashcard/', views.flashcard_mode, name='flashcard_mode'),
    path('lesson/<int:lesson_id>/save/', views.save_lesson, name='save_lesson'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),

    # Quiz
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),

    # Videos
    path('videos/', views.video_list, name='video_list'),
    path('video/<slug:slug>/', views.video_detail, name='video_detail'),

    # Forum
    path('forum/', views.forum_list, name='forum_list'),
    path('forum/create/', views.forum_create, name='forum_create'),
    path('forum/<int:post_id>/', views.forum_detail, name='forum_detail'),
    path('forum/<int:post_id>/edit/', views.forum_edit, name='forum_edit'),
    path('forum/<int:post_id>/delete/', views.forum_delete, name='forum_delete'),
    path('forum/<int:post_id>/like/', views.like_post, name='like_post'),
    path('forum/<int:post_id>/report/', views.report_post, name='report_post'),

    # API
    path('api/progress/<int:lesson_id>/', views.api_update_progress, name='api_update_progress'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/activity-calendar/', views.activity_calendar_api, name='activity_calendar_api'),
    path('api/flashcard/rate/', views.flashcard_rate, name='flashcard_rate'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),

    # Gamification
    path('achievements/', views.achievements, name='achievements'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('my-stats/', views.my_stats, name='my_stats'),
    path('streak/freeze/', views.use_streak_freeze, name='use_streak_freeze'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # Custom Admin Panel
    path('manage/', views.admin_dashboard, name='admin_dashboard'),

    # Category Management
    path('manage/categories/', views.admin_category_list, name='admin_category_list'),
    path('manage/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('manage/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('manage/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),

    # Lesson Management
    path('manage/lessons/', views.admin_lesson_list, name='admin_lesson_list'),
    path('manage/lessons/create/', views.admin_lesson_create, name='admin_lesson_create'),
    path('manage/lessons/<int:lesson_id>/edit/', views.admin_lesson_edit, name='admin_lesson_edit'),
    path('manage/lessons/<int:lesson_id>/delete/', views.admin_lesson_delete, name='admin_lesson_delete'),
    path('manage/lessons/<int:lesson_id>/vocabulary/', views.admin_vocabulary_list, name='admin_vocabulary_list'),
    path('manage/lessons/<int:lesson_id>/vocabulary/create/', views.admin_vocabulary_create, name='admin_vocabulary_create'),
    path('manage/vocabulary/<int:vocab_id>/edit/', views.admin_vocabulary_edit, name='admin_vocabulary_edit'),
    path('manage/vocabulary/<int:vocab_id>/delete/', views.admin_vocabulary_delete, name='admin_vocabulary_delete'),

    # Video Category Management
    path('manage/video-categories/', views.admin_video_category_list, name='admin_video_category_list'),
    path('manage/video-categories/create/', views.admin_video_category_create, name='admin_video_category_create'),
    path('manage/video-categories/<int:category_id>/edit/', views.admin_video_category_edit, name='admin_video_category_edit'),
    path('manage/video-categories/<int:category_id>/delete/', views.admin_video_category_delete, name='admin_video_category_delete'),

    # Video Management
    path('manage/videos/', views.admin_video_list, name='admin_video_list'),
    path('manage/videos/create/', views.admin_video_create, name='admin_video_create'),
    path('manage/videos/<int:video_id>/edit/', views.admin_video_edit, name='admin_video_edit'),
    path('manage/videos/<int:video_id>/delete/', views.admin_video_delete, name='admin_video_delete'),

    # Quiz Management
    path('manage/quizzes/', views.admin_quiz_list, name='admin_quiz_list'),
    path('manage/quizzes/create/', views.admin_quiz_create, name='admin_quiz_create'),
    path('manage/quizzes/<int:quiz_id>/edit/', views.admin_quiz_edit, name='admin_quiz_edit'),
    path('manage/quizzes/<int:quiz_id>/delete/', views.admin_quiz_delete, name='admin_quiz_delete'),
    path('manage/quizzes/<int:quiz_id>/questions/create/', views.admin_question_create, name='admin_question_create'),
    path('manage/questions/<int:question_id>/edit/', views.admin_question_edit, name='admin_question_edit'),
    path('manage/questions/<int:question_id>/delete/', views.admin_question_delete, name='admin_question_delete'),

    # User & Report Management
    path('manage/users/', views.admin_user_list, name='admin_user_list'),
    path('manage/users/<int:user_id>/toggle-teacher/', views.admin_toggle_teacher, name='admin_toggle_teacher'),
    path('manage/reports/', views.admin_report_list, name='admin_report_list'),
    path('manage/reports/<int:report_id>/resolve/', views.admin_report_resolve, name='admin_report_resolve'),

    # Featured Cards Management
    path('manage/featured-cards/', views.admin_featured_card_list, name='admin_featured_card_list'),
    path('manage/featured-cards/create/', views.admin_featured_card_create, name='admin_featured_card_create'),
    path('manage/featured-cards/<int:card_id>/edit/', views.admin_featured_card_edit, name='admin_featured_card_edit'),
    path('manage/featured-cards/<int:card_id>/delete/', views.admin_featured_card_delete, name='admin_featured_card_delete'),

    # CSV Export
    path('manage/export/users/', views.export_users_csv, name='export_users_csv'),
    path('manage/export/progress/', views.export_progress_csv, name='export_progress_csv'),
    path('manage/export/quiz-results/', views.export_quiz_results_csv, name='export_quiz_results_csv'),
    path('manage/export/lessons/', views.export_lessons_csv, name='export_lessons_csv'),
    path('manage/export/vocabulary/', views.export_vocabulary_csv, name='export_vocabulary_csv'),
]
