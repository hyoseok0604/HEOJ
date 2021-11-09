from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def loader_key(request):
    return render(request, 'loader_key.html')