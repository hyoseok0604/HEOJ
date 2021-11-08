from django.db.models.expressions import OuterRef, Subquery
from problem import urls
from django.contrib.auth.models import User
from .forms import SubmitSubmissionForm
from .models import Problem, Submission
from django.shortcuts import render, redirect
from django.http import HttpResponse
import boto3
import json

# Create your views here.
def problemset(request, page=1):
    problems = Problem.objects.order_by('-number')[20*(page-1):20*page]
    page_count = (Problem.objects.all().count() + 19) // 20
    context = {
        "problems": problems,
        "page_count": range(1, page_count+1),
        "current_page" : page,
    }
    return render(request, 'problem/problemset.html', context)

def problem(request, id):
    problem = Problem.objects.get(number=id)

    context = {
        "problem": problem,
        "examples": zip(problem.example_input, problem.example_output),
    }
    return render(request, 'problem/problem.html', context)

def submission(request, id):
    submission = Submission.objects.get(pk=id)
    return render(request, 'submission/submission.html', {"submission": submission})

def submit(request, id):
    problem = Problem.objects.get(number=id)
    if request.method == 'POST':
        form = SubmitSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.author = request.user
            submission.problem = problem
            submission.memory = None
            submission.time = None
            submission.code = request.POST['code']

            submission.save()

            sqs = boto3.resource('sqs')
            queue = sqs.get_queue_by_name(QueueName='heoj_judge_queue.fifo')
            queue.send_message(MessageBody=json.dumps(
                {
                    "submission_id": submission.id,
                    "code": submission.code,
                    "lang": submission.language,
                    "problem_id": id,
                    "time_limit": problem.time_limit,
                    "memory_limit": problem.memory_limit,
                }), MessageGroupId='judge',)

            return redirect('problem_mystatus', id=id)
    else:
        form = SubmitSubmissionForm()
    context = {
        "problem": problem,
        "form": form,
    }
    return render(request, 'problem/submit.html', context)

def rank(request, id, lang=-1, page=1):
    problem = Problem.objects.get(number=id)
    best_submission_per_user = problem.submission_set.filter(
        result__exact=Submission.Result.ACCEPTED,
        author=OuterRef('author')
    ).order_by('time', 'memory', 'submit_time')[:1]
    statuses = problem.submission_set.filter(
        pk__in=Subquery(best_submission_per_user.values('pk'))
    ).order_by('time', 'memory', 'submit_time')[20*(page-1):20*page]

    page_count = (statuses.count() + 19) // 20

    context = {
        "problem": problem,
        "statuses": statuses,
        "page": page,
        "lang": lang,
        "page_count": range(1, page_count+1),
        "current_page": page,
    }
    return render(request, 'problem/rank.html', context)

def status(request, id, page=1):
    problem = Problem.objects.get(number=id)
    statuses = problem.submission_set.select_related('author').order_by('-pk')[20*(page-1):20*page]
    page_count = (problem.submission_set.count() + 19) // 20
    context = {
        "problem": problem,
        "statuses": statuses,
        "page_count": range(1, page_count+1),
        "current_page": page,
    }
    return render(request, 'problem/status.html', context)

def my_status(request, id, page=1):
    problem = Problem.objects.get(number=id)
    submission_set = problem.submission_set
    statuses = submission_set.filter(author=request.user).order_by('-pk')[20*(page-1):20*page]
    page_count = (submission_set.filter(author=request.user).count() + 19) // 20
    context = {
        "problem": problem,
        "statuses": statuses,
        "page_count": range(1, page_count+1),
        "current_page": page,
    }
    return render(request, 'problem/my_status.html', context)
