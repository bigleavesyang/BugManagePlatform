from django.urls import path
from app01 import views as app01_views

urlpatterns = [
    path('register/', app01_views.register,name='register'),
    path('login/', app01_views.login,name='login'),
    path('upload/', app01_views.upload_file,name='upload'),
    path('upload/cridential/',app01_views.get_cridential,name='get_cridential'),
    # AJAX测试
    path('ajax/get/',app01_views.ajax_get,name='ajax_get'),
    path('ajax/',app01_views.ajax,name='ajax'),
]

app_name = 'app01'