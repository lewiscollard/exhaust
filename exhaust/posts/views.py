from django.views.generic import ListView

from .models import Post

class PostMixin:
    def get_queryset(self):
        return super().get_queryset().select_published()


class PostListView(PostMixin, ListView):
    model = Post
