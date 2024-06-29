from django import forms
from web007 import models
from web007.forms.Bootstrap import BootStrapMixin


class WikiForm(BootStrapMixin, forms.ModelForm):
    class Meta:
        model = models.Wiki
        fields = ['wiki_title', 'wiki_content', 'parent']

    # 重新parent字段的初始化
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        total_choices_list = [('', '--------请选择')]
        project_document_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id',
                                                                                                       'wiki_title')
        total_choices_list.extend(project_document_list)
        self.fields['parent'].choices = total_choices_list
        # 添加bootstrap样式
        self.add_bootstrap_class()
