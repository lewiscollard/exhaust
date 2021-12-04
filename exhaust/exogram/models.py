import secrets

from django.db import models

from exhaust.common.models import PublishedModel


class Gram(PublishedModel):
    # `public_id` will be auto-generated on save. It's a six-character random
    # string, which might be enough to prevent object enumeration, for anyone
    # but the most bored.
    public_id = models.CharField(
        max_length=6,
    )

    slug = models.SlugField(
        null=True,
        unique=False,
        help_text='Use this to optimise for search engines in the URL.',
    )

    image = models.ImageField()

    text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = secrets.token_urlsafe(6)
        return super().save(*args, **kwargs)
