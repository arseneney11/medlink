from .permissions import PermissionSet


class PermissionsMiddleware:
    """Adds request.permissions for the current user and facility."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.permissions = PermissionSet(getattr(request, "user", None), getattr(request, "facility", None))
        return self.get_response(request)