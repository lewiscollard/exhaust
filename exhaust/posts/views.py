from django.conf import settings
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


class PostFeedView(PostListView):
    '''An RSS feed for all posts.

    This would, in an idea world, work with Django's feed module. But that API
    is a mess for the common use case of generating a human-readable RSS feed
    to plug in to a reader, as well as looking absolutely nothing like any of
    Django's generic views.
    '''

    template_name = 'posts/post_feed.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # allow previewing in DEBUG mode
        if settings.DEBUG and 'debug' in request.GET:
            response['Content-Type'] = 'text/plain'
        else:
            response['Content-Type'] = 'application/rss+xml'

        return response
