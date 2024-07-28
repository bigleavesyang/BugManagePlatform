from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.http import QueryDict
from web007.forms import issue
from utils.data_encrypt import uid
from utils.pagination import Pagination
from web007.forms.issue import ProjectInviteForm
from web007.models import Issue, IssuesReply, IssueType, ProjectCollaborator, ProjectInvite, Order, ProjectStrategy
from datetime import datetime, timedelta


class CheckList:
    # 和下面的查询部分是分离的，这里主要是返回给前端页面展示的
    def __init__(self, name, request, data_list):
        self.name = name
        self.request = request
        self.data_list = data_list

    # 生成一个生成器对象
    def __iter__(self):
        """
        已经被点击的checkbox生成链接的参数时就不包含自己(因为点击相当于取消了自己)，如果没有被点击，生成链接的参数就加上自己。
        如果点击了第一个checkbox,那么其他checkbox被点击时的参数如下：
        status=1&status=2
        status=1&status=3
        status=1&status=4
        status=1&status=5
        status=1&status=6
        status=1&status=7
        status=1&priority=danger
        status=1&priority=warning
        status=1&priority=success
        :return:
        """
        for item in self.data_list:
            # 判断当前请求的参数是否在查询集中，如果在就设置选中状态
            key = str(item[0])
            text = item[1]
            # 首先设置select的选择属性为空
            checked = ''
            # 每次循环生成一个新的value_list,如果status=1，那么第二次循环中，value_list就为['status=1']
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                # 如果key在前端请求的参数中，就设置选中状态，并从拷贝的参数表中删除
                checked = 'checked'
                # 为以点击的checkbox，生成的链接参数，把自己剔除掉了。
                value_list.remove(key)
            else:
                # 为未点击的checkbox，生成的链接参数，把自己加到拷贝的参数表中
                value_list.append(key)
            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=19
            query_dict = self.request.GET.copy()  # 拷贝一份所有请求参数的字典, 返回一个QueryDict对象
            query_dict._mutable = True  # 修改字典的只读属性为False
            query_dict.setlist(self.name, value_list)  # 修改具体字段的查询参数，添加一个查询条件作为链接的要传递的参数
            # 如果有分页参数，直接剔除，因为分页参数是和查询条件无关的
            query_dict.pop('page', None)
            # 拼接URL，这里的urlencode()是将request.GET的原始参数加上了自定义的通过setlist添加的参数
            url = f"{self.request.path_info}?{query_dict.urlencode()}"  # status=1&status=2&status=3&xx=1
            # print(query_dict.urlencode()) # 仔细观察这里的打印结果。配合前端
            # 生成HTML代码,点击一下checkbox,就触发了一下url点击。
            return_html = f"<a href='{url}' class='cell'><input type='checkbox' {checked} ><label>{text}</label></a>"
            # 返回安全认证的HTML代码
            yield mark_safe(return_html)


# 下拉表生成器，用于选择指派者和参与者
class SelectList:
    def __init__(self, name, request, data_list):
        self.name = name
        self.request = request
        self.data_list = data_list

    # 生成一个生成器对象
    def __iter__(self):
        # 生成一个多选select框，这里使用的是select2插件，需要前端自己引入js和css文件
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;'>")
        for item in self.data_list:
            # 判断当前请求的参数是否在查询集中，如果在就设置选中状态
            key = str(item[0])
            text = item[1]
            # 首先设置select的选择属性为空
            selected = ''
            # 每次循环生成一个新的value_list,如果status=1，那么第二次循环中，value_list就为['status=1']
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                # 如果key在前端请求的参数中，就设置选中状态，并从拷贝的参数表中删除
                selected = 'selected'
                # 为以点击的checkbox，生成的链接参数，把自己剔除掉了。
                value_list.remove(key)
            else:
                # 为未点击的checkbox，生成的链接参数，把自己加到拷贝的参数表中
                value_list.append(key)
            # 为自己生成URL
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            # 如果有分页参数，直接剔除，因为分页参数是和查询条件无关的
            query_dict.pop('page', None)
            url = f"{self.request.path_info}?{query_dict.urlencode()}"
            html_return = f"<option value='{url}' {selected}>{text}</option>"
            yield mark_safe(html_return)
        yield mark_safe("</select>")


