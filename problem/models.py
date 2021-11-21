from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.fields.related import ForeignKey
from django.utils.translation import gettext as _

# Create your models here.'
class Problem(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    
    example_input = ArrayField(base_field=models.TextField(blank=True))
    example_output = ArrayField(base_field=models.TextField(blank=True))
    
    input_description = models.TextField(null=True, blank=True)
    output_description = models.TextField(null=True, blank=True)
    limit_description = models.TextField(null=True, blank=True)
    
    author = ForeignKey(User, on_delete=models.SET_NULL, null=True)

    accepted = models.IntegerField(default=0)
    wrong_answer = models.IntegerField(default=0)
    compilation_error = models.IntegerField(default=0)
    runtime_error = models.IntegerField(default=0)
    time_limit_exceeded = models.IntegerField(default=0)
    memory_limit_exceeded = models.IntegerField(default=0)
    unknown_error = models.IntegerField(default=0)

    is_public = models.BooleanField()
    visible = models.BooleanField()

    class Meta:
        ordering = ['pk']

class Submission(models.Model):
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
        PYPY2 = 11, _('PyPy2')
        PYPY3 = 12, _('PyPy3')
        CSHARP = 13, _('C# (임시)')
        NODEJS = 14, _('node.js (임시)')

    class Result(models.IntegerChoices):
        QUEUED = 0, _('채점 준비 중')
        RUNNING = 1, _('채점 중')
        ACCEPTED = 2, _('맞았습니다')
        WRONG_ANSWER = 3, _('틀렸습니다')
        COMPILATION_ERROR = 4, _('컴파일 에러')
        RUNTIME_ERROR = 5, _('런타임 에러')
        TIME_LIMIT_EXCEEDED = 6, _('시간 초과')
        MEMORY_LIMIT_EXCEEDED = 7, _('메모리 초과')
        UNKNOWN_ERROR = 8, _('알 수 없는 오류')

    author = ForeignKey(User, on_delete=models.CASCADE)
    problem = ForeignKey("problem.Problem", on_delete=models.CASCADE)
    contest = ForeignKey("contest.Contest", on_delete=models.CASCADE, null=True, default=None, blank=True)
    code = models.CharField(max_length=65535)
    language = models.IntegerField(choices=Language.choices, default=Language.CPP14)
    memory = models.IntegerField(null=True, default=None, blank=True)
    time = models.IntegerField(null=True, default=None, blank=True)
    submit_time = models.DateTimeField(auto_now=True)
    result = models.IntegerField(choices=Result.choices, default=Result.QUEUED)
