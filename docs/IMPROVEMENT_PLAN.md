# Rhythm of Signs - Improvement & Feature Plan

> **Document Version:** 1.0
> **Last Updated:** December 12, 2025
> **Purpose:** Comprehensive roadmap for website improvements with difficulty and effectiveness ratings

---

## Rating System

| Difficulty | Description | Time Estimate |
|------------|-------------|---------------|
| 1 - Very Easy | Simple changes, < 1 hour | Few hours |
| 2 - Easy | Basic implementation, existing patterns | 1-2 days |
| 3 - Medium | Moderate complexity, some research needed | 3-5 days |
| 4 - Hard | Complex implementation, new systems | 1-2 weeks |
| 5 - Very Hard | Major feature, significant architecture changes | 2-4 weeks |

| Effectiveness | Description |
|---------------|-------------|
| 1 - Low | Minor improvement, nice to have |
| 2 - Moderate | Noticeable improvement |
| 3 - Good | Significant user benefit |
| 4 - High | Major feature, high user impact |
| 5 - Critical | Essential for success/competition |

**Priority Score** = Effectiveness - (Difficulty × 0.5)
*Higher score = Higher priority*

---

## TIER 1: CRITICAL SECURITY & BASICS

### 1.1 Password Reset Functionality
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 5 - Critical |
| Priority Score | **4.0** |

**Current State:** Users cannot recover accounts if they forget password
**Solution:** Implement Django's built-in password reset views with email

**Implementation:**
- Configure email backend (SMTP)
- Add password reset URLs
- Create password reset templates
- Add "Forgot Password?" link on login page

---

### 1.2 Email Verification on Registration
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 4 - High |
| Priority Score | **2.5** |

**Current State:** Anyone can register with any email, potential spam accounts
**Solution:** Send verification email, require click-to-verify

**Implementation:**
- Add `is_verified` field to UserProfile
- Send verification email on registration
- Create verification view and template
- Restrict access until verified

---

### 1.3 Unit Test Suite
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 4 - High |
| Priority Score | **2.5** |

**Current State:** `tests.py` is empty, no automated testing
**Solution:** Implement pytest with minimum 70% coverage

**Implementation:**
- Setup pytest-django
- Write model tests (User, Lesson, Quiz)
- Write view tests (authentication, lessons, quizzes)
- Write form validation tests
- Add CI/CD pipeline (GitHub Actions)

---

## TIER 2: USER EXPERIENCE IMPROVEMENTS

### 2.1 Global Search
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 4 - High |
| Priority Score | **3.0** |

**Current State:** No unified search, must navigate to each section
**Solution:** Add search bar in navbar searching across lessons, videos, vocabulary, forum

**Implementation:**
- Add search input in navbar
- Create unified search view
- Query across multiple models
- Display categorized results
- Add keyboard shortcut (Ctrl+K)

---

### 2.2 Progress Calendar/Heatmap
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 3 - Good |
| Priority Score | **2.0** |

**Current State:** DailyActivity model exists but not visualized
**Solution:** GitHub-style contribution heatmap on profile/stats page

**Implementation:**
- Query last 365 days of DailyActivity
- Render as SVG/CSS grid heatmap
- Color intensity based on activity level
- Tooltip with day details on hover

---

### 2.3 Quiz Explanations
| Aspect | Rating |
|--------|--------|
| Difficulty | 1 - Very Easy |
| Effectiveness | 3 - Good |
| Priority Score | **2.5** |

**Current State:** Quiz shows correct/incorrect but no explanation why
**Solution:** Add explanation field to Answer model, show on results

**Implementation:**
- Add `explanation` TextField to Answer model
- Update quiz result template to show explanations
- Update admin form to allow entering explanations

---

### 2.4 Streak Freeze
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 3 - Good |
| Priority Score | **2.0** |

**Current State:** Miss one day = streak lost completely
**Solution:** Allow users to "freeze" streak (1-2 per month)

**Implementation:**
- Add `freeze_count` and `freeze_used_this_month` to UserStreak
- UI to activate freeze
- Modify streak break logic to check freeze status
- Monthly reset of freeze count

---

### 2.5 Bookmark Videos
| Aspect | Rating |
|--------|--------|
| Difficulty | 1 - Very Easy |
| Effectiveness | 2 - Moderate |
| Priority Score | **1.5** |

**Current State:** Can save lessons but not videos
**Solution:** Create SavedVideo model (copy SavedLesson pattern)

