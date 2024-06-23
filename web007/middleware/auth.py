from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from web007 import models
from BugManagePlatform import settings
import datetime


class Tracer:
    def __init__(self):
        self.user = None
        self.price_strategy = None


class AuthMiddleware(MiddlewareMixin):
    # 新建一个类，用于在request中保存用户信息和用户的权限额度，方便各个页面使用
    def process_request(self, request):
        # 实例化一个封装了用户信息和权限额度的新对象
        request.tracer = Tracer()
        # 获取用户id或者没有就设置为0，0的索引在数据库中是无效的
        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        # 用户信息存在，则新建一个属性，将用户信息保存到对象中，各个页面都可以使用，否则是空
        request.tracer.user = user_obj

        # 检查网址白名单，如果用户的请求地址在白名单中，则直接放行
        if request.path_info in settings.URL_WHITE_LIST:
            return

        # 如果用户没有登录，访问白名单以外的页面，则跳转到登录页面
        if not request.tracer.user:
            return redirect('web007:login')

        # 获取用户权限额度, 按订单ID倒序排列，取最近一个就是付费订单
        project_strategy = models.Order.objects.filter(user=user_obj, order_status=1).order_by('-id').first()
        current_time = datetime.datetime.now()
        # 如果用户策略是免费版，project_strategy为空，或者结束时间小于当前时间，则表明用户已经到期
        if not project_strategy or project_strategy.order_end_time < current_time:
            # 设置为免费版策略
            request.tracer.price_strategy = models.ProjectStrategy.objects.filter(project_type=0,
                                                                                  project_title='免费版').first()
        # 用户有额度，则直接保存到request中
        request.tracer.price_strategy = project_strategy
