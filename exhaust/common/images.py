import hashlib

from django.core.cache import cache
from django.template.loader import render_to_string
from sorl.thumbnail import get_thumbnail


def render_multiformat_image(image, alt_text=None, max_width=None):
    # Grab it from the cache if we possibly can. Hash the filename (the file
    # itself never changes) and every parameter we are given so we can't
    # return the same thing for a different invocation.
    cache_hash = hashlib.sha256(image.file.name.encode('utf8'))
    cache_hash.update((alt_text or '').encode('utf8'))
    cache_hash.update(str(max_width).encode('utf8'))
    cache_key = f'multiformat_image_{cache_hash.hexdigest()[:6]}'
    cached_version = cache.get(cache_key)
    if cached_version:
        return cached_version

    context = {}
    context.update({
        'image': image,
        'alt_text': alt_text,
    })
    context['original_width'] = image.width
    context['image'] = image
    context['alt_text'] = alt_text or ''
    context['aspect_padding'] = round(image.height / image.width, 6) * 100

    # Stick a bunch of image widths into the context, in both webp and
    # the original format.
    widths = [320, 480, 768, 1024, 1280, 1920]

    context['sources'] = {'image/webp': [], 'image/jpeg': []}

    for width in widths:
        if max_width is not None and width > max_width:
            continue
        context['sources']['image/webp'].append({
            'width': width,
            'url': get_thumbnail(image.file, str(width), format='WEBP').url
        })

        context['sources']['image/jpeg'].append({
            'width': width,
            'url': get_thumbnail(image.file, str(width), format='JPEG').url
        })

    rendered = render_to_string('assets/image.html', context)
    cache.set(cache_key, rendered)
    return rendered
