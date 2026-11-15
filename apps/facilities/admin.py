from django.contrib import admin

from .models import Department, Facility, FacilityMembership


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "facility_type", "district", "is_active")
    list_filter = ("facility_type", "is_active")
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "facility", "is_clinical", "is_active")
    list_filter = ("facility", "is_clinical", "is_active")
    search_fields = ("name", "code")


@admin.register(FacilityMembership)
class FacilityMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "department", "starts_on", "ends_on", "is_active")
    list_filter = ("facility", "is_active")
    autocomplete_fields = ("user",)