"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('problemset/', views.problemset, name='problemset'),
    path('problemset/<int:page>', views.problemset, name='problemset'),
    path('problem/<int:id>', views.problem, name='problem'),
    path('submission/<int:id>', views.submission, name='submission'),
    path('problem/<int:id>/submit', views.submit, name='problem_submit'),
    path('problem/<int:id>/status', views.status, name='problem_status'),
    path('problem/<int:id>/status/<int:page>', views.status, name='problem_status'),
    path('problem/<int:id>/mystatus', views.my_status, name='problem_mystatus'),
    path('problem/<int:id>/mystatus/<int:page>', views.my_status, name='problem_mystatus'),
    path('problem/<int:id>/rank', views.rank, name="problem_rank"),
    path('problem/<int:id>/rank/<int:page>', views.rank, name="problem_rank"),
    # path('problem/<int:id>/rank/<int:lang>/<int:page>', views.rank, name="problem_rank"),
]
