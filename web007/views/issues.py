from django.shortcuts import render
from django.http import JsonResponse
from web007.forms import issue


def issues(request,project_id):
    form = issue.IssueForm(request)
    return render(request,'web007/issues.html',{'form':form})