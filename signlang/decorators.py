"""
Custom decorators for the Sign Language Learning Platform
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def teacher_or_staff_required(view_func):
    """
    Decorator that allows access to staff members OR teachers.
    Teachers can access /manage/ but not /admin/.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')

        # Staff members always have access
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)

        # Check if user is a teacher
        try:
            profile = request.user.profile
            if profile.is_teacher:
                return view_func(request, *args, **kwargs)
        except UserProfile.DoesNotExist:
            pass

        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    return _wrapped_view