**Implementation:**
- Create SavedVideo model
- Add save button to video_detail.html
- Create saved_videos view
- Link from user profile

---

### 2.6 Loading States & Skeleton Loaders
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 2 - Moderate |
| Priority Score | **1.0** |

**Current State:** Page shows nothing while loading
**Solution:** Add skeleton loaders for cards, loading spinners for actions

**Implementation:**
- Create CSS skeleton animations
- Add skeleton HTML in templates
- JavaScript to swap skeleton with content
- Loading spinner for form submissions

---

## TIER 3: LEARNING FEATURES

### 3.1 Spaced Repetition for Flashcards
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 5 - Critical |
| Priority Score | **3.5** |

**Current State:** Flashcards are random, no memory optimization
**Solution:** Implement SM-2 algorithm for optimal review scheduling

**Implementation:**
- Create VocabularyProgress model (easiness, interval, next_review)
- Implement SM-2 algorithm in Python
- Add "Easy/Medium/Hard" buttons on flashcard
- Calculate next review date
- Priority queue for due cards

**Algorithm (SM-2):**
```
easiness = max(1.3, easiness + 0.1 - (5-quality)*(0.08+(5-quality)*0.02))
if quality < 3:
    interval = 1
else:
    interval = interval * easiness
next_review = today + interval days
```

---

### 3.2 Learning Paths / Courses
| Aspect | Rating |
|--------|--------|
| Difficulty | 4 - Hard |
| Effectiveness | 5 - Critical |
| Priority Score | **3.0** |

**Current State:** Lessons are standalone, no structured curriculum
**Solution:** Create Course model grouping lessons in sequence

**Implementation:**
- Create Course model (title, description, lessons[], difficulty, duration)
- Create CourseEnrollment model (user, course, current_lesson, progress)
- Course list and detail pages
- Progress tracking through course
- Completion certificate generation

---

### 3.3 Dictionary / Quick Lookup
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 4 - High |
| Priority Score | **3.0** |

**Current State:** Must browse lessons to find specific signs
**Solution:** Dedicated dictionary page with A-Z index, search

**Implementation:**
- Create dictionary view querying all Vocabulary
- Alphabetical grouping (A, B, C sections)
- Search/filter functionality
- Category filter
- Quick link from navbar

---

### 3.4 Sign Language Recognition (AI/Camera)
| Aspect | Rating |
|--------|--------|
| Difficulty | 5 - Very Hard |
| Effectiveness | 5 - Critical |
| Priority Score | **2.5** |

**Current State:** Passive learning only, no practice verification
**Solution:** Use MediaPipe/TensorFlow.js for hand gesture recognition

**Implementation:**
- Integrate MediaPipe Hands (JavaScript)
- Train/use model for Vietnamese sign recognition
- Camera capture interface
- Real-time feedback on sign accuracy
- Practice mode with scoring

**Tech Stack:**
- MediaPipe Hands for hand landmark detection
- TensorFlow.js for gesture classification
- WebRTC for camera access
- Custom model training with sign dataset

---

### 3.5 Downloadable Content / Offline Mode
| Aspect | Rating |
|--------|--------|
| Difficulty | 4 - Hard |
| Effectiveness | 3 - Good |
| Priority Score | **1.0** |

**Current State:** Requires internet connection
**Solution:** PWA with service workers for offline access

**Implementation:**
- Create service worker for caching
- Add manifest.json for PWA
- Cache lesson content on first view
- Sync progress when back online
- Download button for specific lessons

---

## TIER 4: ENGAGEMENT & GAMIFICATION

### 4.1 Daily/Weekly Challenges
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 4 - High |
| Priority Score | **2.5** |

**Current State:** No short-term goals beyond streaks
**Solution:** Daily challenges (complete 3 lessons) with bonus XP

**Implementation:**
- Create Challenge model (type, requirement, reward, expires_at)
- Create UserChallenge model (user, challenge, progress, completed)
- Daily challenge generation (cron job or on-login)
- Challenge widget on dashboard
- Bonus XP on completion

**Challenge Types:**
- Complete X lessons today
- Pass a quiz with 100%
- Review X flashcards
- Watch X videos
- Post in forum

---

### 4.2 Friends & Social Features
| Aspect | Rating |
|--------|--------|
| Difficulty | 4 - Hard |
| Effectiveness | 4 - High |
| Priority Score | **2.0** |

**Current State:** Users are isolated, no social connections
**Solution:** Follow system, friend leaderboard, activity feed

