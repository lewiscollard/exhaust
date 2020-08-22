from django import template
from django.utils.safestring import mark_safe

from ...posts.markdown import markdown_to_html

register = template.Library()


@register.filter
def markdown(value):
    return mark_safe(markdown_to_html(value))
