from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^$', views.PostListView.as_view(), name='post_list'),
    path('category/<slug:slug>/', views.PostCategoryListView.as_view(), name='post_category_list'),
    path('feed/', views.PostFeedView.as_view(), name='post_feed'),
    path('post/<int:identifier>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>-<int:identifier>/', views.PostDetailView.as_view(), name='post_detail'),
]
