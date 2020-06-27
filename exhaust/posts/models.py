from django.conf import settings
from django.db import models
from django.utils import timezone


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

    text = models.TextField(
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
            if len(self.text) > 20:
                return f'{self.text[:18]}...'

        if self.image:
            return 'Image post: {self.image.file.name}'
