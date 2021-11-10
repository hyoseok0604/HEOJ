import math
from django.template.defaulttags import register
from problem.models import Submission

@register.filter
def result_color(value):
    if value == Submission.Result.ACCEPTED:
        return 'text-success'
    elif value == Submission.Result.QUEUED:
        return' text-warning'
    else:
        return 'text-danger'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def check_inf(value):
    return value != math.inf