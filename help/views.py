from django.shortcuts import render

# Create your views here.
def help_language(request):
    return render(request, 'help/language.html')