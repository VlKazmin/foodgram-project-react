from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
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


@admin.register(Subscription)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "author")
    search_fields = ("follower",)
    list_filter = ("follower", "author")
    ordering = ("follower",)
    empty_value_display = "-пусто-"
