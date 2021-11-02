from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('help', views.help_language, name="help_language")
]