**Implementation:**
- Create Follow model (follower, following)
- Friends-only leaderboard tab
- Activity feed (X completed a lesson, Y earned a badge)
- Share achievements to social media
- Profile visibility settings

---

### 4.3 Animated Badges & Showcase
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 2 - Moderate |
| Priority Score | **1.0** |

**Current State:** Static badge display
**Solution:** CSS animations, badge showcase on profile

**Implementation:**
- Add CSS animations (shine, pulse) to badge icons
- Create badge showcase component for profile
- "Featured badges" selection by user
- Badge unlock animation/notification

---

### 4.4 Achievement Sharing
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 2 - Moderate |
| Priority Score | **1.0** |

**Current State:** No way to share achievements
**Solution:** Social media share buttons, shareable achievement images

**Implementation:**
- Add share buttons (Facebook, Twitter)
- Generate OG images for achievements
- Share URL with preview card
- Track shares for analytics

---

## TIER 5: TECHNICAL IMPROVEMENTS

### 5.1 REST API with Django REST Framework
| Aspect | Rating |
|--------|--------|
| Difficulty | 4 - Hard |
| Effectiveness | 4 - High |
| Priority Score | **2.0** |

**Current State:** Limited API (2 endpoints), web-only
**Solution:** Full REST API for mobile app potential

**Implementation:**
- Install Django REST Framework
- Create serializers for all models
- Build API viewsets with authentication
- Add token/JWT authentication
- API documentation (Swagger/OpenAPI)

**Endpoints Needed:**
- Auth: /api/auth/login, register, logout, me
- Lessons: /api/lessons/, /api/lessons/{id}/
- Videos: /api/videos/
- Quizzes: /api/quizzes/, /api/quizzes/{id}/submit
- Progress: /api/progress/
- Gamification: /api/stats/, /api/leaderboard/

---

### 5.2 Separate CSS Files & Build System
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 3 - Good |
| Priority Score | **1.5** |

**Current State:** 1600+ lines of inline CSS in base.html
**Solution:** Extract to separate files, add build system

**Implementation:**
- Extract CSS to static/css/main.css
- Setup PostCSS or Sass
- Add CSS minification
- Consider Tailwind CSS migration
- Setup webpack/vite for bundling

---

### 5.3 Redis Caching
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 3 - Good |
| Priority Score | **2.0** |

**Current State:** Basic Django cache, limited usage
**Solution:** Redis for sessions, caching, real-time features

**Implementation:**
- Install and configure Redis
- Cache frequently accessed data (leaderboard, categories)
- Session storage in Redis
- Prepare for real-time notifications

---

### 5.4 Real-time Notifications (WebSocket)
| Aspect | Rating |
|--------|--------|
| Difficulty | 4 - Hard |
| Effectiveness | 3 - Good |
| Priority Score | **1.0** |

**Current State:** Notifications require page refresh
**Solution:** Django Channels for WebSocket notifications

**Implementation:**
- Install Django Channels
- Setup ASGI server (Daphne/Uvicorn)
- Create notification consumer
- Frontend WebSocket connection
- Real-time notification popup

---

### 5.5 Admin Analytics Dashboard
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 3 - Good |
| Priority Score | **1.5** |

**Current State:** Basic counts only
**Solution:** Charts, trends, user engagement metrics

**Implementation:**
- Add Chart.js for visualizations
- User registration trend (line chart)
- Lesson completion rates (bar chart)
- Active users (daily/weekly/monthly)
- Popular content ranking
- Quiz pass rates

---

## TIER 6: ACCESSIBILITY & MOBILE

### 6.1 Full ARIA Implementation
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 3 - Good |
| Priority Score | **2.0** |

**Current State:** Basic accessibility, incomplete ARIA
**Solution:** Full WCAG 2.1 AA compliance

**Implementation:**
- Audit with axe-core
- Add missing ARIA labels
- Ensure keyboard navigation
- Focus management for modals
- Screen reader testing

---

### 6.2 Video Captions/Subtitles
| Aspect | Rating |
|--------|--------|
| Difficulty | 3 - Medium |
| Effectiveness | 4 - High |
| Priority Score | **2.5** |

**Current State:** Videos have no captions
**Solution:** VTT subtitle support for all videos

**Implementation:**
- Add subtitle field to Video model
- VTT file upload in admin
- HTML5 video track element
- Auto-caption generation (future: AI)

---

### 6.3 High Contrast Mode
| Aspect | Rating |
|--------|--------|
| Difficulty | 2 - Easy |
| Effectiveness | 2 - Moderate |
| Priority Score | **1.0** |

