#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import traceback
from BugManagePlatform import settings
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.response.AlipayTradeCreateResponse import AlipayTradeCreateResponse
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a',)
logger = logging.getLogger('')
def pay(order_id, price, subject):
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
    alipay_client_config.app_id = "9021000139678164"
    alipay_client_config.app_private_key = '请填写开发者私钥去头去尾去回车，单行字符串'
    alipay_client_config.alipay_public_key = '请填写支付宝公钥，单行字符串'
    BASE_DIR = settings.BASE_DIR
    with open(f'{BASE_DIR}\\alipay_password\\支付宝私钥.txt', 'r') as f:
        alipay_client_config.app_private_key = f.read()
    with open(f'{BASE_DIR}\\alipay_password\\支付宝公钥.txt', 'r') as f:
        alipay_client_config.alipay_public_key = f.read()
    client = DefaultAlipayClient(alipay_client_config, logger)
    # 构造请求参数对象
    model = AlipayTradePagePayModel()
    model.out_trade_no = order_id
    model.total_amount = price
    model.subject = subject
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    request = AlipayTradePagePayRequest(biz_model=model)
    request.notify_url = 'http://127.0.0.1:8000/pay-return/'
    request.return_url = 'http://127.0.0.1:8000/pay-return/'
    # 执行API调用
    response = client.page_execute(request, http_method="GET")
    return response