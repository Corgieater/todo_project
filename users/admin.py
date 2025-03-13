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
        ("Personal Info", {"fields": ("name",)}),
        (
            "Permissions",
            {"fields": ("is_superuser", "is_staff", "groups", "user_permissions")},
        ),
        ("Important Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("last_login",)
    search_fields = (
        "email",
        "name",
    )
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
