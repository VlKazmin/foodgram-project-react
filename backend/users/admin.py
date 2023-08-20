from django.contrib import admin

from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
    )
    search_fields = ("username",)
    list_filter = ("username", "email")
    ordering = ("username",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "author")
    search_fields = ("follower",)
    list_filter = ("follower", "author")
    ordering = ("follower",)
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, FollowAdmin)
