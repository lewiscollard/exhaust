from django.conf.urls import url
from django.urls import path

from .views import PostListView

app_name = 'posts'

urlpatterns = [
    url(r'^$', PostListView.as_view(), name='post_list'),
]
