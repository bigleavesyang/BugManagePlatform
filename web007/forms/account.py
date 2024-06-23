import random
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from web007 import models
from utils.tencent import sms
from utils import data_encrypt
from BugManagePlatform import settings
from django.db.models import Q


class RegisterModelForm(forms.ModelForm):
    username = forms.CharField(
        label='用户名',
        error_messages={
            'required': '用户名不能为空',
        },
        validators=[
            RegexValidator('^[a-zA-Z0-9_]{8,16}$',
                           message='用户名为8-16位大小写字母数字和下划线')
        ]
    )
    email = forms.EmailField(
        label='邮箱',
        max_length=32,
        error_messages={
            'max_length': '邮箱长度不能大于32',
            'required': '邮箱不能为空',
        },
        validators=[
            RegexValidator('^[a-zA-Z0-9_-]+@[a-zA-Z0-9]+\\.[a-z]+$',
                           message='邮箱格式错误')
        ]
    )
    mobile_phone = forms.CharField(
        label='手机号',
        error_messages={
            'required': '手机号不能为空',
        },
        validators=[
            RegexValidator('^1[3-9]\\d{9}$', message='手机号格式错误')
        ]
    )
    password = forms.CharField(
        label='密码',
        error_messages={
            'required': '密码不能为空'
        },
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            '^[a-zA-z0-9_]{8,16}$', message='密码为8-16位大小写字母数字和下划线'
        )]
    )
    confirm_password = forms.CharField(
        label='确认密码',
        error_messages={
            'required': '重复密码不能为空',
        },
        widget=forms.PasswordInput(),
        validators=[RegexValidator('^[a-zA-z0-9_]{8,16}$',
                                   '用户名为8-16位大小写字母数字和下划线')]
    )
    code = forms.CharField(
        widget=forms.TextInput(), label='验证码',
        error_messages={'required': '验证码不能为空'},
        validators=[RegexValidator('^[0-9]{4}$', '验证码格式错误')]
    )

    class Meta:
        model = models.UserInfo
        fields = ['username', 'password', 'confirm_password', 'email', 'mobile_phone', 'code']

    def clean_username(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        username = self.cleaned_data['username']
        if models.UserInfo.objects.filter(username=username).exists():  # 需要加.exist(),不用遍历数据库
            raise ValidationError('用户名已存在')
        return username

    def clean_email(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        email = self.cleaned_data['email']
        if models.UserInfo.objects.filter(email=email).exists():
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        pwd = data_encrypt.encrypt(pwd)
        return pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        confirm_password = data_encrypt.encrypt(confirm_password)
        if pwd != confirm_password:
            raise ValidationError('两次密码输入不一致')
        return confirm_password

    def clean_mobile_phone(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        mobile_phone = self.cleaned_data['mobile_phone']
        if models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists():
            raise ValidationError('手机号已存在')
        return mobile_phone

    def clean_code(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # 防止前面字段没验证通过，导致mobile_phone为空
        if not mobile_phone:
            return code
        redis_conn = get_redis_connection('default')
        sms_code = redis_conn.get(mobile_phone)
        if not sms_code:
            raise ValidationError('验证码已过期')
        sms_code = sms_code.decode('utf-8')
        if code != sms_code:
            raise ValidationError('验证码错误')
        return code

    def db_update(self):
        import uuid
        user = models.UserInfo.objects.filter(username=self.cleaned_data['username']).first()
        # user_id传入的是一个user对象，而不是id，user_id_id是user的id,_id是django添加的。
        order_id = str(uuid.uuid4())
        models.Order.objects.create(
            order_status=True, order_number=order_id, order_year=0, order_price=0,
            order_pay_time=None,order_end_time=None, user_id=user, project_id_id=1
        )


class SendMsgForm(forms.Form):
    mobile_phone = forms.CharField(
        error_messages={'required': '手机号不能为空'},
        label='手机号', max_length=11, validators=[RegexValidator('^1[3-9]\\d{9}$', '手机号格式错误')]
    )

    # 在对象初始化时获取用户网页的request对象
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
    def clean_mobile_phone(self):
        # 对模版进行校验
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE[tpl]
        if not template_id:
            raise ValidationError('短信模板不存在')
        # 钩子校验手机号是否存在
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if tpl == 'register':
            if models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists():
                raise ValidationError('手机号已存在')
        if tpl == 'login':
            if not models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists():
                raise ValidationError('手机号未注册')
        # 生成验证码并判断是否发送成功
        code = str(random.randrange(1000, 9999))
        sms_phone_num = '+86' + mobile_phone
        # 短信
        res = sms.send_sms_msg(sms_phone_num, template_id, code)
        # 发送短信(发送失败，抛出异常)
        if res != 'Ok':
            raise ValidationError('短信发送失败')
        # 验证码写入redis
        redis_conn = get_redis_connection('default')
        redis_conn.set(mobile_phone, code, ex=60)
        # 将SMS验证码返回给前端，这里是模拟用，因为无法发送真正的验证码
        return mobile_phone


class SendMsgLoginForm(forms.Form):
    mobile_phone = forms.CharField(
        error_messages={'required': '手机号不能为空'},
        label='手机号', max_length=11, validators=[RegexValidator('^1[3-9]\\d{9}$', '手机号格式错误')]
    )
    code = forms.CharField(
        error_messages={'required': '验证码不能为空'},
        label='验证码', validators=[RegexValidator('^[0-9]{4}$', '验证码格式错误')]
    )

    def clean_mobile_phone(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        mobile_phone = self.cleaned_data['mobile_phone']
        # 根据收据号判断用户是否存在
        user_obj = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_obj:
            raise ValidationError('手机号还没有注册')
        # 成功直接返回user_obj
        return user_obj

    def clean_code(self):
        # 钩子函数，指在表单正常校验之后，自己加入的逻辑校验，这个方法会在表单is.valid()时调用
        code = self.cleaned_data.get('code')
        user_obj = self.cleaned_data.get('mobile_phone')
        if not user_obj:
            raise ValidationError('手机号还没有注册')
        redis_conn = get_redis_connection('default')
        sms_code = redis_conn.get(user_obj.mobile_phone)
        if not sms_code:
            raise ValidationError('验证码已过期')
        sms_code = sms_code.decode('utf-8')
        if code != sms_code:
            raise ValidationError('验证码错误')
        return code


class LoginForm(forms.Form):
    username = forms.CharField(
        error_messages={
            'required': '用户名或邮箱不能为空',
        },
    )
    password = forms.CharField(
        error_messages={
            'required': '密码不能为空'
        },
        widget=forms.PasswordInput(render_value=True),  # 保留输入的密码
        validators=[RegexValidator(
            '^[a-zA-z0-9_]{8,16}$', message='密码为8-16位大小写字母数字和下划线'
        )]
    )
    code = forms.CharField(
        widget=forms.TextInput(), label='验证码',
        error_messages={'required': '验证码不能为空'},
        validators=[RegexValidator('^[A-Za-z]{5}$', '验证码格式错误')]
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        # 根据用户名和邮箱判断用户是否存在，注意这里Q的用法
        user_obj = models.UserInfo.objects.filter(Q(username=username) | Q(email=username)).first()
        if not user_obj:
            raise ValidationError('用户不存在')
        return user_obj

    def clean_password(self):
        password = self.cleaned_data['password']
        password = data_encrypt.encrypt(password)
        user_obj = self.cleaned_data.get('username')
        if not user_obj:
            raise ValidationError('用户不存在')
        if password != user_obj.password:
            raise ValidationError('密码错误')
        return password

    def clean_code(self):
        code = self.cleaned_data.get('code')
        redis_conn = get_redis_connection('default')
        user_uuid = redis_conn.get('user_uuid')
        if not user_uuid:
            raise ValidationError('验证码已过期')
        user_uuid = user_uuid.decode('utf-8')
        img_code = redis_conn.get(user_uuid)
        img_code = img_code.decode('utf-8')
        if code.upper() != img_code.upper():
            raise ValidationError('验证码错误')
        return code
