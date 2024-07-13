from django.db import models

# Create your models here.
from django.db import models


class UserInfo(models.Model):
    # 用户名可以被索引，增加搜索速度
    username = models.CharField(verbose_name='用户名', max_length=20, db_index=True)
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
    project_type = models.SmallIntegerField(verbose_name='项目分类', choices=category_choices, default=0)
    # 项目分类名称
    project_title = models.CharField(verbose_name='项目分类标题', max_length=32)
    # 项目价格
    project_price = models.PositiveIntegerField(verbose_name='项目价格')
    # 可创建项目个数
    project_count = models.PositiveIntegerField(verbose_name='可创建项目个数')
    # 项目可参加最大人数
    project_max_collaborator = models.PositiveIntegerField(verbose_name='项目可参加人数')
    # 项目占用最大空间
    project_max_space = models.PositiveIntegerField(verbose_name='项目占用最大空间',help_text='M')
    project_max_file = models.PositiveIntegerField(verbose_name='每个项目文件最大容量',help_text='M')
    # 项目创建时间 ,auto_now是每次自动保存当前时间,auto_now_add是只保存第一次自动保存当前时间
    project_create_time = models.DateTimeField(verbose_name='项目创建时间', auto_now_add=True)


# 交易表
class Order(models.Model):
    # 订单号
    order_number = models.CharField(verbose_name='订单号', max_length=64, unique=True, db_index=True)
    # 交易状态
    order_status = models.BooleanField(verbose_name='交易状态', default=False)
    # 用户编号
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    # 项目编号
    project = models.ForeignKey(ProjectStrategy, on_delete=models.CASCADE)
    # 实付金额
    order_price = models.PositiveIntegerField(verbose_name='实付金额')
    # 购买年限
    order_year = models.PositiveIntegerField(verbose_name='购买年限')
    # 支付时间
    order_pay_time = models.DateTimeField(verbose_name='支付时间', null=True, blank=True)
    # 结束时间
    order_end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    # 创建时间
    order_create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


# 项目详情表
class ProjectDetail(models.Model):
    COLOR_CHOICES = (
        (1, "primary"),  # 深蓝
        (2, "secondary"),  # 灰色
        (3, "success"),  # 绿色
        (4, "danger"),  # 红色
        (5, "warning"),  # 黄色
        (6, "info"),  # 浅蓝
        (7, "dark"),  # 黑色
    )
    # 项目名称
    project_name = models.CharField(verbose_name='项目名称', max_length=32)
    # 项目描述
    project_description = models.CharField(verbose_name='项目描述', max_length=128)
    # 项目创建人编号
    project_creator = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    # 项目参与人数
    project_collaborator = models.PositiveIntegerField(verbose_name='项目参与人数', default=1)
    # 项目颜色
    project_color = models.SmallIntegerField(verbose_name='项目颜色', choices=COLOR_CHOICES, default=1)
    # 星标
    project_star = models.BooleanField(verbose_name='星标', default=False)
    # 已使用空间
    project_used_space = models.BigIntegerField(verbose_name='已使用空间', default=0)
    # 存储桶
    project_bucket = models.CharField(verbose_name='存储桶', max_length=64)
    # 存储桶所在地
    project_bucket_location = models.CharField(verbose_name='存储桶所在地', max_length=32, default='ap-beijing')


# 项目参与表
class ProjectCollaborator(models.Model):
    # 项目编号
    project = models.ForeignKey(to='ProjectDetail', on_delete=models.CASCADE)
    # 参与人编号
    collaborator = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    # 星标（对于参与人是否是星标项目）
    collaborator_star = models.BooleanField(verbose_name='星标', default=False)
    # 参与时间
    collaborator_time = models.DateTimeField(verbose_name='参与时间', auto_now_add=True)


# wiki文档项目表
class Wiki(models.Model):
    # 项目编号
    project = models.ForeignKey(to='ProjectDetail', on_delete=models.CASCADE)
    # 文档标题
    wiki_title = models.CharField(verbose_name='标题', max_length=32, db_index=True)
    # 文档内容
    wiki_content = models.TextField(verbose_name='内容')
    # 创建时间
    parent = models.ForeignKey(verbose_name='父文章', to='self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children')

    depth = models.PositiveIntegerField(verbose_name='深度', default=1)

    # 改写打印时打印wiki标题。
    def __str__(self):
        return self.wiki_title


# 文件表，字段：project(外键连接ProjectDetail表),file_name(文件名),file_size(文件大小),file_type(文件类型),parent(父目录),key(新文件名)
class File(models.Model):
    file_type = (
        (1, '文件'),
        (2, '目录')
    )
    # 项目编号
    project = models.ForeignKey(to='ProjectDetail', on_delete=models.CASCADE)
    # 文件名
    file_name = models.CharField(verbose_name='文件名', max_length=128, db_index=True)
    # 文件大小
    file_size = models.BigIntegerField(verbose_name='文件大小', null=True, blank=True)
    # 文件类型
    file_type = models.SmallIntegerField(verbose_name='文件类型', choices=file_type, default=2)
    # 文件路径,考虑到长目录名，所以使用路径长度也大一些
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)
    # 父目录
    parent = models.ForeignKey('self', verbose_name='父目录', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children')
    # 新文件名
    key = models.CharField(verbose_name='新文件名', max_length=128)
    # 改写文件人员，与用户表关联
    user = models.ForeignKey(verbose_name='最近更新者', to=UserInfo, on_delete=models.CASCADE)
    # 创建时间
    file_update_time = models.DateTimeField(verbose_name='更新时间', auto_now_add=True)

    def __str__(self):
        return self.file_name
