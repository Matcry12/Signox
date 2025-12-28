# Rhythm of Signs - Project Status & TODO

## Project Overview

A sign language learning platform built with Django, featuring lessons, quizzes, videos, gamification, and community forum.

---

## Current Database Status

| Content | Count | Status |
|---------|-------|--------|
| Users | 2 | OK |
| Categories | 6 | OK (1 empty: "Work") |
| Lessons | 6 | OK |
| Vocabularies | 23 | OK |
| Quizzes | 6 | OK |
| Videos | 12 | 12 need source files |
| Badges | 18 | OK |
| Featured Cards | 3 | OK |

---

## ✅ COMPLETED - Dark Mode UI Fixes

### All Pages Updated with Dark Mode

| Page | Template | Status |
|------|----------|--------|
| Home | `home.html` | Done |
| Dashboard | `dashboard.html` | Done |
| Forum List | `forum/forum_list.html` | Done |
| Forum Detail | `forum/forum_detail.html` | Done |
| Lesson List | `lessons/lesson_list.html` | Uses CSS vars |
| Lesson Detail | `lessons/lesson_detail.html` | Done |
| Video List | `videos/video_list.html` | Done |
| Video Detail | `videos/video_detail.html` | Done |
| Quiz List | `quiz/quiz_list.html` | Done |
| Quiz Detail | `quiz/quiz_detail.html` | Done |
| Profile | `auth/profile.html` | Done |
| Login/Register | `auth/*.html` | Done |
| Achievements | `gamification/achievements.html` | Done |
| Leaderboard | `gamification/leaderboard.html` | Done |
| My Stats | `gamification/my_stats.html` | Done |
| Notifications | `gamification/notifications.html` | Done |
| Admin Panel | `admin/base_admin.html` | Done |

### Common Dark Mode Issues to Fix

1. **Hardcoded `white` backgrounds** - Replace with `var(--bg-primary)`
2. **Hardcoded text colors** - Use CSS variables that invert
3. **Form inputs** - Need dark backgrounds
4. **Cards and containers** - Need dark backgrounds
5. **Borders** - `var(--gray-200)` doesn't invert well
6. **SVG icons** - May need color adjustments
7. **Images** - Consider adding slight opacity or borders

### Dark Mode Color Palette

```css
/* Dark Background Colors */
--bg-darkest: #0F172A;    /* Page background */
--bg-dark: #1E293B;       /* Cards, containers */
--bg-dark-hover: #334155; /* Hover states, borders */

/* Dark Text Colors */
--text-light: #F1F5F9;    /* Primary text */
--text-muted: #94A3B8;    /* Secondary text */
--text-dim: #64748B;      /* Dimmed text */

/* Dark Border */
--border-dark: #334155;
```

---

## 🟠 MEDIUM PRIORITY - Content & Data

### Missing Content

- [ ] **Work category is EMPTY** - Add lessons about workplace signs
- [ ] **12 videos have no source** - Upload video files or add YouTube URLs

### Video Sources Needed

Videos in database without source files:
1. At the Market: Buying Vegetables, Asking for Prices, Numbers Review, Payment Methods
2. At the Hospital: Describing Symptoms, Emergency Signs, Body Parts, Doctor Conversation
3. Transportation: Taking a Bus, Asking for Directions, Ticket Buying, Location Signs

---

## 🟡 LOW PRIORITY - Enhancements

### Features to Verify

- [ ] Gamification widgets on dashboard (streak, XP, badges)
- [ ] Notification system display
- [ ] Leaderboard weekly/monthly tabs
- [ ] Video view count tracking
- [ ] Forum like animation feedback

### Nice to Have

- [ ] Weekly/monthly point reset cron job
- [ ] Email notifications for badges
- [ ] Social sharing for achievements
- [ ] Keyboard shortcuts for flashcards

---

## ✅ Recently Completed

### UI/UX Improvements
- [x] Modern design system (Indigo color scheme)
- [x] Glassmorphism navbar
- [x] Updated home page with hero section
- [x] Book shelf category display
- [x] XP card with proper shadow/border
- [x] Admin panel redesign
- [x] Custom file upload UI (replaced ugly Django widget)
- [x] Pagination for admin lists (lessons, videos, users, quizzes, reports)
- [x] Search functionality in admin lists
- [x] Delete confirmation modal redesign

### Dark Mode (Partial)
- [x] Dark mode toggle in navbar
- [x] Dark mode toggle in admin panel
- [x] Base CSS variables for dark mode
- [x] localStorage persistence
- [x] System preference detection

### Backend
- [x] FeaturedCard management in custom admin
- [x] Pagination in views with search
- [x] All admin forms with clean file display

---

## 🛠️ Technical Notes

### Template Structure
```
templates/
├── base.html                 # Main layout with dark mode
├── signlang/
│   ├── admin/
│   │   ├── base_admin.html   # Admin layout with dark mode
│   │   └── includes/
│   │       └── pagination.html
│   ├── auth/
│   ├── forum/
│   ├── gamification/
│   ├── lessons/
│   ├── quiz/
│   ├── videos/
│   ├── home.html
│   └── dashboard.html
```

### CSS Variables Location
- Light mode: `base.html` lines 14-90
- Dark mode: `base.html` lines 1148-1175
- Admin dark mode: `base_admin.html` lines 747-971

### Key URLs
| Feature | URL |
|---------|-----|
| Home | `/` |
| Dashboard | `/dashboard/` |
| Lessons | `/lessons/` |
| Videos | `/videos/` |
| Forum | `/forum/` |
| Quizzes | `/quizzes/` |
| Custom Admin | `/manage/` |
| Django Admin | `/admin/` |

---

## 📋 Quick Commands

```bash
# Run server
python manage.py runserver

# Check for issues
python manage.py check

# Initialize all sample data
python manage.py init_sample_data
python manage.py init_gamification
python manage.py init_featured_cards
python manage.py init_sample_quizzes
python manage.py init_sample_videos

# Create superuser
python manage.py createsuperuser
```

---

*Last Updated: December 8, 2025*
