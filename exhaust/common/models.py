from django.db import models
from django.utils import timezone


class PublishedModelQuerySet(models.QuerySet):
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


class PublishedModel(models.Model):
    objects = models.Manager.from_queryset(PublishedModelQuerySet)()

    date = models.DateTimeField(
        default=timezone.now
    )

    online = models.BooleanField(
        default=False,
        help_text='Uncheck this to hide this post on the frontend.'
    )

    class Meta:
        abstract = True
