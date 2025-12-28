"""
Utility functions for the Sign Language Learning Platform
"""
import re
from django.utils.text import slugify as django_slugify
from unidecode import unidecode


def safe_int(value, default=0):
    """Safely convert value to int, return default if conversion fails"""
    if value is None or value == '':
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert value to float, return default if conversion fails"""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def sanitize_string(value, max_length=None):
    """Sanitize string input - strip whitespace and limit length"""
    if value is None:
        return ''
    value = str(value).strip()
    if max_length:
        value = value[:max_length]
    return value


def validate_slug(slug):
    """Validate that a slug is properly formatted"""
    if not slug:
        return False
    # Slug should only contain lowercase letters, numbers, and hyphens
    return bool(re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug))


def generate_slug(text, max_length=50):
    """Generate a valid slug from text, handles Vietnamese and other non-ASCII characters"""
    if not text:
        return ''
    # Convert Vietnamese/non-ASCII characters to ASCII equivalents
    ascii_text = unidecode(text)
    slug = django_slugify(ascii_text)
    # Ensure we have a valid slug (not empty after conversion)
    if not slug:
        slug = 'item'
    return slug[:max_length]


def clamp(value, min_value, max_value):
    """Clamp a value between min and max"""
    return max(min_value, min(value, max_value))
