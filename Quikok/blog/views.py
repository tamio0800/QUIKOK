from django.shortcuts import render, HttpResponse, redirect
from django.template import Template, Context
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile
from blog.models import article_info ,author_profile, uploaded_pictures
from datetime import datetime
import re

def _get_all_categories_for_blog(excluded=['Mail',]):
    '''
    用以回傳除了某些特定類別以外的，資料庫中的文章的所有類別。
    '''
    all_unique_categories = \
        list(article_info.objects.values_list('category', flat=True).distinct())
    return [_ for _ in all_unique_categories if _ not in excluded]

# Create your views here.
def main_blog(request):
    
    all_unique_categories = _get_all_categories_for_blog()
    the_articles = article_info.objects.filter(category__in=all_unique_categories)
    the_one_big_picture = uploaded_pictures.objects.filter(special_tag='blog_s_main_picture').first()
    #print(the_one_big_picture)
    #print(str(the_one_big_picture.picture.url))

    articles_in_list = list()
    # 將文章應該有的資訊再度整合成一個物件（字典形式）
    if len(the_articles) > 0:
        for each_article_object in the_articles:
            articles = dict()
            correspondent_author_object = \
                author_profile.objects.filter(id=each_article_object.author_id).first()
            articles['date'] = str(each_article_object.created_time).split()[0].replace('-', '.')
            articles['id'] = each_article_object.id
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
                'articles_in_list': articles_in_list,
                'all_unique_categories': all_unique_categories,
                'the_one_big_picture': the_one_big_picture
            })

    return render(request, 'blog/articles_list.html',
            {
                'the_one_big_picture': the_one_big_picture
            })
    

def aritcle_content(request, article_id):
    
    the_article = article_info.objects.filter(id = article_id).first()
    if the_article is None:
        # 萬一找不到該文章的id，直接回到blog首頁。
        return redirect('main_blog')
    
    author_object = author_profile.objects.filter(id=the_article.author_id).first()
    author_nickname = author_object.name
    author_intro = author_object.intro
    author_thumbnail = author_object.thumbnail
    article_title = the_article.title
    article_date = str(the_article.last_edited_time).split()[0].replace('-', '.')
    article_main_picture = the_article.main_picture
    article_content = the_article.content
    article_category = the_article.category
    article_hashtags = [_ for _ in re.sub(r'[,#;]', ' ', the_article.hashtag).split() if len(_) > 0]

    the_articles = article_info.objects.all()
    all_unique_categories = _get_all_categories_for_blog()
    
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
            'article_hashtags' : article_hashtags,
            'article_author_introduction' : author_intro,

            'all_unique_categories': all_unique_categories,
            'the_articles': the_articles,
        })


def article_editor(request):
    # 這個函式用來回傳blog中文章的編輯器
    if request.method == 'POST':
        title = request.POST.get('title', False)
        textarea = request.POST.get('textarea', False)
        author_id = request.POST.get('author_id', False)
        category = request.POST.get('category', False)
        hashtag = request.POST.get('hashtag', False)
        if False not in [title, textarea, category, author_id, hashtag]:
            
            new_article = article_info.objects.create(
                author_id = author_id,
                title = title,
                content = textarea,
                category = category,
                hashtag = hashtag)
            new_article.save()
            
            return HttpResponse('已經成功匯入資料庫')
        else:
            return render(request, 'blog/article_editor.html', 
            {
              'title': title,
              'textarea': textarea,
              'author_id': author_id,
              'category': category,
              'hashtag': hashtag
            })
        
    return render(request, 'blog/article_editor.html')