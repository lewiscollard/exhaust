from django.urls import path

from exhaust.exogram import views

app_name = 'exogram'

urlpatterns = [
    path('', views.GramListView.as_view(), name='gram_list'),
    path('<str>/', views.GramDetailView.as_view(), name='gram_detail'),
    path('<str>-<slug>/', views.GramDetailView.as_view(), name='gram_detail'),
]