**Current State:** Dark mode only
**Solution:** High contrast mode for visual impairments

**Implementation:**
- Create high-contrast CSS variables
- Toggle button in accessibility menu
- Black/white/yellow color scheme
- Larger text option

---

### 6.4 Native Mobile App
| Aspect | Rating |
|--------|--------|
| Difficulty | 5 - Very Hard |
| Effectiveness | 4 - High |
| Priority Score | **1.5** |

**Current State:** Web only, responsive design
**Solution:** React Native or Flutter app

**Implementation:**
- Requires REST API first (5.1)
- React Native / Flutter development
- Offline capability
- Push notifications
- App store deployment

---

## PRIORITY IMPLEMENTATION ORDER

Based on Priority Scores, recommended implementation order:

### Phase 1: Foundation (Week 1-2)
| # | Feature | Score | Difficulty |
|---|---------|-------|------------|
| 1 | Password Reset | 4.0 | Easy |
| 2 | Spaced Repetition | 3.5 | Medium |
| 3 | Global Search | 3.0 | Easy |
| 4 | Dictionary | 3.0 | Easy |
| 5 | Learning Paths | 3.0 | Hard |

### Phase 2: Quality (Week 3-4)
| # | Feature | Score | Difficulty |
|---|---------|-------|------------|
| 6 | Email Verification | 2.5 | Medium |
| 7 | Test Suite | 2.5 | Medium |
| 8 | Quiz Explanations | 2.5 | Very Easy |
| 9 | Daily Challenges | 2.5 | Medium |
| 10 | Video Captions | 2.5 | Medium |

### Phase 3: Enhancement (Week 5-6)
| # | Feature | Score | Difficulty |
|---|---------|-------|------------|
| 11 | AI Sign Recognition | 2.5 | Very Hard |
| 12 | Progress Calendar | 2.0 | Easy |
| 13 | Streak Freeze | 2.0 | Easy |
| 14 | REST API | 2.0 | Hard |
| 15 | Redis Caching | 2.0 | Easy |
| 16 | Friends System | 2.0 | Hard |
| 17 | ARIA Accessibility | 2.0 | Easy |

### Phase 4: Polish (Week 7-8)
| # | Feature | Score | Difficulty |
|---|---------|-------|------------|
| 18 | Bookmark Videos | 1.5 | Very Easy |
| 19 | CSS Refactoring | 1.5 | Medium |
| 20 | Admin Analytics | 1.5 | Medium |
| 21 | Mobile App | 1.5 | Very Hard |

### Phase 5: Future
| # | Feature | Score | Difficulty |
|---|---------|-------|------------|
| 22 | Loading States | 1.0 | Easy |
| 23 | Offline Mode | 1.0 | Hard |
| 24 | WebSocket Notifications | 1.0 | Hard |
| 25 | Badge Animations | 1.0 | Easy |
| 26 | Achievement Sharing | 1.0 | Easy |
| 27 | High Contrast Mode | 1.0 | Easy |

---

## COMPETITION HIGHLIGHTS (KHKT)

For the science competition, focus on these differentiating features:

### Must Have for Competition:
1. **AI Sign Recognition** - Unique, impressive, technical depth
2. **Spaced Repetition** - Scientifically-backed learning
3. **Learning Paths** - Structured curriculum
4. **Analytics Dashboard** - Data-driven insights

### Demo-Ready Features:
1. Existing gamification (points, badges, streaks)
2. Personalized recommendations
3. Community forum
4. Dark mode & responsive design

### Talking Points:
- "Cá nhân hóa học tập" (Personalized learning)
- "Thuật toán gợi ý thông minh" (Smart recommendation algorithm)
- "Hệ sinh thái học tập khép kín" (Closed learning ecosystem)
- "Ứng dụng AI nhận dạng cử chỉ" (AI gesture recognition)

---

## QUICK REFERENCE

### Highest Impact, Lowest Effort:
1. Password Reset (Score: 4.0, Difficulty: 2)
2. Global Search (Score: 3.0, Difficulty: 2)
3. Dictionary (Score: 3.0, Difficulty: 2)
4. Quiz Explanations (Score: 2.5, Difficulty: 1)

### Competition Winners (High Impact):
1. AI Sign Recognition
2. Spaced Repetition
3. Learning Paths
4. Daily Challenges

### Technical Debt to Address:
1. Test Suite
2. CSS Refactoring
3. REST API

---

*Document maintained by: Development Team*
*Next Review: After Phase 1 completion*
