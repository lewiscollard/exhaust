from django import template
from sorl.thumbnail import get_thumbnail

register = template.Library()


@register.inclusion_tag('assets/image.html', takes_context=True)
def render_image(context, image, alt_text=None, max_width=None):
    context.update({
        'image': image,
        'alt_text': alt_text,
    })
    context['image'] = image
    context['alt_text'] = alt_text or ''
    context['aspect_padding'] = round(image.height / image.width, 6) * 100

    # Stick a bunch of image widths into the context, in both webp and
    # the original format.
    widths = [320, 480, 768, 1024, 1280, 1920]

    context['sources'] = {'image/webp': [], 'image/jpeg': []}

    for width in widths:
        context['sources']['image/webp'].append({
            'width': width,
            'url': get_thumbnail(image.file, str(width), format='WEBP').url
        })

        context['sources']['image/jpeg'].append({
            'width': width,
            'url': get_thumbnail(image.file, str(width), format='JPEG').url
        })
    return context
