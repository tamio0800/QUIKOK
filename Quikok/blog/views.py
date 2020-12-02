from django.shortcuts import render, HttpResponse

# Create your views here.
def hello_blog(request):
    return HttpResponse('hello blog')