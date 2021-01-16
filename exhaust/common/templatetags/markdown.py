from django import template
from django.utils.safestring import mark_safe

from ..markdown import markdown_to_html

register = template.Library()


@register.filter
def markdown(value):
    # Mark_safe is fine here - it's filtered through Bleach which takes care
    # of removing anything malicious
    return mark_safe(markdown_to_html(value))
