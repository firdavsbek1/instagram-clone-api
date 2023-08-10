from django.contrib import admin
from .models import User,UserConfirmation


class UserModelAdmin(admin.ModelAdmin):
    list_display = ['username','email','phone_number','auth_type']


class UserConfirmModelAdmin(admin.ModelAdmin):
    list_display = ['id','owner','expiration_time']


admin.site.register(User,UserModelAdmin)
admin.site.register(UserConfirmation,UserConfirmModelAdmin)