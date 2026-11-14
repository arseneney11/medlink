from contextvars import ContextVar

_current_user = ContextVar("current_user", default=None)


def get_current_user():
    """Return the signed-in user of the current request, or None."""
    user = _current_user.get()
    if user is not None and user.is_authenticated:
        return user
    return None


def set_current_user(user):
    return _current_user.set(user)


def reset_current_user(token):
    _current_user.reset(token)