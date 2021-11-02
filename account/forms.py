from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.forms.widgets import TextInput
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')

class UserForm(UserCreationForm):
    name = forms.CharField(required=True, label="이름")
    school_number = forms.CharField(
        required=True,
        widget=TextInput(attrs={'type':'number'}),
        label="학번",
        help_text="사용자 정보가 정확하지 않은 경우 계정이 삭제될 수 있습니다.")

    class Meta:
        model = User
        fields = ("username", "name", "school_number", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields["username"].label = "아이디"
        self.fields["username"].validators = [alphanumeric]
        self.fields["username"].max_length = 36
        self.fields["username"].help_text = "36자 이하 영문, 숫자만 가능합니다."

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.name = self.cleaned_data['name']
        user.school_number = self.cleaned_data['school_number']
        if commit:
            user.save()
        return user