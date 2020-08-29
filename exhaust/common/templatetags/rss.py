import email

from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

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


@register.simple_tag
def rss_post_body(post):
    '''
    Outputs the body of a post, rewriting the HTML to be more suitable for an
    RSS feed.

    It will convert any relative image links to absolute ones, e.g.
    `/media/uploads/something.jpg' will be rewritten to
    'https://exhaust.lewiscollard.com/media/uploads/something.jpg'. Note that
    we don't have to do this with the <source srcset...> as output by the
    multi-format image renderer, as these are already made absolute in the
    template.

    Very site-specifically, it will also remove `.image__padder`, as there
    will be no CSS to force the images within it to be absolute.
    '''
    def is_relative(path):
        return path.startswith('/') and not path.startswith('//')

    rendered = render_to_string('posts/post_rss_item.html', {'object': post})
    soup = BeautifulSoup(rendered, 'html.parser')

    # Simple attribute replacements - convert to absolute URLs where
    # appropriate.
    check_these = [('img', 'src'), ('source', 'src'), ('iframe', 'src'), ('a', 'href')]
    for tag, attribute in check_these:
        for element in soup.find_all(tag):
            if element.has_attr(attribute) and is_relative(element[attribute]):
                element[attribute] = path_to_url(element[attribute])

    # These serve no purpose in an unstyled world.
    for element in soup.find_all(attrs={'class': 'image__padder'}):
        element.extract()

    # W3C validator thinks 'max-width' on '.image' is 'potentially dangerous'.
    # It's probs not, but the max-width is only useful with our CSS, so make
    # W3C happy.
    for element in soup.find_all(attrs={'class': 'image'}):
        element['style'] = ''
    return mark_safe(str(soup))  # nosec


@register.filter
def format_rfc2822(value):
    '''
    Formats a date to the RFC2822 format, as used by pubDate in RSS feeds.
    '''
    return email.utils.format_datetime(value)
