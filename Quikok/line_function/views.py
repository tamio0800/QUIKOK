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


line_bot_api = LineBotApi('12Mo2EzQJYqUhhL1feBf0KKzzTrnoDJe0iBU5JzdTHQabuMEiOtJY27TaZHOff36Hw0TGGjvQt1PQQDHQ1GoED1k3zhy5oGc0ZLmhoBDHNvbLmMKhuB2czzzdvA9y//MxJbyiaPo5THU8wt1fzoMjQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c51ff7c4fe9be02993a68aab624111a2')


#設定
@csrf_exempt
def callback(request):
    #test =request.Post.getlist()
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        print(signature)
        body = request.body.decode()
        print(body)
        try: # 目前這個寫法若user傳圖片會報錯
            handler.handle(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
#        for event in events:
#            if isinstance(event, MessageEvent):  # 如果有訊息事件
#                line_bot_api.reply_message(  # 回復傳入的訊息文字
#                    event.reply_token,
#                    TextSendMessage(text=event.message.text)
#                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

#當收到訊息
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print(event)
    user_id = event.source.user_id
    print("user_id =", user_id)

    try:
        #if account.objects.filter(verify = event.message.text).exists():
        #    account.objects.filter(verify = event.message.text).update(userid=event.source.user_id)
            #username=account.objects.filter(verify = event.message.text)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='success\nhello '))
        #else :
        #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='驗證碼過期'))

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

