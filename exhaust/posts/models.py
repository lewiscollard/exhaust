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
            # Swapping out the seconds and microseconds to 0 means that the
            # same query is generated for any particular minute in the day.
            # This is much more query-caching (i.e. cachalot) friendly, in
            # both that the same query will be generated for one minute, and
            # stops the cache filling up with entries that will never get a
            # hit.
            date__lte=timezone.now().replace(second=0, microsecond=0),
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

    link = models.URLField(
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

    categories = models.ManyToManyField(
        'posts.Category',
        blank=True,
    )

    # SEO things
    seo_title = models.CharField(
        'SEO title',
        max_length=60,
        null=True,
        blank=True,
    )

    meta_description = models.TextField(
        null=True,
        blank=True,
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

    def get_title_link_url(self):
        return self.link or self.get_absolute_url()

    def get_absolute_url(self):
        if self.slug:
            return reverse('posts:post_detail', kwargs={'pk': self.pk, 'slug': self.slug})
        return reverse('posts:post_detail', kwargs={'pk': self.pk})


class Category(models.Model):
    title = models.CharField(
        max_length=20,
    )

    slug = models.SlugField()

    description = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['title']
        # avoid default rendering of "Categorys"
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:post_category_list', kwargs={'slug': self.slug})
