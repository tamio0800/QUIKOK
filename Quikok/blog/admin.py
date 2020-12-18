from django.contrib import admin
from blog.models import article_info, author_profile, uploaded_pictures

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(article_info, BlogAdmin)
admin.site.register(author_profile, BlogAdmin)
admin.site.register(uploaded_pictures, BlogAdmin)


