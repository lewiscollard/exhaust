import commonmark
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def markdown(value):
    return mark_safe(commonmark.commonmark(value))
