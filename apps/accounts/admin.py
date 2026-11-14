from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MedlinkUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "job_title", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Staff details", {"fields": ("phone", "employee_number", "job_title")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Staff details", {"fields": ("first_name", "last_name", "phone", "employee_number", "job_title")}),
    )