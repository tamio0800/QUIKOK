from django.shortcuts import render, HttpResponse
from django.template import Template, Context

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
            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評...',
            'article_group' : '教育現場',
        })


def second_blog(request):
    return render(
        request,
        'blog/articles.html',
        {
            'article_time' : '2011.11.11',
            'article_author' : 'Tam',
            'article_title' : '英國文化大臣稱劇集《王冠》應標明情節虛構',
            'article_content' : '因為劇中對一些王室事件，尤其是對威爾士親王夫婦婚姻破裂的刻畫，由英國演員奧利維婭曼扮演女王的《王冠》第四季招致了一些批評...',
            'article_group' : '教育現場',
            'article_hastage' : '新鮮人職場必備',
            'article_author_introduction' : '台灣韓國情報站創辦人，先後任職美國國會山莊遊說團體、無國界記者組織，現為獨立記者、公共外交說客。'
        })