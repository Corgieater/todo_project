from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "email",
        "name",
        "is_superuser",
    )
    list_filter = ("is_superuser",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Name", {"fields": ("name",)}),
        ("Last Login", {"fields": ("last_login",)}),
    )
    readonly_fields = (
        "email",
        "name",
        "last_login",
    )
    search_fields = (
        "email",
        "name",
    )
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
