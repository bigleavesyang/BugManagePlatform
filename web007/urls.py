from django.urls import path, include

from web007.views import account
from web007.views import project
from web007.views import home
from web007.views import wiki
from web007.views import file
from web007.views import settings
from web007.views import issues
from web007.views import dashboard
from web007.views import statistics

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

        path('wiki/', wiki.index, name='wiki'),
        path('wiki/add/', wiki.add, name='wiki_add'),
        # 接受前端ajax发来的请求，返回json格式的数据，返回的是文章列表。
        path('wiki/catelog/', wiki.catalog, name='wiki_catalog'),
        path('wiki/edit/<int:wiki_id>/', wiki.wiki_edit, name='wiki_edit'),
        path('wiki/delete/<int:wiki_id>/', wiki.wiki_del, name='wiki_del'),
        path('wiki/upload/', wiki.upload_image, name='wiki_upload'),

        # 文件路径相关
        path('file/', file.file, name='file'),
        path('file/delFolder/', file.del_folder, name='delete_folder'),
        path('file/getCredential/', file.get_credential, name='get_credential'),
        path('file/postFile/', file.post_file, name='post_file'),
        path('file/download/<int:file_id>', file.file_download, name='file_download'),

        # 设置路径相关
        path('settings/', settings.settings, name='settings'),
        path('settings/delete/', settings.settings_delete, name='settings_delete'),

        # 问题处理相关路径
        path('issues/', issues.issues, name='issues'),
        path('issues/detail/<int:issues_id>',issues.issues_detail, name='issues_detail'),
        path('issues/issues-record/<int:issues_id>/', issues.issues_record,name='issues_record'),
        path('issues/issues-change/<int:issues_id>/', issues.issues_change,name='issues_change'),
        path('issues/project-invite/',issues.project_invite,name='project_invite'),

        # 项目首页路径
        path('dashboard/', dashboard.dashboard, name='dashboard'),
        path('dashboard/issues-chart/', dashboard.issues_chart, name='issues_chart'),


        path('statistics/', statistics.statistics, name='statistics'),
        path('statistics/statistics/priority/', statistics.statistics_priority, name='statistics_priority'),
        path('statistics/statistics/project-user/',statistics.statistics_project_user,name='statistics_project_user'),
    ])),
    # 放在manage路径外面，以为被邀请成员，没有权限进入管理页面
    path('invite-join/<str:invite_code>/',issues.invite_join,name='invite_join'),
    path('price/',home.price,name='price'),
    path('payment/<int:policy_id>/',home.payment,name='payment'),
    path('pay/',home.pay,name='pay'),
    path('pay-return/',home.pay_return,name='pay_return')
]

app_name = 'web007'
