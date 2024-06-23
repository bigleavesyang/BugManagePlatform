from django.urls import path
from app01 import views as app01_views

urlpatterns = [
    path('register/', app01_views.register,name='register'),
    path('login/', app01_views.login,name='login'),
]

app_name = 'app01'