from django.shortcuts import render,redirect
from django.http import HttpResponse
from web007 import models
from django_redis import get_redis_connection
from datetime import datetime,timedelta
import json
from utils.data_encrypt import uid
from web007.ali_pay import alipay

def index(request):
    return render(request, 'web007/index.html')

# 价格展示页面
def price(request):
    policy_list = models.ProjectStrategy.objects.filter(project_type=1)
    return render(request, 'web007/price.html', {'policy_list': policy_list})


# 付款页面
def payment(request, policy_id):
    # 根据policy_id获取策略对象
    policy_obj = models.ProjectStrategy.objects.get(id=policy_id, project_type=1)
    # 如果没则跳回价格页面
    if not policy_obj:
        return redirect('web007:price')
    # 获取购买数量，并计算价格，如果购买数量不存在，则跳回价格页面，如果购买数字不是数字或者小于1，则跳回价格页面
    number = request.GET.get('number')
    if not number:
        return redirect('web007:price')
    if not number.isdecimal():
        return redirect('web007:price')
    number = int(number)
    if number < 1:
        return redirect('web007:price')
    # 计算价格
    total_money = policy_obj.project_price * number

    # 判断用户之前是否购买过付费服务，如果购买过，则计算其剩余时间的单日价格，乘以他的剩余天数，用总价格减去，得到剩余金额是付费费用
    balance = 0  # 剩余金额
    user_order_obj = None  # 用户上次购买订单对象
    if request.tracer.price_strategy.project_type == 1:
        # 获取用户上次最近一次的购买订单对象
        user_order_obj = models.Order.objects.filter(user=request.tracer.user,order_status=True).order_by('-id').first()
        # 获取用户购买订单的总时间和剩余时间
        total_time = (user_order_obj.order_end_time - user_order_obj.order_pay_time).days
        balance_time = (user_order_obj.order_end_time - datetime.now()).days
        # 如果当天买了就更改套餐则扣掉一天的钱
        if total_time == balance_time:
            balance = user_order_obj.project_strategy.project_price * user_order_obj.order_year/total_time*(balance_time-1)
        else:
            balance = user_order_obj.project_strategy.project_price * user_order_obj.order_year/total_time*(balance_time)
        # 如果买的套餐价格比之前的高则余额是大于这次总价的，则直接跳回价格展示页面
        if balance > total_money:
            return redirect('web007:price')
    # 将订单构造成字典，并返回给前端
    context = {
        'policy_id': policy_obj.id,
        'number': number,
        'origin_price': total_money,
        'balance': round(balance, 2),
        'total_price': round((total_money - round(balance, 2)),2)
    }
    # 将构造的信息写入redis中，设置过期时间30分钟，如果30分钟内没有支付，则订单失效
    conn = get_redis_connection('default')
    key = request.tracer.user.mobile_phone
    conn.set(key, json.dumps(context),ex=1800)
    # 将策略对象和订单对象返回给前端
    context['policy_object'] = policy_obj
    context['transaction'] = user_order_obj
    return render(request, 'web007/payment.html', context)


#  支付宝支付以及返回
def pay(request):
    conn = get_redis_connection('default')
    value = conn.get(request.tracer.user.mobile_phone)
    if not value:
        return redirect('web007:price')
    content = json.loads(value.decode('utf-8'))
    #  订单号
    order_id = uid(request.tracer.user.mobile_phone)
    total_price = content['total_price']
    models.Order.objects.create(
        order_number=order_id,
        order_status=True,
        user=request.tracer.user,
        project_strategy_id=content['policy_id'],
        order_price=total_price,
        order_year=content['number'],
        order_pay_time=datetime.now(),
        order_end_time=datetime.now()+timedelta(days=content['number']*365),
    )
    # 支付宝支付
    response = alipay.pay(order_id, total_price, '购买项目')
    return redirect(response)

def pay_return(request):
    # 获取支付宝返回的参数
    params = request.GET.dict()
    print(params)
    return HttpResponse('支付成功')


