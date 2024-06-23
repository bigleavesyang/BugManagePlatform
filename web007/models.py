from django.db import models

# Create your models here.
from django.db import models


class UserInfo(models.Model):
    # 用户名可以被索引，增加搜索速度
    username = models.CharField(verbose_name='用户名', max_length=20,db_index=True)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=11)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)


class ProjectStrategy(models.Model):
    # 项目分类的类似枚举作用的定义
    category_choices = (
        (0, '免费版'),
        (1, '收费版'),
        (2, '其他')
    )
    # 项目分类(收费，免费)
    project_type = models.SmallIntegerField(verbose_name='项目分类', choices=category_choices,default=2)
    # 项目分类名称
    project_title = models.CharField(verbose_name='项目分类标题', max_length=32)
    # 项目价格
    project_price = models.PositiveIntegerField(verbose_name='项目价格')
    # 可创建项目个数
    project_count = models.PositiveIntegerField(verbose_name='可创建项目个数')
    # 项目可参加最大人数
    project_max_collaborator = models.PositiveIntegerField(verbose_name='项目可参加人数')
    # 项目占用最大空间
    project_max_space = models.PositiveIntegerField(verbose_name='项目占用最大空间')
    # 每个项目文件最大容量
    project_max_file = models.PositiveIntegerField(verbose_name='每个项目文件最大容量')
    # 项目创建时间 ,auto_now是每次自动保存当前时间,auto_now_add是只保存第一次自动保存当前时间
    project_create_time = models.DateTimeField(verbose_name='项目创建时间',auto_now_add=True)


# 交易表
class Order(models.Model):
    # 订单号
    order_number = models.CharField(verbose_name='订单号', max_length=64,unique=True,db_index=True)
    # 交易状态
    order_status = models.BooleanField(verbose_name='交易状态', default=False)
    # 用户编号
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    # 项目编号
    project_id = models.ForeignKey(ProjectStrategy, on_delete=models.CASCADE)
    # 实付金额
    order_price = models.PositiveIntegerField(verbose_name='实付金额')
    # 购买年限
    order_year = models.PositiveIntegerField(verbose_name='购买年限')
    # 支付时间
    order_pay_time = models.DateTimeField(verbose_name='支付时间',null=True,blank=True)
    # 结束时间
    order_end_time = models.DateTimeField(verbose_name='结束时间',null=True,blank=True)
    # 创建时间
    order_create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)



# 项目详情表
class ProjectDetail(models.Model):
    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )
    # 项目名称
    project_name = models.CharField(verbose_name='项目名称', max_length=32)
    # 项目描述
    project_description = models.CharField(verbose_name='项目描述', max_length=128)
    # 项目创建人编号
    project_creator = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    # 项目参与人数
    project_collaborator = models.PositiveIntegerField(verbose_name='项目参与人数')
    # 项目颜色
    project_color = models.SmallIntegerField(verbose_name='项目颜色', choices=COLOR_CHOICES, default=1)
    # 星标
    project_star = models.BooleanField(verbose_name='星标', default=False)
    # 已使用空间
    project_used_space = models.PositiveIntegerField(verbose_name='已使用空间',default=0)


# 项目参与表
class ProjectCollaborator(models.Model):
    # 项目编号
    project_id = models.ForeignKey(to='ProjectDetail', on_delete=models.CASCADE)
    # 参与人编号
    collaborator_id = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    # 星标（对于参与人是否是星标项目）
    collaborator_star = models.BooleanField(verbose_name='星标', default=False)
    # 参与时间
    collaborator_time = models.DateTimeField(verbose_name='参与时间',auto_now_add=True)



