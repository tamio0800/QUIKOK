from django.contrib import admin
from analytics.models import object_accessed_info
# Register your models here.

class ObjectAccessedAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id',
        'auth_id',
        'ip_address',
        'url_path',
        'api_name',
        'model_name',
        'object_name',
        'object_id',
        'action_type',
        'timestamp'
        )

admin.site.register(object_accessed_info, ObjectAccessedAdmin)