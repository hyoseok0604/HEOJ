from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from account.models import Profile
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
    profile = Profile.objects.get(user__username=username)

    context = {
        "profile": profile,
    }

    return render(request, "account/profile.html", context)
