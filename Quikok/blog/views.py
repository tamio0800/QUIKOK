from django.shortcuts import render, HttpResponse, redirect
from django.template import Template, Context
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile
from .models import article_info ,author_profile
from datetime import datetime

# Create your views here.
def main_blog(request):
    the_articles = article_info.objects.all()

    articles_in_list = list()
    
    # 將文章應該有的資訊再度整合成一個物件（字典形式）
    for each_article_object in the_articles:
        articles = dict()
        correspondent_author_object = \
            author_profile.objects.filter(id=each_article_object.author_id).first()
        articles['date'] = str(each_article_object.created_time).split()[0].replace('-', '.')
        articles['category'] = each_article_object.category
        articles['hashtag'] = each_article_object.hashtag
        articles['main_picture'] = each_article_object.main_picture
        articles['author'] = correspondent_author_object
        articles['title'] = each_article_object.title
        articles['snippet'] = each_article_object.snippet
        print(f'articles[\'snippet\']:  {each_article_object.snippet}')
        articles_in_list.append(articles)

    return render(
        request,
        'blog/articles_list.html',
        {
            'articles_in_list': articles_in_list
        })

'''
'article_date' : article_date,
'article_main_picture': article_main_picture,
'article_author' : author_nickname,
'article_title' : article_title,
'article_snippet' : article_snippet,
'article_category' : article_category,
'''
#def second_blog(request):
#    return render(
#        request,
#        'blog/articles.html',
#        {
#            'article_time' : '2011.11.11',
#            'article_author' : 'Tam',
#            'article_title' : '英國文化大臣稱劇集《王冠》應標明情節虛構',
#            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評',
#            'article_category' : '教育現場',
#            'article_hashtag' : '新鮮人職場必備',
#            'article_author_introduction' : '台灣韓國情報站創辦人，先後任職美國國會山莊遊說團體、無國界記者組織，現為獨立記者、公共外交說客。'
#        })

def aritcle_content(request, article_id):
    the_article = article_info.objects.filter(id = article_id).first()
    if the_article is None:
        # 萬一找不到該文章的id，直接回到blog首頁。
        return redirect('main_blog')
    # print(the_article.author_id)
    author_object = author_profile.objects.filter(id=the_article.author_id).first()
    author_nickname = author_object.name
    author_intro = author_object.intro
    author_thumbnail = author_object.thumbnail
    article_title = the_article.title
    article_date = str(the_article.last_edited_time).split()[0].replace('-', '.')
    article_main_picture = the_article.main_picture
    article_content = the_article.content
    article_category = the_article.category
    article_hashtag = the_article.hashtag
    return render(
        request,
        'blog/articles.html',
        {
            'article_date' : article_date,
            'article_main_picture': article_main_picture,
            'article_author' : author_nickname,
            'article_title' : article_title,
            'author_thumbnail': author_thumbnail,
            'article_content' : article_content,
            'article_category' : article_category,
            'article_hashtag' : article_hashtag,
            'article_author_introduction' : author_intro,
        })

def article_editor(request):
    # 這個函式用來回傳blog中文章的編輯器
    if request.method == 'POST':
        print(request.POST.get('textarea', False))

    return render(request, 'blog/article_editor.html')