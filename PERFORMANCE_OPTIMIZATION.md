# Performance Optimization for Vercel

## Issues Found & Fixes

### 1. **Missing `select_related()` in Dashboard** (Critical)
**Line 306-327 in views.py**

Problem: Loading user relationships without optimization causes N+1 queries.

```python
# BEFORE (SLOW)
progress_list = UserProgress.objects.filter(user=user)
saved_lessons = SavedLesson.objects.filter(user=user).select_related('lesson')[:5]
recent_badges = UserBadge.objects.filter(user=user).select_related('badge')[:3]

# AFTER (OPTIMIZED)
progress_list = UserProgress.objects.filter(user=user).select_related('lesson')
saved_lessons = SavedLesson.objects.filter(user=user).select_related('lesson')[:5]
recent_badges = UserBadge.objects.filter(user=user).select_related('badge')[:3]
```

### 2. **Missing `prefetch_related()` in Forum**
**Line 205-208 in views.py**

```python
# BEFORE
forum_posts = ForumPost.objects.filter(...).select_related('author')[:10]

# AFTER (load comments+likes too)
forum_posts = ForumPost.objects.filter(...).select_related('author').prefetch_related('comments', 'likes')[:10]
```

### 3. **Expensive Count Queries** (High)
**Multiple locations**

Problem: Running `.count()` on large querysets is slow on PostgreSQL.

```python
# BEFORE (Slow on large tables)
completed_count = progress_list.filter(status='completed').count()

# AFTER (Use aggregation)
from django.db.models import Count, Q
stats = progress_list.aggregate(
    completed=Count('id', filter=Q(status='completed')),
    in_progress=Count('id', filter=Q(status='in_progress'))
)
completed_count = stats['completed']
```

### 4. **Quiz List Query** (Medium)
**Line 776-784 in views.py**

Already fixed with `Exists()` but ensure you add more optimization:

```python
quizzes = Quiz.objects.filter(is_active=True).select_related('lesson').prefetch_related('questions')
```

## Quick Fixes to Apply

### Fix 1: Dashboard Optimization
Edit line 306 in `signlang/views.py`:

```python
# Add select_related to progress_list
progress_list = UserProgress.objects.filter(
    user=user
).select_related('lesson__category')  # Add this
```

### Fix 2: Add Caching Layer
Add to top of views.py:

```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Cache homepage for 5 minutes
@cache_page(300)
def home(request):
    # ... existing code
```

### Fix 3: Database Connection Pooling for Vercel
In `KHKT2025/settings.py`, add after DATABASES config:

```python
# Connection pooling for production
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Reuse connections for 10 min
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
    }
```

### Fix 4: Add Database Indexes
Create migration:

```bash
python manage.py makemigrations
```

Add to `signlang/models.py`:

```python
class UserProgress(models.Model):
    # ... existing fields ...
    class Meta:
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-last_accessed']),
        ]

class QuizAttempt(models.Model):
    # ... existing fields ...
    class Meta:
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['user', '-started_at']),
        ]
```

## Vercel-Specific Optimizations

### 1. **Enable Cold Start Caching**
Add `vercel.json`:

```json
{
  "functions": {
    "manage.py": {
      "maxDuration": 60,
      "memory": 1024
    }
  }
}
```

### 2. **Use Environment-Based Optimization**
In `settings.py`:

```python
# Aggressive caching in production
if os.environ.get('ENVIRONMENT') == 'production':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 300,
        }
    }
```

### 3. **Disable Debug Toolbar in Production**
Already in `.gitignore`, but verify `DEBUG=False` in production `.env`.

## Performance Monitoring

### Check Query Count
Add to settings.py (development only):

```python
if DEBUG:
    INSTALLED_APPS += ['django_extensions']
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {'class': 'logging.StreamHandler'},
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
```

Then run locally and check SQL logs.

## Testing on Vercel

### Before Deploy
```bash
# Check for N+1 queries
python manage.py shell_plus
>>> from django.test.utils import override_settings
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext

# Count queries on your views
```

### Monitor on Vercel
1. Check Vercel function logs for slow requests
2. Use Django Debug Toolbar screenshot if available
3. Add timing logs:

```python
import time
@login_required
def dashboard(request):
    start = time.time()
    # ... existing code ...
    print(f"Dashboard loaded in {time.time() - start:.2f}s")
```

## Summary of Changes Needed

| File | Line | Issue | Fix |
|------|------|-------|-----|
| `views.py` | 306 | Missing select_related | Add `.select_related('lesson')` |
| `views.py` | 321 | Already optimized | ✅ Good |
| `views.py` | 326 | Already optimized | ✅ Good |
| `views.py` | 350+ | Heavy counts | Use `.aggregate()` |
| `settings.py` | EOF | No cache config | Add cache settings |
| `models.py` | Meta | No indexes | Add database indexes |

## Expected Improvement
- **Cold start**: 2-3 seconds (Vercel limitation, use "Prerender" if needed)
- **Page load**: 50-70% faster with proper caching
- **Database queries**: 70-80% fewer with select_related
- **Memory usage**: Lower with connection pooling