def issues(request, project_id):
    if request.method == 'GET':
        # 设置查询条件列表
        allow_filter_name = ['status', 'issues_type', 'priority', 'assign', 'attention']
        # 根据URL做筛选，筛选条件（根据用户通过GET传过来的参数实现）
        # ?status=1&status=2&issues_type=1&priority=2&assign=3&attention=4
        # 筛选条件字典
        condition = {}
        for name in allow_filter_name:
            # 从GET中获取参数列表
            request_list = request.GET.getlist(name)
            # 如果参数列表为空，跳过
            if not request_list:
                continue
            # 参数列表不为空，将参数列表添加到筛选条件字典中
            condition[f'{name}__in'] = request_list
        """
        condition = {
            "status__in":[1,2],
            'issues_type__in':[1,]
        }
        """

        form = issue.IssueForm(request)
        # 将筛选条件字典添加到查询集中，分解出的字典会得到这样的SQL查询语句：
        # SELECT * FROM web007_issue WHERE status IN (1,2) AND issues_type IN (1,)
        query_set = Issue.objects.filter(project_id=project_id).filter(**condition)
        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=query_set.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=20
        )
        # 分页后返回的问题对象列表
        issues_obj_list = query_set[page_object.start:page_object.end]
        page_html = page_object.page_html()
        # 获取项目下的所有问题类型
        pro_issues_type_list = IssueType.objects.filter(project_id=project_id).values_list('id', 'title')
        # 获取项目的所有成员，创建者+参与者
        pro_member_list = [
            (request.tracer.project.project_creator_id, request.tracer.project.project_creator.username), ]
        pro_collaborator_list = ProjectCollaborator.objects.filter(project_id=project_id).values_list('id',
                                                                                                      'collaborator__username')
        pro_member_list.extend(pro_collaborator_list)
        # 生成邀请表单返回给前端，用于添加项目成员时渲染
        invite_form = ProjectInviteForm()
        # 添加过滤条件进入渲染页面
        return render(request, 'web007/issues.html', {
            'form': form,
            'invite_form': invite_form,
            'issues_obj_list': issues_obj_list,
            'page_html': page_html,
            'filter_list': [
                {'title': '问题类型', 'filter': CheckList('issues_type', request, pro_issues_type_list)},
                {'title': '状态', 'filter': CheckList('status', request, Issue.status_choices)},
                {'title': '优先级', 'filter': CheckList('priority', request, Issue.priority_choices)},
                {'title': '指派给', 'filter': SelectList('assign', request, pro_member_list)},
                {'title': '关注人', 'filter': SelectList('attention', request, pro_member_list)}
            ],
        })

    form = issue.IssueForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    issues_obj = Issue.objects.filter(project_id=project_id, id=issues_id).first()
    form = issue.IssueForm(request, instance=issues_obj)
    return render(request, 'web007/issues_detail.html', {'form': form, 'issues_obj': issues_obj})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    if request.method == 'GET':
        issues_reply_list = IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)
        data_list = []
        for row in issues_reply_list:
            data_list.append({
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_time.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            })
        is_creator = Issue.objects.filter(project_id=project_id, id=issues_id, creator=request.tracer.user.id).exists()
        return JsonResponse({"status": True, "data": data_list, 'is_creator': is_creator})

    form = issue.IssuesReplyForm(data=request.POST)
    if form.is_valid():
        form.instance.reply_type = 2
        form.instance.issues_id = issues_id
        form.instance.creator = request.tracer.user
        instance = form.save()
        data = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_time.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }
        return JsonResponse({"status": True, 'data': data})
    return JsonResponse({"status": False, "error": form.errors})


