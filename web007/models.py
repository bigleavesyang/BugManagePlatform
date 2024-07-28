from django.db import models

# Create your models here.
from django.db import models


class UserInfo(models.Model):
    # 用户名可以被索引，增加搜索速度
    username = models.CharField(verbose_name='用户名', max_length=20, db_index=True)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=11)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)

    def __str__(self):
        return self.username


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
    project_max_space = models.PositiveIntegerField(verbose_name='项目占用最大空间', help_text='M')
    project_max_file = models.PositiveIntegerField(verbose_name='每个项目文件最大容量', help_text='M')
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
    # 价格策略
    project_strategy = models.ForeignKey(ProjectStrategy, on_delete=models.CASCADE)
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


# 和项目相关的问题表
class Issue(models.Model):
    # 关联的项目
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.CASCADE)
    # 问题类型
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssueType', null=True, on_delete=models.SET_NULL)
    # 问题模块（进度）
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.SET_NULL)
    # 主题及描述
    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    # 问题优先级
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')
    # 问题状态
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    # 被指派者
    assign = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE, verbose_name='指派', related_name='task')
    #  关注者，这是一个manytomany字段
    attention = models.ManyToManyField(to='UserInfo', verbose_name='关注者', related_name='observe')
    start_date = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    # 父问题
    parent = models.ForeignKey(verbose_name='父问题', to='self', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='child')
    # 问题的创建者
    creator = models.ForeignKey(verbose_name='创建者', to=UserInfo, on_delete=models.CASCADE,
                                related_name='create_problem')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_update_time = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class IssueType(models.Model):
    PROJECT_ISSUES_TYPE = ['任务', '功能', 'Bug']

    title = models.CharField(verbose_name='类型名称', max_length=32, )
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title


class Module(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.DO_NOTHING)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesReply(models.Model):
    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.SmallIntegerField(verbose_name='类型', choices=reply_type_choices, default=2)
    issues = models.ForeignKey(to='Issue', on_delete=models.CASCADE, verbose_name='问题')
    creator = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE, related_name='create_reply')
    content = models.TextField(verbose_name='描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 是否是某个回复的评论
    reply = models.ForeignKey(to='self', null=True, blank=True, on_delete=models.CASCADE, related_name='parent_reply')


"""
生成一个项目邀请码生成表，用于邀请用户加入项目
字段：关联的项目，邀请码，最大邀请人数（可以为空），已经使用的邀请人数数量，
    邀请码有效时间（30分钟，1小时，5小时，24小时），生成的时间，创建者
"""


class ProjectInvite(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='ProjectDetail', on_delete=models.CASCADE)
    invite_code = models.CharField(max_length=64, verbose_name='邀请码')
    max_invite = models.PositiveIntegerField(verbose_name='最大邀请人数', null=True, blank=True,
                                             help_text='如果为空，则表示不限制')
    invite_num = models.PositiveIntegerField(verbose_name='已邀请人数', default=0)
    time_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时')
    )
    period = models.IntegerField(verbose_name='有效时间', choices=time_choices, default=1440)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE, related_name='create_invite')
