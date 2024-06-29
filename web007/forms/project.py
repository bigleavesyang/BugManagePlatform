from django import forms
from web007 import models
from web007.forms.Bootstrap import BootStrapMixin


class ProjectModelForm(forms.ModelForm, BootStrapMixin):
    project_name = forms.CharField(label='项目名', max_length=32, error_messages={
        'required': '请输入项目名称',
        'max_length': '项目名最长32个字符'
    })

    # 把请求传进来，请求中有用户信息和用户权限信息
    class Meta:
        model = models.ProjectDetail
        fields = ['project_name', 'project_color', 'project_description']
        # 自定义字段的样式
        widgets = {
            'project_description': forms.Textarea,
            'project_color': forms.Select(choices=models.ProjectDetail.COLOR_CHOICES)
        }

    # 这里运行了继承来的add_bootstrap_class方法,改写了project_color的样式,同时接受了request参数
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.add_bootstrap_class()

        color_mapping = {
            'primary': '蓝色',
            'secondary': '灰色',
            'success': '绿色',
            'danger': '红色',
            'warning': '黄色',
            'info': '浅蓝色',
            'light': '白色',
            'dark': '黑色'
        }
        # 列表套元组，初始颜色
        original_choices = self.fields['project_color'].widget.choices
        # 列表套元组，修改后的颜色
        new_choices = [(key, color_mapping.get(value)) for key, value in original_choices]
        # 修改样式，将元组列表赋值给choices
        self.fields['project_color'].widget.choices = new_choices

    def clean_project_name(self):
        # 获取用户输入的名称
        name = self.cleaned_data['project_name']
        # 1、获取这个用户创建的项目是否存在
        if models.ProjectDetail.objects.filter(project_name=name, project_creator=self.request.tracer.user).exists():
            raise forms.ValidationError('项目已存在')
        # 2、用户是否还有额度去创建项目
        count = models.ProjectDetail.objects.filter(project_creator=self.request.tracer.user).count()
        if count >= self.request.tracer.price_strategy.project_count:
            raise forms.ValidationError('项目数量已达上限')
        return name
