from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from web007 import models
from BugManagePlatform import settings


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 获取用户id或者没有就设置为0，0的索引在数据库中是无效的
        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        # 用户信息存在，则新建一个属性，将用户信息保存到request中，各个页面都可以使用，否则是空
        request.tracer = user_obj

        # 检查网址白名单，如果用户的请求地址在白名单中，则直接放行
        if request.path_info in settings.URL_WHITE_LIST:
            return

        # 如果用户没有登录，访问白名单以外的页面，则跳转到登录页面
        if not request.tracer:
            return redirect('web007:login')
