from django.contrib import admin
from .models import RequestEnroll
# Register your models here.


class RequestEnrollAdmin(admin.ModelAdmin):
    list_display = ['course_id','enrollment_status','student']
admin.site.register(RequestEnroll,RequestEnrollAdmin)