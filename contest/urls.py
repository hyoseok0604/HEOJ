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
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('contests', views.contests, name="contests"),
    path('contest/<int:id>', views.contest, name="contest"),
    path('contest/<int:id>/problemset', views.contest_problemset, name="contest_problemset"),
    path('contest/<int:contest_id>/problem', views.contest_problem, name="contest_problem"),
    path('contest/<int:contest_id>/problem/<int:problem_id>', views.contest_problem, name="contest_problem"),
    path('contest/<int:contest_id>/submit', views.contest_submit, name="contest_submit"),
    path('contest/<int:contest_id>/submit/<int:problem_id>', views.contest_submit, name="contest_submit"),
    path('contest/<int:id>/status', views.contest_status, name="contest_status"),
    path('contest/<int:id>/status/<int:page>', views.contest_status, name="contest_status"),
    path('contest/<int:id>/mystatus', views.contest_mystatus, name="contest_mystatus"),
    path('contest/<int:id>/mystatus/<int:page>', views.contest_mystatus, name="contest_mystatus"),
    path('contest/<int:id>/scoreboard', views.contest_scoreboard, name="contest_scoreboard"),
    path('contest/<int:id>/scoreboard/<int:page>', views.contest_scoreboard, name="contest_scoreboard"),
]
