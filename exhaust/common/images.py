import hashlib

from django.core.cache import cache
from django.template.loader import render_to_string
from sorl.thumbnail import get_thumbnail


def render_multiformat_image(image, *, width, alt_text=None, title=None):
    # Grab it from the cache if we possibly can. Hash the filename (the file
    # itself never changes) and every parameter we are given so we can't
    # return the same thing for a different invocation.
    cache_hash = hashlib.sha256(image.file.name.encode('utf8'))
    cache_hash.update((alt_text or '').encode('utf8'))
    cache_hash.update((title or '').encode('utf8'))
    cache_hash.update(str(width).encode('utf8'))
    cache_key = f'multiformat_image_{cache_hash.hexdigest()[:6]}'
    cached_version = cache.get(cache_key)
    if cached_version:
        # CANARY: if this branch ends up uncovered, it means the test in
        # test_render_multiformat_image_cache_branch is broken
        return cached_version

    context = {}
    context.update({
        'image': image,
        'alt_text': alt_text,
        'title': title,
    })
    context['image'] = image
    context['alt_text'] = alt_text or ''
    context['aspect'] = f'{image.width} / {image.height}'

    # Don't upscale an image.
    real_width = min(width, image.width)
    context['sources'] = []
    for fmt, mime_type in [('WEBP', 'image/webp'), ('JPEG', 'image/jpeg')]:
        thumbnail = get_thumbnail(image.file, str(real_width), format=fmt)
        context['sources'].append({
            'mime_type': mime_type,
            'url': thumbnail.url,
            'width': thumbnail.width,
        })

    # This is necessary because at least one RSS reader (The Old Reader, which
    # I use) strips out picture/source tags.
    context['fallback_image_url'] = context['sources'][0]['url']
    # So we can add a link to the original!
    context['original'] = image

    rendered = render_to_string('assets/image.html', context)
    cache.set(cache_key, rendered)
    return rendered
