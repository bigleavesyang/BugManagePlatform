from django.shortcuts import render
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from app01 import models as app01_models


class RegisterModelForm(forms.ModelForm):
    mobile_phone = forms.CharField(
        label='手机号', max_length=11, validators=[RegexValidator('^1[3-9]\d{9}$', '手机号格式错误')]
    )
    password = forms.CharField(
        label='密码', max_length=16, widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(
        label='确认密码', max_length=16, widget=forms.PasswordInput()
    )
    code = forms.CharField(
        widget=forms.TextInput(),label='验证码', max_length=6, validators=[RegexValidator('^[0-9]{6}$', '验证码格式错误')]
    )

    class Meta:
        model = app01_models.UserInfo
        fields = ['username', 'password', 'confirm_password','mobile_phone', 'code']

    # 为每个表单项添加样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name,filed in self.fields.items():
            filed.widget.attrs['class'] = 'form-control'
            filed.widget.attrs['placeholder'] = f'请输入{filed.label}'

def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})
