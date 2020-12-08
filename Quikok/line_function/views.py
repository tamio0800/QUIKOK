from django.shortcuts import redirect, render
from django.http import FileResponse
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import random
from .models import account
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FollowEvent


line_bot_api = LineBotApi('KrLaJm+6juX+LOjbIdZPhVmANzc1gaBT7LAQERHLUygzV1Wrj8nWwKX7U7vf+9ACiT+oai2fwps5oiVv4DzZj8HMHnRtpaL+9AKfbvhzd8TzC2RY+iv0b3d5LXZZe//4m5ccb6mGKyJoNRbvQMRqbwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ee6b6c9d1c72714d0b86dd5fcd34bce5')


#設定
@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode()

        try:
            handler.handle(body, signature)
        except InvalidSignatureError as e:
            print(e)
            return HttpResponseForbidden()
        except LineBotApiError as e:
            print(e)
            return HttpResponseBadRequest()

        return HttpResponse("OK")
    else:
        return HttpResponseBadRequest()

#當收到訊息
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print(event)
    user_id = event.source.user_id
    print("user_id =", user_id)

    try:
        if account.objects.filter(verify = event.message.text).exists():
            account.objects.filter(verify = event.message.text).update(userid=event.source.user_id)
            #username=account.objects.filter(verify = event.message.text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='success\nhello '))
        else :
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='驗證碼過期'))

    except LineBotApiError as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error.message)
        print(e.error.details)

#當被加為好友
@handler.add(FollowEvent)
def follow(event):
    print(event)
    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入驗證碼'))

    except LineBotApiError as e:
        print(e.status_code)
        print(e.request_id)
        print(e.error.message)
        print(e.error.details)


#上傳圖片
def upload_file(file):
    path_base=os.getcwd()
    picture_path=os.path.join(path_base,'img',file)
    img = open(picture_path, 'rb')
    response = FileResponse(img)
    return response

