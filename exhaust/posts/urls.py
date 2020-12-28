from django.urls import path, re_path

from . import views

app_name = 'posts'

urlpatterns = [
    re_path(r'^$', views.PostListView.as_view(), name='post_list'),
    path('category/<slug:slug>/', views.PostCategoryListView.as_view(), name='post_category_list'),
    path('feed/', views.PostFeedView.as_view(), name='post_feed'),
    path('post/<int:identifier>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:identifier>/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    # Media upload stuff for the admin.
    path('image-upload/', views.ImageUploadView.as_view(), name='image_upload'),
    path('image-redirect/<int:pk>/', views.ImageRedirectView.as_view(), name='image_redirect'),
]
