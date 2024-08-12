from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from web007 import models


def statistics(request, project_id):
    return render(request, 'web007/statistics.html')


def statistics_priority(request, project_id):
    # 获取查询的时间节点
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    # 构建一个字典存储项目的问题描述及数量统计
    issues_dict = {}
    for key, value in models.Issue.priority_choices:
        issues_dict[key] = {'name': value, 'y': 0}
    # 找到项目中所有的问题，按照优先级进行分组并统计数量
    issues_count = models.Issue.objects.filter(
        project_id=project_id, create_time__gte=start_date, create_time__lte=end_date
    ).values('priority').annotate(ct=Count('priority'))
    for item in issues_count:
        issues_dict[item['priority']]['y'] = item['ct']
    # 按照前端需求的数据格式返回数据
    """
    数据格式：
    [
        {name: '高', y: 10},
        {name: '中', y: 20},
        {name: '低', y: 30}
    ]
    """
    return JsonResponse({'status': True, 'data': list(issues_dict.values())})


"""
   返回数据格式：（用户与数据一一对应）
   user_issues_dict = {
       'status': True,
       'data': {
           'categories': ['用户1', '用户2'],
           'series': [
               {name: '新建', data: [10, 20]},  ct结果
               {name: '处理中', data: [30, 40]}
       }
   }
   """


def statistics_project_user(request, project_id):
    # 获取查询的时间节点
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    # 构建一个字典存储所有用户的关于项目的问题类型描述及数量统计
    """
        info = {
            1:{
                name:"武沛齐",
                status:{
                    1:0,
                    2:1,
                    3:0,
                    4:0,
                    5:0,
                    6:0,
                    7:0,
                }
            },
            2:{
                name:"王洋",
                status:{
                    1:0,
                    2:0,
                    3:1,
                    4:0,
                    5:0,
                    6:0,
                    7:0,
                }
            }
        }
        """
    # 1. 所有项目成员 及 未指派
    all_user_dict = {}
    all_user_dict[request.tracer.project.project_creator.id] = {
        'name': request.tracer.project.project_creator.username,
        'status': {item[0]: 0 for item in models.Issue.status_choices}  # 生成式
    }
    all_user_dict[None] = {
        'name': '未指派',
        'status': {item[0]: 0 for item in models.Issue.status_choices}
    }
    users = models.ProjectCollaborator.objects.filter(project_id=project_id)
    for user in users:
        all_user_dict[user.collaborator_id] = {
            'name': user.collaborator.username,
            'status': {item[0]: 0 for item in models.Issue.status_choices}
        }

    # 2.去数据库中获取关于项目的所有问题，并判断是否有指派者，如果有则在其状态上+1
    issues = models.Issue.objects.filter(project_id=project_id, create_time__gte=start_date, create_time__lte=end_date)
    for issue in issues:
        # 如果没有指派者
        if not issue.assign:
            all_user_dict[None]['status'][issue.status] += 1
        else:
            all_user_dict[issue.assign_id]['status'][issue.status] += 1
    # 3.获取所有用户姓名,生成列表
    categories = [data['name'] for data in all_user_dict.values()]
    # 4.构造字典
    """
    data_result_dict = {
        1:{name:新建,data:[1，2，3，4]},
        2:{name:处理中,data:[3，4，5]},
        3:{name:已解决,data:[]},
        4:{name:已忽略,data:[]},
        5:{name:待反馈,data:[]},
        6:{name:已关闭,data:[]},
        7:{name:重新打开,data:[]},
    }
    """
    data_result_dict = {}
    for item in models.Issue.status_choices:
        data_result_dict[item[0]] = {
            'name': item[1],
            'data': []
        }
    # 5.构建data[]内部内容，每个客户在具体问题上的计数
    for key, text in models.Issue.status_choices:
        for user in all_user_dict.values():
            count = user['status'][key]
            data_result_dict[key]['data'].append(count)
    # 6.返回最终构造的数据
    context = {
        'status': True,
        'data': {
            'categories': categories,
            'series': list(data_result_dict.values())}
    }
    return JsonResponse(context)
