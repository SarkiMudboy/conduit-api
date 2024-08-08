from django.contrib import admin

from .models import Bucket, Drive, Object

# Register your models here.
admin.site.register(Drive)
admin.site.register(Object)
admin.site.register(Bucket)
