from django.urls import path, include
from web007.views import account
from web007.views import project
from web007.views import home
from web007.views import manage
from web007.views import wiki
from web007.views import file

urlpatterns = [
    # 用户模块
    path('register/', account.register, name='register'),
    path('send-sms/', account.send_sms, name='send_sms'),
    path('login-sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('image-code/', account.image_code, name='image_code'),
    path('index/', home.index, name='index'),
    path('logout/', account.logout, name='logout'),

    # 项目展示模块
    path('project-list/', project.project_list, name='project_list'),

    # ?P<project_type>是URL模式中捕获的参数。?P是正则表达式开始，\w+是正则表达式
    # 这是这个URL模式的名字。你可以使用这个名字在Django的模板中通过{% url 'project_star'
    #  project_type=some_type project_id=some_id %}来生成URL，或者在Python代码中通
    #  过reverse('project_star', kwargs={'project_type': some_type,
    #  'project_id': some_id})来生成URL。
    path('project-star/<str:project_type>/<int:project_id>/', project.project_star, name='project_star'),
    path('project-unstar/<str:project_type>/<int:project_id>/', project.project_unstar, name='project_unstar'),

    # 项目内部模块
    path('manage/<int:project_id>/', include([
        path('dashboard/', manage.dashboard, name='dashboard'),
        path('issues/', manage.issues, name='issues'),

        path('wiki/', wiki.index, name='wiki'),
        path('wiki/add/', wiki.add, name='wiki_add'),
        # 接受前端ajax发来的请求，返回json格式的数据，返回的是文章列表。
        path('wiki/catelog/',wiki.catalog, name='wiki_catalog'),
        path('wiki/edit/<int:wiki_id>/',wiki.wiki_edit, name='wiki_edit'),
        path('wiki/delete/<int:wiki_id>/', wiki.wiki_del, name='wiki_del'),
        path('wiki/upload/', wiki.upload_image, name='wiki_upload'),

        # 文件路径相关
        path('file/', file.file, name='file'),
        path('file/delFolder/', file.del_folder, name='delete_folder'),


        path('statistics/', manage.statistics, name='statistics'),
        path('setting/',manage.setting, name='setting'),
    ]))
]

app_name = 'web007'
