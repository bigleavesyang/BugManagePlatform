from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from web007 import models
from web007.forms.wiki import WikiForm


def index(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    # 如果没有wiki_id，则返回wiki列表首页
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'web007/wiki.html')
    # 获取了当前项目的wiki文章
    wiki_project = models.Wiki.objects.filter(id=wiki_id, project=request.tracer.project).first()
    return render(request, 'web007/wiki.html', {'wiki_project': wiki_project})


def add(request, project_id):
    if request.method == 'GET':
        form = WikiForm(request)
        # 返回给列表，渲染页面
        return render(request, 'web007/wiki-add.html', {'form': form})

    form = WikiForm(request, data=request.POST)
    if form.is_valid():
        # 判断文章是否有父节点
        if form.instance.parent:
            # 获取父节点的深度并加1
            form.instance.depth = form.instance.parent.depth + 1
            # 如果没有父节点，则深度为1
        else:
            form.instance.depth = 1

        form.instance.project = request.tracer.project
        form.save()
        # 需要在网址中带参数
        url = reverse('web007:wiki', kwargs={'project_id': project_id})
        return redirect(url)
    # 字段审核没有通过，返回给列表，渲染页面
    return render(request, 'web007/wiki-add.html', {'form': form})


def catalog(request, project_id):
    # 获取当前项目的所有文章资料，并按照深度排序，然后按照id排序，并返回一个类似列表套字典的query对象
    data = models.Wiki.objects.filter(project=request.tracer.project).order_by('depth', 'id').values('id', 'wiki_title',
                                                                                                     'parent_id')
    # 返回json数据
    return JsonResponse({'status': True, 'data': list(data)})


def wiki_edit(request, project_id, wiki_id):
    wiki = models.Wiki.objects.filter(project=request.tracer.project, id=wiki_id).first()
    if not wiki:
        return redirect(reverse('web007:wiki', kwargs={'project_id': project_id}))
        # 获取当前项目的wiki文章
        # 把wiki对象传给form，让form自动渲染页面
    if request.method == 'GET':
        form = WikiForm(request,instance=wiki)
        return render(request, 'web007/wiki-add.html', {'form': form})

    form = WikiForm(request,data=request.POST, instance=wiki)
    if form.is_valid():
        # 判断文章是否有父节点
        if form.instance.parent:
            # 获取父节点的深度并加1
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        # 获取项目网址，并拼接wiki_id
        url = reverse('web007:wiki', kwargs={'project_id': project_id})
        # 返回到这个项目的wiki文章的预览页面
        preview_url = f'{url}?wiki_id={wiki_id}'
        return redirect(preview_url)
    else:
        return render(request, 'web007/wiki-add.html', {'form': form})


def wiki_del(request, project_id, wiki_id):
    models.Wiki.objects.filter(project=request.tracer.project, id=wiki_id).first().delete()
    url = reverse('web007:wiki', kwargs={'project_id': project_id})
    return redirect(url)
