from django.shortcuts import render, HttpResponse, redirect
from django.http.response import JsonResponse
from web007.forms.project import ProjectModelForm
from web007 import models
from utils.tencent import cos
import time


def project_list(request):
    # 注意实例化表单对象的时候传入POST数据
    form = ProjectModelForm(request, data=request.POST)
    if request.method == 'GET':
        # GET请求查看项目列表
        """
        1. 从数据库中获取两部分数据
            我创建的所有项目：已星标、未星标
            我参与的所有项目：已星标、未星标
        2. 提取已星标
            列表 = 循环 [我创建的所有项目] + [我参与的所有项目] 把已星标的数据提取
        得到三个列表：星标、创建、参与
        """
        projects_dict = {'star': [], 'my': [], 'join': []}
        # 获取我创建的所有项目
        my_projects_list = models.ProjectDetail.objects.filter(project_creator=request.tracer.user)
        for row in my_projects_list:
            if row.project_star:
                # 已星标
                projects_dict['star'].append({'value': row, 'type': 'my'})
            else:
                # 未星标
                projects_dict['my'].append(row)
        # 获取我参与的所有项目
        join_projects_list = models.ProjectCollaborator.objects.filter(collaborator=request.tracer.user)
        for row in join_projects_list:
            # 获取项目详情
            if row.collaborator_star:
                # 已星标
                projects_dict['star'].append({'value': row.project, 'type': 'join'})
            else:
                # 未星标
                projects_dict['join'].append(row.project)
        return render(request, 'web007/project-list.html', {'form': form, 'projects_dict': projects_dict})

    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        #创建项目存储文件的桶
        # 获取手机号码后3位+时间戳
        bucket_name = request.tracer.user.mobile_phone[-3:] + str(int(time.time()))+'-1327273828'
        # 在云端创建一个存储桶
        cos.create_bucket(bucket_name)
        form.instance.project_bucket = bucket_name
        form.instance.project_creator = request.tracer.user
        instance = form.save()
        # 创建问题列表中的问题类型
        issues_type_list = []
        for item in models.IssueType.PROJECT_ISSUES_TYPE:
            # 每个任务类型生成一个对象加到列表之中
            issues_type_list.append(models.IssueType(project=instance,title=item))
        models.IssueType.objects.bulk_create(issues_type_list)
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    if project_type == 'my':
        models.ProjectDetail.objects.filter(project_creator=request.tracer.user, id=project_id).update(
            project_star=True)
        return redirect('web007:project_list')
    if project_type == 'join':
        # project是一个外键，project_id是外键的id
        models.ProjectCollaborator.objects.filter(collaborator=request.tracer.user, project_id=project_id).update(
            collaborator_star=True)
        return redirect('web007:project_list')
    return HttpResponse('非法访问！')


def project_unstar(request, project_type, project_id):
    if project_type == 'my':
        models.ProjectDetail.objects.filter(project_creator=request.tracer.user, id=project_id).update(
            project_star=False)
        return redirect('web007:project_list')
    if project_type == 'join':
        # project是一个外键，project_id是外键的id
        models.ProjectCollaborator.objects.filter(collaborator=request.tracer.user, project_id=project_id).update(
            collaborator_star=False)
        return redirect('web007:project_list')
    return HttpResponse('非法访问！')
