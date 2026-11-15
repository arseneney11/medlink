from functools import cached_property, wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from apps.facilities.models import FacilityMembership

from .models import Permission, Role
from .registry import ALL_CODES


class PermissionSet:
    """What one user may do in one facility. Loaded from the database only when first used."""

    def __init__(self, user, facility):
        self.user = user
        self.facility = facility

    @cached_property
    def membership(self):
        if self.user is None or not self.user.is_authenticated or self.facility is None:
            return None
        return (
            FacilityMembership.objects.current()
            .filter(user=self.user, facility=self.facility, facility__is_active=True)
            .first()
        )

    @cached_property
    def codes(self):
        if self.membership is None:
            return frozenset()
        return frozenset(
            Permission.objects.filter(
                roles__is_active=True,
                roles__facility=self.facility,
                roles__assignments__membership=self.membership,
            ).values_list("code", flat=True)
        )

    @cached_property
    def role_names(self):
        if self.membership is None:
            return []
        return list(
            Role.objects.filter(
                is_active=True, facility=self.facility, assignments__membership=self.membership
            ).values_list("name", flat=True)
        )

    def __contains__(self, code):
        return code in self.codes


def require_permission(code):
    """Protect a view: sign-in is required, and the user must hold this permission in their
    current facility. A mistyped code fails immediately when the view is defined."""
    if code not in ALL_CODES:
        raise ImproperlyConfigured(f"Unknown permission code: {code!r}")

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if code not in request.permissions:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator