from datetime import timedelta
from django.contrib import admin
from .models import UserProfile, Club, ClubUser, UserMessage


# Register your models here.
class AdminUserProfile(admin.ModelAdmin):
    list_display = ('username','get_utc','is_verified')
    search_fields = ('user',)
    list_filter = ('user', 'is_verified',)
    empty_value_display = '-empty field-'

    def username(self, obj):
        return obj.user.username

    def get_utc(self, obj):
        return obj.user.date_joined + timedelta(minutes=330)

    get_utc.short_description = 'Created (UTC)'


class AdminClub(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-empty field-'


class AdminUserMessage(admin.ModelAdmin):
    search_fields = ('body',)
    list_filter = ('body',)
    empty_value_display = '-empty field-'


admin.site.register(UserProfile, AdminUserProfile)
admin.site.register(Club, AdminClub)
admin.site.register(ClubUser)
admin.site.register(UserMessage, AdminUserMessage)
