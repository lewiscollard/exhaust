from django import template
from django.utils.safestring import mark_safe

from ..markdown import markdown_to_html

register = template.Library()


@register.filter
def markdown(value):
    # mark_safe is fine because I'm not going to introduce an XSS on myself
    # in my posts
    return mark_safe(markdown_to_html(value))  # nosec
