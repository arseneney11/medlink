from django.contrib import admin

from .models import MembershipRole, Permission, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "facility", "is_active")
    list_filter = ("facility", "is_active")
    search_fields = ("name", "code")
    filter_horizontal = ("permissions",)


@admin.register(MembershipRole)
class MembershipRoleAdmin(admin.ModelAdmin):
    list_display = ("membership", "role", "created_at", "created_by")
    list_filter = ("role__facility",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "label")
    list_filter = ("module",)
    search_fields = ("code", "label")

    # Permissions come from registry.py, so the admin only lets you look at them.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False