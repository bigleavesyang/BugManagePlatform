from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from web007 import models
from datetime import datetime, timedelta
import time
import collections


def dashboard(request, project_id):
    # 获取项目下的所有问题的状态，然后统计返回给前端
    issues_type_dict = {}
    for key, value in models.Issue.status_choices:
        issues_type_dict[key] = {'text': value, 'count': 0}
    # 关于项目的问题状态的统计，聚合查询,统计这个id下的status状态，然后统计数量
    issues_status_count = models.Issue.objects.filter(project=request.tracer.project).values('status').annotate(
        ct=Count('id'))
    """
    数据格式是这样的
    [
    {'status': 'Open', 'ct': 3},
    {'status': 'Closed', 'ct': 2},
    {'status': 'InProgress', 'ct': 1},
    ]
    """
    for issue_status in issues_status_count:
        issues_type_dict[issue_status['status']]['count'] = issue_status['ct']

    # 获取当前项目的所有参与者
    """
    [
    {'collaborator_id': 1, 'collaborator__username': 'alice'},
    {'collaborator_id': 2, 'collaborator__username': 'bob'},
    ]
    """
    collaborators = models.ProjectCollaborator.objects.filter(project=request.tracer.project).values(
        'collaborator_id', 'collaborator__username')

    # 当前项目的最近十个问题,列表的剪切
    last_seven_issues = models.Issue.objects.filter(project=request.tracer.project).order_by('-create_time')[:7]
    context = {
        'status_dict': issues_type_dict,
        'user_list': collaborators,
        'top_ten_object': last_seven_issues
    }
    return render(request, 'web007/dashboard.html', context)


# 返回一个数据表，用于展示最近30天的每日问题个数，格式是前端需求的格式。
def issues_chart(request, project_id):
    # 获取最近30天的这个项目的每日问题个数数据
    today = datetime.now().date()
    date_dict = collections.OrderedDict()  # 创建一个有序字典，key是日期，value是时间戳和0的列表
    for i in range(30):
        date = today - timedelta(days=i)
        # date.timetuple() 返回一个元组，包含年月日时分秒的格式化时间，用于转换成时间戳
        # 构建出一个字典，key是日期，value是时间戳和0的列表{‘2024-01-01’: [1672537600, 0]}
        date_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple())*1000, 0]
    # 得到每日问题个数的数据
    # select id,name, strftime("%Y-%m-%d",create_datetime) as ctime from table;
    # "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
    # select = {'ctime': "strftime('%%Y-%%m-%%d',web_issues.create_datetime)"}
    """
    得到的数据格式是这样的
    [
        {'ctime': '2023-04-01', 'ct': 5},  # 假设2023年4月1日有5个Issues被创建
        {'ctime': '2023-04-02', 'ct': 10},  # 假设2023年4月2日有10个Issues被创建
        {'ctime': '2023-04-03', 'ct': 3},   # 假设2023年4月3日有3个Issues被创建
        # ... 其他日期及其对应的Issue数量
    ]
    """
    result = (models.Issue.objects.filter(project=request.tracer.project, create_time__gte=today - timedelta(days=30))
              .extra(select={'ctime': "DATE_FORMAT(web007_issue.create_time,'%%Y-%%m-%%d')"}).values('ctime').
              annotate(ct=Count('id')))  # 最近30天的每日问题个数，
    for item in result:
        date_dict[item['ctime']][1] = item['ct']  # 更新字典，将数据填进去
    # 将数据转换为列表，返回给前端，格式是这样的[[时间戳，问题数量]，...]
    return JsonResponse({'status':True, 'data':list(date_dict.values())})