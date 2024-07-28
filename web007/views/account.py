from django.shortcuts import render, HttpResponse,redirect
from django.http import JsonResponse
from web007 import models
from web007.forms.account import SendMsgForm, RegisterModelForm, SendMsgLoginForm, LoginForm


# 注册
def register(request):
    if request.method == 'GET':
        return render(request, 'web007/register.html')
    form = RegisterModelForm(request.POST)
    if form.is_valid():
        form.save()
        form.db_update()
        return JsonResponse({'status': True, 'url': '/login/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


# 发送短信验证码
def send_sms(request):
    # 生成一个表单实例化对象，data = ...是初始化表单的值
    form = SendMsgForm(request, data=request.GET)
    # 校验手机是否存在，格式是否正确
    if form.is_valid():
        return JsonResponse({'status': True, })
    # 校验失败，返回错误信息，错误信息是form出现验证错误时自动生成的。
    return JsonResponse({'status': False, 'error': form.errors})


# 短信验证码登录
def login_sms(request):
    if request.method == 'GET':
        return render(request, 'web007/login-sms.html')
    form = SendMsgLoginForm(request.POST)
    if form.is_valid():
        # 短信验证码成功，后台清查手机号数据，直接返回前台一个用户对象
        user_obj = form.cleaned_data['mobile_phone']
        # 准备在session中保存用户对象
        request.session['user_id'] = user_obj.id
        request.session['user_name'] = user_obj.username
        return JsonResponse({'status': True, 'url': '/index/'})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


# 用户名密码登录
def login(request):
    if request.method == 'GET':
        return render(request, 'web007/login.html')
    form = LoginForm(request.POST)
    if form.is_valid():
        # cleaned_data['username']返回的是一个对象。
        user_obj = form.cleaned_data['username']
        # 准备在session中保存用户对象，以判断用户是否是登录状态
        request.session['user_id'] = user_obj.id
        request.session['user_name'] = user_obj.username
        # 跳转用的是路由名，不是url
        return redirect('web007:index')
    else:
        return render(request, 'web007/login.html', {'form': form})


# 退出登录
def logout(request):
    request.session.flush()
    return redirect('web007:index')


# 图片验证码
def image_code(request):
    from utils import image_code
    from io import BytesIO
    import uuid
    from django_redis import get_redis_connection
    # 获取图片验证码和验证码图片对象
    image_obj, code = image_code.check_code()
    # 保存图片验证码到redis中
    user_uuid = str(uuid.uuid4())
    redis_conn = get_redis_connection('default')
    #  以uuid为key，验证码为value
    redis_conn.set(user_uuid, code,ex=60)
    # 以user_uuid为key,uuid为value
    redis_conn.set('user_uuid', user_uuid,ex=60)
    # 将图片文件写入内存中
    stream = BytesIO()
    image_obj.save(stream, format='PNG')
    return HttpResponse(stream.getvalue(), content_type='image/png')
