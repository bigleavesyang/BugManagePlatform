from django.shortcuts import render,redirect
from utils.tencent import cos
from web007 import models


def settings(request, project_id):
    return render(request, 'web007/settings.html')


# 删除项目和存储桶。
def settings_delete(request, project_id):
    if request.method == 'GET':
        return render(request, 'web007/settings-delete.html')

    project_name = request.POST.get('project_name')
    if not project_name or project_name != request.tracer.project.project_name:
        return render(request, 'web007/settings-delete.html',{'error':'项目不存在。'})

    if request.tracer.user != request.tracer.project.project_creator:
        return render(request, 'web007/settings-delete.html',{'error':'您没有权限删除该项目。'})

    # 1. 删除桶
    #       - 删除桶中的所有文件（找到桶中的所有文件 + 删除文件 )
    #       - 删除桶中的所有碎片（找到桶中的所有碎片 + 删除碎片 )
    #       - 删除桶
    # 2. 删除项目
    #       - 项目删除

    cos.delete_bucket(request.tracer.project.project_bucket)
    models.ProjectDetail.objects.filter(id=request.tracer.project.id).delete()
    return redirect('web007:project_list')


