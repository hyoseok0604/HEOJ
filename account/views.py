from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count

from account.models import Profile
from problem.models import Submission
from .forms import UserForm
from django.shortcuts import render, redirect

# Create your views here.
def register_request(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile(user=user)
            profile.save()
            login(request, user)
            return redirect("/")
        return render(request=request, template_name="account/register.html", context={"register_form":form})
    form = UserForm()
    return render(request=request, template_name="account/register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
        return render(request=request, template_name="account/login.html", context={"login_form":form})
    form = AuthenticationForm()
    return render(request=request, template_name="account/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	return redirect("/")

def profile(request, username):
    profile = Profile.objects.get(user__username=username).select_related("user")

    # 제출 결과별 통계
    result_queryset = profile.user.submission_set.values('result').annotate(Count('result'))
    result_labels = Submission.Result.labels
    result_counts = [0 for _ in range(result_labels)]
    for result_query in result_queryset:
        result_counts[result_query['result']] = result_query['result__count']

    # 제출 언어별 통계
    language_queryset = profile.user.submission_set.values('language').annotate(Count('language'))
    language_labels = Submission.Language.labels
    language_counts = [0 for _ in range(language_labels)]
    for language_query in language_queryset:
        language_counts[language_query['language']] = language_query['language__count']

    # 제출 언어별 결과 통계
    language_result_queryset = profile.user.submission_set.values('language', 'result').annotate(Count('language', 'result')) # 언어별 결과 통계

    context = {
        "profile": profile,
        "result_labels": result_labels[2:],
        "result_counts": result_counts[2:],
        "language_counts": 

    }

    return render(request, "account/profile.html", context)
