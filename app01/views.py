# !/usr/bin/env python
# coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from app01 import models as app01_models
from sts.sts import Sts
from BugManagePlatform import settings
from app01 import models


class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号', max_length=11, validators=[RegexValidator('^1[3-9]\\d{9}$', '手机号格式错误')]
    )
    password = forms.CharField(
        label='密码', max_length=16, widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        label='确认密码', max_length=16, widget=forms.PasswordInput()
    )
    code = forms.CharField(
        widget=forms.TextInput(), label='验证码', max_length=6,
        validators=[RegexValidator('^[0-9]{6}$', '验证码格式错误')]
    )

    class Meta:
        model = app01_models.UserInfo
        fields = ['username', 'password', 'confirm_password', 'mobile_phone', 'code']

    # 为每个表单项添加样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = f'请输入{filed.label}'


def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})

def login(request):
    print(request.GET.get('mobile_phone'),request.GET.get('tpl'))
    return render(request, 'app01/login.html')


def upload_file(request):
    return render(request, 'app01/upload-file.html')


# 获取临时凭证，解决跨域问题。
def get_cridential(request):
    config = {
        # 请求URL，域名部分必须和domain保持一致
        # 使用外网域名时：https://sts.tencentcloudapi.com/
        # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        # 内网域名：sts.internal.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': settings.TENCENT_APP_ID,
        # 固定密钥
        'secret_key': settings.TENCENT_APP_KEY,
        # 换成你的 bucket
        'bucket': 'zy089721-1327273828',
        # 换成 bucket 所在地区
        'region': 'ap-beijing',
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            # 'name/cos:PostObject',
            # # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
        ],
    }
    try:
        sts = Sts(config)
        response = sts.get_credential()
        return JsonResponse(response)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)})


# 新建文件或文件夹页面，目录逐层显示的问题
# 用于生成文件目录结构
def file(request,project_id):
    # 生成一个folder_id用户接受前端get发送来的文件夹id
    folder_id = request.GET.get('folder_id')
    # 生成一个列表套字典字典，用于存储文件信息，字典中key设置为id,value设置为文件名
    file_list = []
    # 判断folder_id是否存在，如果不存在则pass,如果存在则从file表中查询folder_id对应的文件信息,
    if not folder_id:
        pass
    else:
        # 查询是否是文件夹
        file_obj = models.File.objects.filter(folder_id=folder_id,file_type=2).first()
        row_obj = file_obj
        # 如果row_obj存在，则while循环，将file_obj的id和name添加到字典中,然后赋值row_obj为file_obj的parent
        while row_obj:
            # 向列表的第0个位置添加字典，字典中key为id,value为row_obj.id，这样第一个位置一直是最上层，知道顶层，row_obj为None
            file_list.insert(0,{'id':row_obj.id,'name':row_obj.file_name})
            row_obj = row_obj.parent
    return JsonResponse(file_list)

