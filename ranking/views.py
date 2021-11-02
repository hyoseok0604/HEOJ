from django.db.models.aggregates import Count
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from problem.models import Submission

# Create your views here.
def ranking(request, page=1):
    submissions = User.objects.annotate(
            count = Count('submission__problem__pk',
                filter=Q(submission__result__exact=Submission.Result.ACCEPTED),
                distinct=True
            )).order_by('-count')[20*(page-1):20*page]
    page_count = (User.objects.all().count() + 19) // 20
    context = {
        "rank_data": submissions,
        "page_count": range(1, page_count+1),
        "current_page" : page,
    }
    return render(request, 'ranking/ranking.html', context=context)