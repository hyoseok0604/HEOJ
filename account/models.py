from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.
class Profile(models.Model):
    class Language(models.IntegerChoices):
        CPP11 = 0, _('C++11')
        CPP14 = 1, _('C++14')
        CPP17 = 2, _('C++17')
        CPP20 = 3, _('C++20')
        C11 = 4, _('C11')
        C90 = 5, _('C90')
        C99 = 6, _('C99')
        PYTHON2 = 7, _('Python2')
        PYTHON3 = 8, _('Python3')
        JAVA8 = 9, _('Java 8')
        JAVA11 = 10, _('Java 11')
        
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    one_line = models.TextField(max_length=50, default="")
    default_language = models.IntegerField(choices=Language.choices, default=Language.CPP14)