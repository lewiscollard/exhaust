from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView, ListView

from exhaust.common.views import PublishedModelViewMixin
from exhaust.exogram.models import Gram


class GramMixin(PublishedModelViewMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class GramListView(GramMixin, ListView):
    model = Gram


class GramDetailView(GramMixin, DetailView):
    model = Gram
