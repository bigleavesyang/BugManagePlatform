from web007 import models
from django import forms
from django.core.exceptions import ValidationError


class FolderForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = ['file_name']

    def __init__(self, request,parent,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.request = request
        self.parent = parent
        self.fields['file_name'].widget.attrs = {'placeholder': '请输入文件夹名称', 'class': 'form-control'}

    # 传过来的文件夹名称如果重名则报错
    def clean_file_name(self):
        file_name = self.cleaned_data['file_name']
        first_query = models.File.objects.filter(file_name=file_name,file_type=2,project=self.request.tracer.project)
        # 判断父级文件夹是否存在，如果存在看父级文件夹下是否存在重名
        if self.parent:
            exists = first_query.filter(parent=self.parent).exists()
        else:
            # 判断父级文件夹是否为空,如果为空则表示是根目录，根目录下不能重名
            #  # 使用 parent__isnull=True 而不是 parent=None,因为更显式
            exists = first_query.filter(parent=None).exists()
        if exists:
            raise ValidationError('文件夹名称不能重复')
        return file_name