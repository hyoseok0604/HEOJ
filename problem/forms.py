from django.contrib.postgres import fields
from problem.models import Submission
from django import forms

class SubmitSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        labels = {
            'language': "언어"
        }
        fields = ['language']
