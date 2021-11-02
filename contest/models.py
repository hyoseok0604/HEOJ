from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Contest(models.Model):
    title = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    participants = models.ManyToManyField(User, blank=True)
    problems = models.ManyToManyField("problem.Problem", blank=True)
