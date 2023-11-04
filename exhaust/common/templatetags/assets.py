from django import template

from ..images import render_multiformat_image

register = template.Library()


@register.simple_tag()
def render_image(image, *, width, alt_text=None):
    return render_multiformat_image(image, alt_text=alt_text, width=width)
