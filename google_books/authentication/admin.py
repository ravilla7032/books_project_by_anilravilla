from django.contrib import admin
from . import models

class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "mobile_number", "email", "username", "first_name", "last_name", "is_active"
    )
    fields = ("password", "mobile_number", "email", "username", "first_name", "last_name", "age", "date_joined", "is_admin", "is_active", "is_superuser", "is_staff", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at","date_joined")

class UserProfile(admin.ModelAdmin):
    list_display = (
        "id", "user", "security_code", "security_code_validated_upto", "verified"
    )
    fields = ("user", "bio", "gender", "last_login", "otp", "security_code", "security_code_validated_upto", "verified", "address","forgot_password_token", "created_at", "updated_at")
    readonly_fields = ("created_at","updated_at","last_login")

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Profile, UserProfile)