def issues_change(request, project_id, issues_id):
    issues_obj = Issue.objects.filter(project_id=project_id, id=issues_id).first()
    form = issue.IssueForm(request, data=request.POST, instance=issues_obj)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def project_invite(request, project_id):
    # 阻止通过GET请求访问
    if request.method == 'GET':
        return redirect('web007:issues', *[request.tracer.project.id, ])
    form = ProjectInviteForm(data=request.POST)
    if form.is_valid():
        # 如果申请邀请码的用户不是项目创建者，则返回错误信息
        if request.tracer.user != request.tracer.project.project_creator:
            form.add_error('max_invite', '您无权申请邀请码')
            return JsonResponse({'status': False, 'error': form.errors})
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        # 根据用户的手机号生成一个加密的邀请码
        invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.invite_code = invite_code
        form.save()
        # 返回前端一个带邀请码的url
        scheme = request.scheme  # 返回http或https
        host = request.get_host()  # 返回域名
        path = reverse('web007:invite_join', kwargs={'invite_code': invite_code})  # 返回路径
        url = f'{scheme}://{host}{path}'
        return JsonResponse({'status': True, 'url': url})


# 邀请加入项目,校验
def invite_join(request, invite_code):
    current_time = datetime.now()
    invite_obj = ProjectInvite.objects.filter(invite_code=invite_code).first()
    # 如果邀请码不对返回错误
    if not invite_obj:
        return render(request, 'web007/invite-join.html', {'error': '邀请码错误'})
    # 如果是项目创建者，提示错误，不需要邀请码
    if invite_obj.project.project_creator == request.tracer.user:
        return render(request, 'web007/invite-join.html', {'error': '您是项目创建者，不需要邀请码'})
    # 如果是项目成员，提示错误，不需要邀请码
    if ProjectCollaborator.objects.filter(project=request.tracer.project, collaborator=request.tracer.user).exists():
        return render(request, 'web007/invite-join.html', {'error': '您是项目成员，不需要邀请码'})

    # 根据订单表，判断当前用户权限，如果是付费用户，则最大邀请人数就是付费策略中的最大邀请人数
    user_strategy = Order.objects.filter(user=invite_obj.creator).order_by('-id').first() # 倒序排列，得到最近一次的订单情况
    max_member = 0
    if user_strategy.project_strategy.project_type == 1:
        max_member = user_strategy.project_strategy.project_max_collaborator
        # 如果是付费用户，如果到期了，则按照免费用户处理
        if user_strategy.order_end_time < current_time:
            # 免费版，最大项目参与人数是2
            max_member = ProjectStrategy.objects.filter(project_type=0).first().project_max_collaborator
    else:
        # 如果不是收费版，则最大项目参与人数是免费版的策略
        max_member = ProjectStrategy.objects.filter(project_type=0).first().project_max_collaborator

    # 先得到这个项目的所有参与人数统计
    current_member = ProjectCollaborator.objects.filter(project=invite_obj.project).count()
    current_member += 1  # 当前参与人数+1,把项目创建者算进去
    # 设否项目当前人员已经超出项目策略中的最大参与人数
    if current_member >= max_member:
        return render(request, 'web007/invite-join.html', {'error': f'当前项目参与人数已达上限，最多{max_member}人'})
    # 是否已经过期
    valid_time = invite_obj.create_time + timedelta(minutes=invite_obj.period)
    if valid_time < current_time:
        return render(request, 'web007/invite-join.html', {'error': f'邀请码已过期'})
    # 是否已经超出最大邀请人数
    if invite_obj.max_invite:
        if invite_obj.invite_num >= invite_obj.max_invite:
            return render(request, 'web007/invite-join.html', {'error': f'邀请码使用已超过最大次数'})
        invite_obj.invite_num += 1
        # 如果没超出，则把邀请人数+1
        invite_obj.save()
    # 条件都符合，则把当前用户加入项目
    ProjectCollaborator.objects.create(project=invite_obj.project, collaborator=request.tracer.user)
    # 项目表中的项目参与者+1
    invite_obj.project.project_collaborator += 1
    invite_obj.project.save()
    # 把被邀请到的项目返回给被邀请客户。
    return render(request, 'web007/invite-join.html', {'project': invite_obj.project})


