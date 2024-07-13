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


class PostFileForm(forms.ModelForm):
    etag = forms.CharField(label='etag')
    class Meta:
        model = models.File
        exclude = ['file_type','project','file_update_time','user']

    def __init__(self, request,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.request = request


    def clean_file_path(self):
        return f'http://{self.cleaned_data["file_path"]}'


    # 对上传后的文件进行细粒度的校验，检查是否有人恶意传输文件。
    # def clean(self):
    #     # 检验这三项是否与服务端返回的信息一致，如果不一致则认为有人恶意传输文件
    #     key = self.cleaned_data['key']
    #     etag = self.cleaned_data['etag']
    #     file_size = self.cleaned_data['file_size']
    #     if not key or not etag:
    #         # 直接返回数据，不进行继续校验，因为校验失败了，views视图中会直接返回错误信息
    #         return self.cleaned_data
    #     # 进行细密度校验，先从腾讯云获取文件传输结果。
    #     from utils.tencent.cos import check_file
    #     res = check_file(self.request.tracer.project.project_bucket,key)
    #
    #     cos_etag = res['ETag']
    #     if etag != cos_etag:
    #         self.add_error('etag', 'ETag校验失败')
    #         return self.cleaned_data
    #
    #     cos_file_size = res['Content-Length']
    #     if file_size != cos_file_size:
    #         self.add_error('file_size', '文件大小校验失败')
    #         return self.cleaned_data
    #
    #     return self.cleaned_data