from django.conf.urls import url
from django.urls import path

from .views import PostDetailView, PostListView

app_name = 'posts'

urlpatterns = [
    url(r'^$', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
]
