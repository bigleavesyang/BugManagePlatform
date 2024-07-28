from django import forms
from web007.forms.Bootstrap import BootStrapMixin
from web007 import models


class IssueForm(forms.ModelForm, BootStrapMixin):
    class Meta:
        model = models.Issue
        exclude = ['creator', 'project', 'create_time', 'last_update_time']
        widgets = {
            "assign": forms.Select(attrs={"class": "selectpiker form-select", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(attrs={
                "class": "selectpiker form-select", "data-live-search": "true", 'data-actions-box': "true"
            }),
            "parent": forms.Select(attrs={'class': "selectpicker form-select", "data-live-search": "true"}),
            'start_date': forms.DateInput(attrs={'autocomplete': 'false'}),
            'end_date': forms.DateInput(attrs={'autocomplete': 'false'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['priority'].widget.attrs['class'] = 'form-select'
        self.fields['issues_type'].widget.attrs['class'] = 'form-select'
        self.bootstrap_class_exclude = ['assign', 'attention', 'parent', 'status', 'priority']
        self.add_bootstrap_class()

        # 数据初始化的筛选
        self.fields['issues_type'].choices = models.IssueType.objects.filter(
            project=request.tracer.project).values_list('id', 'title')
        # 模块可以为空
        module_list = [('', '没有选择模块')]
        module_list.extend(models.Module.objects.filter(
            project=request.tracer.project).values_list('id', 'title'))
        self.fields['module'].choices = module_list
        # 项目的创建者与参与者才可以进入问题的指派和关注
        issues_user_list = []
        pro_creator = models.ProjectDetail.objects.filter(
            id=request.tracer.project.id).values_list('project_creator__id', 'project_creator__username')
        pro_collaborator = models.ProjectCollaborator.objects.filter(
            project=request.tracer.project).values_list('collaborator__id', 'collaborator__username')
        issues_user_list.extend(pro_creator)
        issues_user_list.extend(pro_collaborator)
        self.fields['assign'].choices = issues_user_list
        # 关注者是可以为空的
        issues_attention_list = [("", '没有关注者')]
        issues_attention_list.extend(issues_user_list)
        self.fields['attention'].choices = issues_attention_list


class IssuesReplyForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class ProjectInviteForm(forms.ModelForm, BootStrapMixin):
    class Meta:
        model = models.ProjectInvite
        fields = ['period', 'max_invite']

    # 为邀请码弹出页面添加样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].widget.attrs['class'] = 'form-select'
        self.bootstrap_class_exclude = ['period']
        self.add_bootstrap_class()
