from django.shortcuts import render

def index(request):
    return render(request, 'web007/index.html')