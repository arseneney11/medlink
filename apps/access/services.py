from .models import Permission, Role
from .registry import DEFAULT_ROLES, PERMISSIONS


def sync_permissions():
    """Make the Permission table match registry.py exactly."""
    existing = {p.code: p for p in Permission.objects.all()}
    for code, label, module, action in PERMISSIONS:
        permission = existing.pop(code, None)
        if permission is None:
            Permission.objects.create(code=code, label=label, module=module, action=action)
        elif (permission.label, permission.module, permission.action) != (label, module, action):
            permission.label, permission.module, permission.action = label, module, action
            permission.save()
    if existing:  # codes that were removed from the registry
        Permission.objects.filter(code__in=existing).delete()


def create_default_roles(facility):
    """Give a facility the default roles. Roles that already exist are left exactly as they are,
    so a hospital's own edits are never overwritten."""
    permissions = {p.code: p for p in Permission.objects.all()}
    created = []
    for code, name, description, codes in DEFAULT_ROLES:
        role, was_created = Role.objects.get_or_create(
            facility=facility, code=code, defaults={"name": name, "description": description}
        )
        if was_created:
            role.permissions.set([permissions[c] for c in codes])
            created.append(role)
    return created