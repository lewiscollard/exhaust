from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^$', views.PostListView.as_view(), name='post_list'),
    path('feed/', views.PostFeedView.as_view(), name='post_feed'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>-<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
]
