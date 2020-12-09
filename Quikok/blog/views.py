from django.shortcuts import render, HttpResponse
from django.template import Template, Context
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile
from .models import article_info,author_profile
# Create your views here.
def hello_blog(request):
    #return HttpResponse('hello blog')
    return render(
        request,
        'blog/articles_list.html',
        {
            'article_time' : '2011.11.11',
            'article_author' : 'Tam',
            'article_title' : '英國文化大臣稱劇集《王冠》應標明情節虛構',
            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評第四季招致了一些批評第四季招致了一些批評第四季招致了一些批評第四季招致了一些批評第四季招致了一些批評',
            'article_category' : '教育現場',
        })


def second_blog(request):
    return render(
        request,
        'blog/articles.html',
        {
            'article_time' : '2011.11.11',
            'article_author' : 'Tam',
            'article_title' : '英國文化大臣稱劇集《王冠》應標明情節虛構',
            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評',
            'article_category' : '教育現場',
            'article_hashtag' : '新鮮人職場必備',
            'article_author_introduction' : '台灣韓國情報站創辦人，先後任職美國國會山莊遊說團體、無國界記者組織，現為獨立記者、公共外交說客。'
        })

def aritcle_content(request, article_id):
    the_article = article_info.objects.filter(id = article_id).first()
    print(the_article.author_id)
    author_nickname = teacher_profile.objects.filter(auth_id=50).first().nickname
    article_title = the_article.title
    return render(
        request,
        'blog/articles.html',
        {
            'article_time' : '2011.11.11',
            'article_author' : author_nickname,
            'article_title' : article_title,
            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評...',
            'article_group' : '教育現場',
            'article_hashtag' : '新鮮人職場必備',
            'article_author_introduction' : '台灣韓國情報站創辦人，先後任職美國國會山莊遊說團體、無國界記者組織，現為獨立記者、公共外交說客。'
        })

def article_editor(request):
    # 這個函式用來回傳blog中文章的編輯器
    if request.method == 'POST':
        print(request.POST.get('textarea', False))

    return render(request, 'blog/article_editor.html')