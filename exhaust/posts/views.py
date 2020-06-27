from django.views.generic import DetailView, ListView

from .models import Post

class PostMixin:
    model = Post
    def get_queryset(self):
        return super().get_queryset().select_published()


class PostListView(PostMixin, ListView):
    pass


class PostDetailView(PostMixin, DetailView):
    pass
