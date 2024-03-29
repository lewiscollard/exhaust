import os
import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from markdownx.models import MarkdownxField

from exhaust.common.models import PublishedModel


class SEOModel(models.Model):
    '''
    Helper model to get SEO fields (common to posts and categories).
    '''
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
        abstract = True


class Post(PublishedModel, SEOModel):
    '''
    A post on the site.

    The only required field here is the date. That's to allow any kind of post
    (image-only, text-only, title-only). Of course, it would not make sense to
    have a post with no title, text or image set, but that can be enforced in
    the admin.
    '''

    # It is possible to not have a slug if we only have an image. I also want
    # the option to change the slug while keeping a persistent URL (see views
    # for how this works), so I want some kind of persistent identifier, and
    # PKs offend me for irrational reasons. This will be automatically
    # populated when save() is called.
    identifier = models.IntegerField()

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

    # Open Graph stuff. I don't like Facebook, but their standards for having
    # a title and description and an image are universally adopted. Roll with
    # it.
    opengraph_title = models.CharField(
        verbose_name='title',
        max_length=100,
        blank=True,
    )

    opengraph_image = models.ImageField(
        verbose_name='image',
        null=True,
        blank=True,
        upload_to='opengraph-images'
    )

    opengraph_description = models.TextField(
        verbose_name='description',
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
            return self.text

        if self.image:
            return f'Image post: {self.image.file.name}'

        # Should never happen, but make pylint happy
        return '(Broken post)'

    def save(self, *args, **kwargs):  # pylint:disable=signature-differs
        if not self.identifier:
            # probs enough for now as it's just me
            # (dear future employers: I would never write something this crappy
            # in code I write for you, promise)
            self.identifier = secrets.randbelow(2**31)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug:
            return reverse('posts:post_detail', kwargs={'identifier': self.identifier, 'slug': self.slug})
        return reverse('posts:post_detail', kwargs={'identifier': self.identifier})

    def get_title_link_url(self):
        return self.link or self.get_absolute_url()

    @cached_property
    def body_template(self):
        # upgrade this later to handle various different kinds of post
        # layouts
        return 'posts/layouts/post_body.html'

    @cached_property
    def status_text(self):
        if not self.online:
            return 'Draft'
        if self.date > timezone.now():
            return 'Scheduled'
        return 'Published'


class PostImage(models.Model):
    '''
    A model for storing a in-text image. See `ImageUploadView` in views.py;
    this isn't really useful by itself.
    '''

    image = models.ImageField()

    title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.title or self.image.file.name

    def get_absolute_url(self):
        return reverse('posts:image_redirect', kwargs={'pk': self.pk})


class Category(SEOModel):
    title = models.CharField(
        max_length=100,
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
        return reverse('posts:post_category_list', kwargs={'category': self.slug})


class Attachment(models.Model):
    # A model for "I want to do something with a file". I will use it for
    # small locally-hosted videos.

    file = models.FileField(
        upload_to='post-attachments',
    )

    timestamp = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return os.path.basename(self.file.name)
