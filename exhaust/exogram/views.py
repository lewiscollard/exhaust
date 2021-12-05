from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.views.generic import DetailView, ListView

from exhaust.common.views import PublishedModelViewMixin
from exhaust.exogram.models import Gram


class GramMixin(PublishedModelViewMixin, UserPassesTestMixin):
    def test_func(self):
        # gate this on the user being me, for now
        return self.request.user.is_superuser


class GramListView(GramMixin, ListView):
    model = Gram


class GramDetailView(GramMixin, DetailView):
    model = Gram

    def get_object(self, queryset=None):
        # Re-implementation of the Django default get_object, which cannot
        # handle two arguments when one of the arguments is not `pk`.
        try:
            return self.get_queryset().get(public_id=self.kwargs['public_id'])
        except self.model.DoesNotExist:
            raise Http404(f'{self.model._meta.verbose_name.capitalize()} not found.')  # pylint:disable=raise-missing-from
