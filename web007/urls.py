from django.urls import path
from web007.views import account
from web007.views import project
from web007.views import home

urlpatterns = [
    # 用户模块
    path('register/', account.register,name='register'),
    path('send-sms/',account.send_sms,name='send_sms'),
    path('login-sms/', account.login_sms,name='login_sms'),
    path('login/',account.login,name='login'),
    path('image-code/',account.image_code,name='image_code'),
    path('index/',home.index,name='index'),
    path('logout/',account.logout,name='logout'),
    # 项目模块
    path('project-list/',project.project_list,name='project_list'),
]

app_name = 'web007'