from django import template
from django.utils.safestring import mark_safe
import markdown
import bleach

register = template.Library()

# Allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
    'hr', 'div', 'span',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}


@register.filter(name='markdown')
def markdown_filter(value):
    """Convert markdown text to HTML with XSS protection."""
    if not value:
        return ''

    # Configure markdown with useful extensions
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',  # ```code blocks```
        'markdown.extensions.tables',        # | tables |
        'markdown.extensions.nl2br',         # newlines to <br>
        'markdown.extensions.sane_lists',    # better list handling
    ])

    # Convert markdown to HTML
    html = md.convert(value)

    # Sanitize HTML to prevent XSS attacks
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

    return mark_safe(clean_html)
