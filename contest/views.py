from django.forms.models import ModelChoiceField
from contest.models import Contest
from django.utils import timezone
from django.shortcuts import render, redirect
from contest.forms import SubmitSubmissionForm
from problem.models import Submission
import string
import boto3
import json

# Create your views here.
def contests(request, page=1):
    contest_before = Contest.objects.filter(start_time__gt=timezone.now()).order_by('start_time')
    contest_running = Contest.objects.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now()).order_by('start_time')
    contest_after = Contest.objects.filter(end_time__lt=timezone.now()).order_by('-end_time')

    page_count = (Contest.objects.all().count() + 19) // 20
    
    context = {
        "contest_before": contest_before,
        "contest_running": contest_running,
        "contest_after": contest_after,
        "page_count": range(1, page_count+1),
        "current_page" : page,
    }

    return render(request, 'contest/contests.html', context)

def contest(request, id):
    contest = Contest.objects.get(pk=id)

    context = {
        "contest": contest,
    }

    return render(request, 'contest/contest.html', context)


def contest_problemset(request, id):
    contest = Contest.objects.get(pk=id)

    problemset = zip(string.ascii_uppercase, contest.problems.all())

    context = {
        "contest": contest,
        "problemset": problemset,
    }

    return render(request, 'contest/problemset.html', context)

def contest_problem(request, contest_id, problem_id=1):
    contest = Contest.objects.get(pk=contest_id)

    if problem_id < 1 or problem_id > contest.problems.count():
        return redirect('contest', contest_id)
    
    problem = contest.problems.all()[problem_id-1]

    contest_problem_title = string.ascii_uppercase[problem_id-1] + "번 " + problem.title

    context = {
        "contest": contest,
        "problem": problem,
        "examples": zip(problem.example_input, problem.example_output),
        "problem_id": problem_id,
        "contest_problem_title": contest_problem_title,
    }

    return render(request, 'contest/problem.html', context)

def contest_submit(request, contest_id, problem_id=0):
    contest = Contest.objects.get(pk=contest_id)
    problemset = contest.problems.all()

    if request.method == 'POST':
        form = SubmitSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.author = request.user
            submission.memory = None
            submission.time = None
            submission.code = request.POST['code']
            submission.contest = contest

            submission.save()

            sqs = boto3.resource('sqs')
            queue = sqs.get_queue_by_name(QueueName='heoj_judge_queue.fifo')
            queue.send_message(MessageBody=json.dumps(
                {
                    "submission_id": submission.id,
                    "code": submission.code,
                    "lang": submission.language,
                    "problem_id": submission.problem.number,
                    "time_limit": submission.problem.time_limit,
                    "memory_limit": submission.problem.memory_limit,
                }
            ), MessageGroupId='judge',)

            return redirect('contest_mystatus', id=contest_id)
    else:
        form = SubmitSubmissionForm()

    form.fields["problem"].queryset = problemset
    form.fields["problem"].empty_label = None

    context = {
        "contest": contest,
        "problemset": problemset,
        "form": form,
    }

    return render(request, 'contest/submit.html', context)

def contest_scoreboard(request, id, page=1):
    return render(request, 'contest/scoreboard.html')

def contest_status(request, id, page=1):
    contest = Contest.objects.get(pk=id)
    submissions = Submission.objects.filter(contest__exact=contest).select_related('author').order_by('-pk')[20*(page-1):20*page]
    # submissions = contest.submission_set.order_by('-pk')[20*(page-1):20*page]

    problemset = zip(string.ascii_uppercase, contest.problems.all())

    alpha_wrapper = dict()
    number_wrapper = dict()

    index = 1
    for alpha, problem in problemset:
        alpha_wrapper[problem.number] = alpha
        number_wrapper[problem.number] = index
        index = index + 1

    page_count = (Submission.objects.filter(contest__exact=contest).count() + 19) // 20

    context = {
        "contest": contest,
        "statuses": submissions,
        "page_count": range(1, page_count+1),
        "current_page": page,
        "alpha_wrapper": alpha_wrapper,
        "number_wrapper": number_wrapper,
    }

    return render(request, 'contest/status.html', context)

def contest_mystatus(request, id, page=1):
    return render(request, 'contest/my_status.html')