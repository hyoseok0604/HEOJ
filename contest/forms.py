from django.contrib.postgres import fields
from problem.models import Submission
from django import forms
from django.forms import widgets
from problem.models import Problem

class ContestProblemSelectWidget(widgets.Select):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        return super().create_option(name, value, chr(index + ord('A')) + ' - ' + label, selected, index, subindex=subindex, attrs=attrs)

class SubmitSubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        labels = {
            'language': "언어",
            'problem': "문제",
        }
        fields = ['problem', 'language']
        widgets = {
            'problem': ContestProblemSelectWidget
        }

    def __init__(self, *args, **kwargs) -> None:
        super(SubmitSubmissionForm, self).__init__(*args, **kwargs)

        self.fields['problem'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return obj.title
