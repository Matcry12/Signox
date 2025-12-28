from django import template
import re

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def youtube_embed(url):
    """
    Convert various YouTube URL formats to embed URL.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID (already embed format)
    - https://youtube.com/watch?v=VIDEO_ID
    """
    if not url:
        return ''

    url = str(url).strip()

    # Already embed format
    if '/embed/' in url:
        return url

    video_id = None

    # Match youtu.be/VIDEO_ID
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if match:
        video_id = match.group(1)

    # Match youtube.com/watch?v=VIDEO_ID
    if not video_id:
        match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)

    # Match youtube.com/v/VIDEO_ID
    if not video_id:
        match = re.search(r'youtube\.com/v/([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)

    if video_id:
        return f'https://www.youtube.com/embed/{video_id}'

    # Return original if not a recognized YouTube URL
    return url
