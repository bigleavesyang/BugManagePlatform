from django.shortcuts import render, redirect


def dashboard(request,project_id):
    return render(request,'web007/dashboard.html')



def statistics(request,project_id):
    return render(request,'web007/statistics.html')
