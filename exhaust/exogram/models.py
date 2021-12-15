import secrets

from django.db import models
from django.urls import reverse

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

    text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

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