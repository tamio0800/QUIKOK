from django.contrib import admin
from blog.models import article_info, author_profile

# Register your models here.
admin.site.register(article_info)
admin.site.register(author_profile)

