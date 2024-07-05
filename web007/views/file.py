from django.shortcuts import render, redirect
from django.http import JsonResponse
from web007 import models
from web007.forms.file import FolderForm
from utils.tencent import cos


# 文件页面的展示，新增与修改
def file(request, project_id):
    # 文件页面的展示
    # 先设置当前目录的父目录为空
    parent = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent = models.File.objects.filter(file_type=2, id=int(folder_id), project=request.tracer.project).first()

    if request.method == 'GET':
        form = FolderForm(request, parent)
        # 设置一个列表用于存储文件夹的级联关系。
        folder_list = []
        current_folder = parent
        while current_folder:
            # 获取父目录的id和名称，并添加到列表中。
            folder_list.insert(0, {'folder_id': current_folder.id, 'folder_name': current_folder.file_name})
            # 获取父目录的父目录，直到没有父目录为止。
            current_folder = current_folder.parent
        # 如果有父目录
        if parent:
            # 按照文件类型排序，把所有目录下得文件和文件夹找出来发给前端。
            file_list = models.File.objects.filter(parent=parent, project=request.tracer.project).order_by('-file_type')
        # 没有父目录，则是根目录，把所有文件和文件夹找出来发给前端。
        else:
            file_list = models.File.objects.filter(parent=None, project=request.tracer.project).order_by('-file_type')
        context = {
            'form': form,
            'file_list': file_list,
            'folder_list': folder_list,
        }
        return render(request, 'web007/file.html', context)

    # 文件夹的添加和修改
    fid = request.POST.get('fid', '')
    # 如果fid不为空，说明是修改操作,获取要修改的文件夹对象。
    edit_obj = None
    if fid.isdecimal():
        edit_obj = models.File.objects.filter(id=int(fid), project=request.tracer.project, file_type=2).first()
    if edit_obj:
        form = FolderForm(request, parent, data=request.POST, instance=edit_obj)
    else:
        form = FolderForm(request, parent, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.parent = parent
        form.instance.user = request.tracer.user
        form.instance.file_type = 2
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


# 删除文件及文件夹（级联删除）
def del_folder(request, project_id):
    # 获取要删除的文件夹id
    file_obj = None
    fid = request.GET.get('fid', '')
    if fid.isdecimal():
        file_obj = models.File.objects.filter(id=int(fid), project=request.tracer.project).first()
    # 如果是文件，则归还用户使用空间，并删除文件。需要同时删除数据库中记录，以及腾讯云端的文件。
    if file_obj.file_type == 1:
        # 归还用户使用空间
        request.tracer.project.project_used_space -= file_obj.file_size
        request.tracer.project.save()
        # 删除腾讯云端文件
        cos.del_file(request.tracer.project.project_bucket, file_obj)
        file_obj.delete()
        return JsonResponse({'status': True})

    # 如果是文件夹，数据库中数据在删除时已经级联删除了，需要处理的是腾讯云端文件夹下每个文件的删除。另外需要记录被删除的文件夹下的文件大小，并归还用户使用空间。
    total_size = 0
    # 先建立一个列表用于储备被删除的文件夹下的文件夹。
    file_list = [file_obj, ]
    # 建立一个被删除文件列表，用于记录被删除的文件在服务器上的名字，以便删除腾讯云端文件。
    key_list = []
    # 上面已经判断了到这，说明是文件夹，开始循环处理。
    for folder in file_list:
        # 获取文件夹下的所有内容，这是一个列表。
        child_list = models.File.objects.filter(parent=folder, project=request.tracer.project).order_by('-file_type')
        # 循环处理每个内容，如果是文件，则归还用户使用空间并删除腾讯云端文件。如果是文件夹，则把文件夹添加到列表中，等待下次循环处理。
        for child in child_list:
            if child.file_type == 1:
                total_size += child.file_size
                # 形成腾讯云批量删除的格式。
                key_list.append({'key': child.file_name})
            else:
                file_list.append(child)
    # cos端批量删除文件
    cos.batch_del_file(request.tracer.project.project_bucket, key_list)

    # 归还用户使用空间
    request.tracer.project.project_used_space -= total_size
    request.tracer.project.save()

    # 删除数据库中记录
    file_obj.delete()
    return JsonResponse({'status': True})
