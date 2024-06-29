from django.template import Library
from web007 import models
from django.urls import reverse

register = Library()


# 导航栏菜单引入
@register.inclusion_tag('web007/layout/NavBarMenu.html')
def nav_bar_menu(request):
    my_projects_list = models.ProjectDetail.objects.filter(project_creator=request.tracer.user)
    join_projects_list = models.ProjectCollaborator.objects.filter(collaborator=request.tracer.user)
    return {'my': my_projects_list, 'join': join_projects_list, 'request': request}


# 把进入项目后显示的菜单栏用tag的形式引入，并在这里做更复杂的逻辑判断，这里给被点击的菜单加上active类
@register.inclusion_tag('web007/layout/manage-list.html')
def manage_list(request):
    url_list = [
        {'title': '概览', 'url': reverse('web007:dashboard', kwargs={'project_id': request.tracer.project.id}), },
        {'title': '问题', 'url': reverse('web007:issues', kwargs={'project_id': request.tracer.project.id}), },
        {'title': '统计', 'url': reverse('web007:statistics', kwargs={'project_id': request.tracer.project.id}), },
        {'title': 'wiki', 'url': reverse('web007:wiki', kwargs={'project_id': request.tracer.project.id}), },
        {'title': '文件', 'url': reverse('web007:file', kwargs={'project_id': request.tracer.project.id}), },
        {'title': '设置', 'url': reverse('web007:setting', kwargs={'project_id': request.tracer.project.id}), },
    ]
    for item in url_list:
        # 判断当前访问的url是否在导航栏菜单中，如果是就给active类
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'
    return {'url_list': url_list}
