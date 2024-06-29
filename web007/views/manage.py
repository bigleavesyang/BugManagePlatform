from django.shortcuts import render, redirect


def dashboard(request,project_id):
    return render(request,'web007/dashboard.html')


def issues(request,project_id):
    return render(request,'web007/issues.html')


def setting(request,project_id):
    return render(request,'web007/setting.html')


def wiki(request,project_id):
    return render(request,'web007/wiki.html')


def file(request,project_id):
    return render(request,'web007/file.html')


def statistics(request,project_id):
    return render(request,'web007/statistics.html')
