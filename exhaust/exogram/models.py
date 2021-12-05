import secrets
from datetime import datetime

from django.db import models
from django.urls import reverse
from markdownx.models import MarkdownxField

from exhaust.common.models import PublishedModel


class Gram(PublishedModel):
    # `public_id` will be auto-generated on save. It's a six-character random
    # string, which might be enough to prevent object enumeration, for anyone
    # but the most bored.
    public_id = models.CharField(
        max_length=8,
    )

    slug = models.SlugField(
        blank=True,
        unique=False,
        help_text='Use this to optimise the URL for search engines.',
    )

    image = models.ImageField()

    text = MarkdownxField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        parts = [datetime.strftime(self.date, '%Y-%m-%d')]

        if self.text:
            if len(self.text) > 40:
                parts.append(self.text[:40] + '...')
            else:
                parts.append(self.text)

        return ': '.join(parts)

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = secrets.token_urlsafe(6)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug:
            return reverse(
                'exogram:gram_detail',
                kwargs={'public_id': self.id, 'slug': self.slug}
            )
        return reverse('exogram:gram_detail', kwargs={'public_id': self.public_id})

    def detail_pagination(self):
        pagination = {}
        for key, attribute in [('newer', 'get_next_by_date'), ('older', 'get_previous_by_date')]:
            try:
                pagination[key] = getattr(self, attribute)().get_absolute_url()
            except self.DoesNotExist:
                pass
        return pagination
