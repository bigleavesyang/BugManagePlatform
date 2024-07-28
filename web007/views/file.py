from django.shortcuts import render, redirect,reverse
from django.http import JsonResponse,HttpResponse
from web007 import models
from web007.forms.file import FolderForm,PostFileForm
from utils.tencent import cos
import json
from django.views.decorators.csrf import csrf_exempt
import requests



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
            'folder_obj': parent,
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
        cos.del_file(request.tracer.project.project_bucket, file_obj.key)
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
                key_list.append({"Key": child.key})
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


# 获取cors的授权
@csrf_exempt #发送post请求不需要csrf证书
def get_credential(request, project_id):
    # 项目策略表中的文件最大限度。
    file_limit_size = request.tracer.price_strategy.project_max_file * 1024 * 1024
    # 项目策略表中的用户可使用最大空间。
    space_limit_size = request.tracer.price_strategy.project_max_space * 1024 * 1024
    # 从前端拿到每个文件的大小，并计算出总大小。
    total_size = 0
    # 获取前端传过来的文件列表。反序列化成python格式。
    file_list = json.loads(request.body.decode('utf-8'))
    for file_obj in file_list:
        if file_obj['size'] > file_limit_size:
            file_limit_m = int(file_obj["size"]/1024/1024)
            print(file_limit_m)
            msg = f'上传单个文件大小超出限制，请升级。{file_obj["name"]}大小{file_limit_m}M'
            return JsonResponse({'status': False, 'error': msg})
        total_size += file_obj['size']
    # 判断上传文件总量是否超出用户策略最大值。
    if request.tracer.project.project_used_space + total_size > space_limit_size:
        return JsonResponse({'status': False, 'error': '容量已超出限制，请升级套餐。'})
    # 所有条件都符合，往前端传回秘钥。
    bucket_name = request.tracer.project.project_bucket
    data_dict = cos.credential(request,bucket_name)
    return JsonResponse({'status': True,'data':data_dict})


# 往数据库中写入文件信息
@csrf_exempt
def post_file(request, project_id):
    """ 已上传成功的文件写入到数据 """
    """
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    # etag: data.ETag,
    file_path: data.Location
    """
    data = json.loads(request.body.decode('utf-8'))
    form = PostFileForm(request,data=data)
    if form.is_valid():
        # 通过ModelForm.save存储到数据库中的数据返回的isntance对象，无法通过get_xx_display获取choice的中文
        # form.instance.file_type = 1
        # form.update_user = request.tracer.user
        # instance = form.save() # 添加成功之后，获取到新添加的那个对象（instance.id,instance.name,instance.file_type,instace.get_file_type_display()

        # 校验通过：把清洗后的数据，写入到数据库中。并得到写入数据库后的对象。
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update({'project': request.tracer.project, 'user': request.tracer.user,'file_type': 1})
        instance = models.File.objects.create(**data_dict)
        # 计算用于已使用空间和新上传的文件的总大小。这里是字节。
        request.tracer.project.project_used_space += instance.file_size
        request.tracer.project.save()
        # 通过产生的对象中的属性，生成一个字典，用于返回给前端。进行渲染。
        res = {
            'id': instance.id,
            'name': instance.file_name,
            'size': instance.file_size,
            'username': instance.user.username,
            'datetime': instance.file_update_time.strftime('%Y-%m-%d %H:%M'),
            'download_url': reverse('web007:file_download', kwargs={'project_id':project_id,'file_id':instance.id}),
        }
        return JsonResponse({'status': True, 'data': res})
    else:
        return JsonResponse({'status': False, 'error': '文件写入错误'})


def file_download(request, project_id, file_id):
    file_obj = models.File.objects.filter(id=file_id,project=request.tracer.project).first()
    res = requests.get(file_obj.file_path)
    # 文件分块下载处理
    data = res.iter_content()
    # 设置content_type=application/octet-stream 用于提示下载的是二进制数据流
    response = HttpResponse(data, content_type='application/octet-stream')
    # 转义文件名中的特殊字符
    from django.utils.encoding import escape_uri_path
    # 设置响应头，同时对有可能出现的中文文件名进行转义
    response['Content-Disposition'] = 'attachment; filename="%s"' % escape_uri_path(file_obj.file_name)
    return response


