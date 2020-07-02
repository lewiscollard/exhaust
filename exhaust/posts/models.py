from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from markdownx.models import MarkdownxField


class PostQuerySet(models.QuerySet):
    '''
    A manager that allows some crude version of "draft" and a "post queue"
    by excluding anything with online=False or a date set to the future.
    '''

    def select_published(self):
        return self.filter(
            online=True,
            date__lte=timezone.now(),
        )


class Post(models.Model):
    '''
    A post on the site.

    The only required field here is the date. That's to allow any kind of post
    (image-only, text-only, title-only). Of course, it would not make sense to
    have a post with no title, text or image set, but that can be enforced in
    the admin.
    '''

    objects = models.Manager.from_queryset(PostQuerySet)()

    date = models.DateTimeField(
        default=timezone.now
    )

    title = models.CharField(
        max_length=280,
        null=True,
        blank=True,
    )

    # Optional slug, for nicer URLs.
    slug = models.SlugField(
        null=True,
        blank=True,
    )

    text = MarkdownxField(
        null=True,
        blank=True,
    )

    online = models.BooleanField(
        default=True,
        help_text='Uncheck this to hide this post on the frontend.'
    )

    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='post_images',
    )

    alt_text = models.CharField(
        max_length=1000,
        help_text='This is assistive text for screen readers. This is very important to fill out on image-only posts.',
        null=True,
        blank=True,
    )

    # This will only be me, but for the future who knows?! (foreveralone.png)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        if self.title:
            return self.title

        if self.text:
            if len(self.text) > 40:
                return f'{self.text[:38]}...'

        if self.image:
            return 'Image post: {self.image.file.name}'

        # Should never happen, but make pylint happy
        return '(Broken post)'

    @cached_property
    def body_template(self):
        # upgrade this later to handle various different kinds of post
        # layouts
        return 'posts/layouts/post_body.html'

    def get_absolute_url(self):
        if self.slug:
            return reverse('posts:post_detail', kwargs={'pk': self.pk, 'slug': self.slug})
        return reverse('posts:post_detail', kwargs={'pk': self.pk})
