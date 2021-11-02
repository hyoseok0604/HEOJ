from django.forms.models import ModelChoiceField
from contest.models import Contest
from django.utils import timezone
from django.shortcuts import render, redirect
from contest.forms import SubmitSubmissionForm
import string
import boto3
import json

# Create your views here.
def contests(request):
    contest_before = Contest.objects.filter(start_time__gt=timezone.now()).order_by('start_time')
    contest_running = Contest.objects.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now()).order_by('start_time')
    contest_after = Contest.objects.filter(end_time__lt=timezone.now()).order_by('-end_time')
    
    context = {
        "contest_before": contest_before,
        "contest_running": contest_running,
        "contest_after": contest_after,
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

def contest_problem(request, contest_id, problem_id=0):
    contest = Contest.objects.get(pk=contest_id)
    problem = contest.problems.all()[problem_id-1]

    context = {
        "contest": contest,
        "problem": problem,
        "examples": zip(problem.example_input, problem.example_output),
        "problem_id": problem_id
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

            queue.send_message(MessageBody=json.dumps({"id": submission.pk, "code": submission.code}), MessageGroupId='judge',)

            return redirect('contest/mystatus', id=contest_id)
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
    return render(request, 'contest/status.html')

def contest_mystatus(request, id, page=1):
    
    return render(request, 'contest/my_status.html')