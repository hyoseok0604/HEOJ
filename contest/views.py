import operator
from django.db.models.aggregates import Count
from django.forms.models import ModelChoiceField
from contest.models import Contest
from django.utils import timezone
from django.shortcuts import render, redirect
from contest.forms import SubmitSubmissionForm
from problem.models import Submission
import string
import boto3
import json
import math

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

    before_contest = timezone.now() < contest.start_time

    context = {
        "contest": contest,
        "problemset": problemset,
        "before_contest": before_contest,
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

    before_contest = timezone.now() < contest.start_time

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

            if submission.submit_time > contest.end_time or submission.submit_time < contest.start_time:
                submission.contest = None
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
        "before_contest": before_contest,
    }

    return render(request, 'contest/submit.html', context)

class ScoreboardContestant:
    def __init__(self, username, problem_count) -> None:
        self.rank = 0
        self.username = username
        self.solved_problem_count = 0
        self.total_penalty = math.inf
        self.problems = [ScoreboardProblem() for _ in range(problem_count)]

class ScoreboardProblem:
    def __init__(self) -> None:
        self.try_count = 0
        self.penalty = 0
        self.solved = False

def contest_scoreboard(request, id, page=1):
    contest = Contest.objects.get(pk=id)

    submissions = Submission.objects.filter(contest__exact=contest)\
                            .select_related('author', 'problem').order_by('-pk').all()
    
    problems = contest.problems.all()
    problem_count = problems.count()
    problem_number_to_index = dict()
    index = 0
    for problem in problems:
        problem_number_to_index[problem.number] = index
        index += 1
    
    contestants = Submission.objects.filter(contest__exact=contest).select_related('author').distinct('author')
    contestant_count = contestants.count()
    contestant_name_to_index = dict()
    index = 0
    for contestant in contestants:
        contestant_name_to_index[contestant.author.username] = index
        index += 1
    
    # 정답 여부..
    # 패널티 계산..

    # 스코어보드 대회 참가 인원 x 대회 문제 크기의 배열
    # 시도 횟수, 패널티 정보가 필요함

    scoreboard = [ScoreboardContestant(contestant.author.username, problem_count) for contestant in contestants]

    for submission in submissions:
        contestant_index = contestant_name_to_index[submission.author.username]
        problem_index = problem_number_to_index[submission.problem.number]

        contestant_line = scoreboard[contestant_index]
        problem_cell = contestant_line.problems[problem_index]

        if submission.result == Submission.Result.ACCEPTED:
            if not problem_cell.solved:
                problem_cell.try_count += 1 # 제출 횟수 1 증가
                problem_cell.penalty += (submission.submit_time - contest.start_time).total_seconds() // 60 # 정답 코드의 패널티 계산
                problem_cell.solved = True # 더이상의 패널티를 계산하지 않도록

                if contestant_line.total_penalty == math.inf:
                    contestant_line.total_penalty = 0

                contestant_line.solved_problem_count += 1
                contestant_line.total_penalty += problem_cell.penalty
        elif submission.result == Submission.Result.QUEUED or \
            submission.result == Submission.Result.RUNNING: # 해당 결과를 가진 제출들은 무시
            pass
        else:
            if not problem_cell.solved:
                problem_cell.try_count += 1 # 제출 횟수 1 증가
                problem_cell.penalty += 10 # 제출 패널티 = 10분

    # 해결한 문제 내림차순 - 패널티 오름차순 으로 정렬
    scoreboard.sort(key=operator.attrgetter('total_penalty'))
    scoreboard.sort(key=operator.attrgetter('solved_problem_count'), reverse=True)

    if len(scoreboard) > 0:
        scoreboard[0].rank = 1
    
    for index in range(1, contestant_count):
        before = scoreboard[index-1]
        now = scoreboard[index]
        if before.total_penalty == now.total_penalty and before.solved_problem_count == now.solved_problem_count:
            scoreboard[index].rank = before.rank
        else:
            scoreboard[index].rank = index + 1

    context = {
        "contest": contest,
        "scoreboard": scoreboard,
        "alphastr": string.ascii_uppercase[:problem_count],
    }

    return render(request, 'contest/scoreboard.html', context)

def contest_status(request, id, page=1):
    contest = Contest.objects.get(pk=id)
    submissions = Submission.objects.filter(contest__exact=contest).select_related('author', 'problem').order_by('-pk')[20*(page-1):20*page]
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
    contest = Contest.objects.get(pk=id)
    submissions = Submission.objects.filter(contest=contest, author=request.user).select_related('author', 'problem').order_by('-pk')[20*(page-1):20*page]
    # submissions = contest.submission_set.order_by('-pk')[20*(page-1):20*page]

    problemset = zip(string.ascii_uppercase, contest.problems.all())

    alpha_wrapper = dict()
    number_wrapper = dict()

    index = 1
    for alpha, problem in problemset:
        alpha_wrapper[problem.number] = alpha
        number_wrapper[problem.number] = index
        index = index + 1

    page_count = (Submission.objects.filter(contest=contest, author=request.user).count() + 19) // 20

    context = {
        "contest": contest,
        "statuses": submissions,
        "page_count": range(1, page_count+1),
        "current_page": page,
        "alpha_wrapper": alpha_wrapper,
        "number_wrapper": number_wrapper,
    }
    
    return render(request, 'contest/my_status.html', context)