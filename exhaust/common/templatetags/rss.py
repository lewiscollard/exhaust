import email

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def path_to_url(value):
    '''
    Converts a /path/ as typically returned by a get_absolute_url call
    to an actually absolute URL.
    '''

    # just in case
    if value.startswith('http://') or value.startswith('https://'):
        return value

    if settings.DEBUG:
        # Make links work in `runserver` mode.
        root = 'http://localhost:8000'
    else:
        root = f'https://{settings.SITE_DOMAIN}'

    return f'{root}{value}'


@register.filter
def format_rfc2822(value):
    '''
    Formats a date to the RFC2822 format, as used by pubDate in RSS feeds.
    '''
    return email.utils.format_datetime(value)
