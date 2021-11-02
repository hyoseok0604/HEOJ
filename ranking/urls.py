from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('ranking', views.ranking, name='ranking'),
    path('ranking/<int:page>', views.ranking, name='ranking'),
]