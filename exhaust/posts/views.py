from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from .models import Post


class PostMixin:
    model = Post

    def get_queryset(self):
        return super().get_queryset().select_published()


class PostListView(PostMixin, ListView):
    pass


class PostDetailView(PostMixin, DetailView):
    def get(self, request, *args, **kwargs):
        # If the path does not match the canonical URL of the post, then
        # redirect. This handles two situations:
        #
        # 1) that we create a post, add a slug later. We could end up with
        #    two possible URLs for it, e.g. /post/42/ and /post/42-some-slug/,
        #    which we don't really want.
        #
        # 2) that some genius decides to change the second URL above to
        #    /post/42-something-unpleasant/ and it looks like we created that
        #    URL.

        obj = self.get_object()

        if not request.path == obj.get_absolute_url():
            return redirect(obj.get_absolute_url(), permanent=True)
        return super().get(request, args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_page'] = True
        return context
