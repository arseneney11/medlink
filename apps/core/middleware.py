from .current_user import reset_current_user, set_current_user


class CurrentUserMiddleware:
    """Makes the signed-in user available to models during each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = set_current_user(getattr(request, "user", None))
        try:
            return self.get_response(request)
        finally:
            reset_current_user(token)