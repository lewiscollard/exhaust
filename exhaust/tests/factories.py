import os
from datetime import timedelta

import factory
from django.contrib.auth import get_user_model
from django.core.files.base import File
from django.utils.timezone import now
from factory.django import DjangoModelFactory

from exhaust.exogram.models import Gram
from exhaust.posts.models import Attachment, Category, Post, PostImage


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user{n}')

    class Meta:
        model = get_user_model()


class AttachmentFactory(DjangoModelFactory):
    class Meta:
        model = Attachment

    @factory.post_generation
    def file(obj, create, extracted, **kwargs):
        attachment_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', extracted))
        with open(attachment_path, mode='rb') as fd:
            obj.file.save('small-image.jpg', File(fd, name=extracted))  # pylint:disable=no-member


class GramFactory(DjangoModelFactory):
    date = factory.LazyFunction(lambda: now() - timedelta(minutes=1))

    class Meta:
        model = Gram

    @factory.post_generation
    def image(obj, create, extracted, **kwargs):
        attachment_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', extracted))
        with open(attachment_path, mode='rb') as fd:
            obj.image.save(extracted, File(fd, name=extracted))  # pylint:disable=no-member


class PostFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Test post {n}')
    slug = factory.Sequence(lambda n: f'test-post-{n}')
    author = factory.SubFactory(UserFactory)
    # It's necessary to set the date to something a little less than the
    # current time because select_published zeroes out the second and the
    # microsecond.
    date = factory.LazyFunction(lambda: now() - timedelta(minutes=1))
    # Force online/offline to be specified explicitly, otherwise we could get
    # misleading test results because of queryset exclusion on everything in
    # `posts.views`.
    online = None

    class Meta:
        model = Post

    @factory.post_generation
    def image(obj, create, extracted, **kwargs):
        if extracted is None:
            return
        attachment_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', extracted))
        with open(attachment_path, mode='rb') as fd:
            obj.image.save('small-image.jpg', File(fd, name=extracted))  # pylint:disable=no-member

    @factory.post_generation
    def categories(obj: Post, create, extracted, **kwargs):
        if extracted is None:
            return
        obj.categories.set(extracted)  # pylint:disable=no-member


class PostImageFactory(DjangoModelFactory):
    @factory.post_generation
    def image(obj, create, extracted, **kwargs):
        attachment_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', extracted))
        with open(attachment_path, mode='rb') as fd:
            obj.image.save('small-image.jpg', File(fd, name=extracted))  # pylint:disable=no-member

    class Meta:
        model = PostImage


class CategoryFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'Test category {n}')
    slug = factory.Sequence(lambda n: f'test-category{n}')

    class Meta:
        model = Category
