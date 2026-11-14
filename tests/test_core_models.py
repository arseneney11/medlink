import pytest

from apps.core.current_user import get_current_user, reset_current_user, set_current_user
from apps.core.exceptions import HardDeleteNotAllowed
from apps.core.models import (
    BaseModel,
    ProtectedModel,
    ProtectedQuerySet,
    TimestampedModel,
    UUIDModel,
)


class FakeUser:
    def __init__(self, authenticated=True):
        self.is_authenticated = authenticated


def test_core_models_are_abstract():
    for model in (UUIDModel, TimestampedModel, BaseModel, ProtectedModel):
        assert model._meta.abstract


def test_protected_model_has_audit_and_void_fields():
    names = {field.name for field in ProtectedModel._meta.local_fields}
    expected = {
        "id", "created_at", "updated_at", "created_by", "updated_by",
        "voided_at", "voided_by", "void_reason",
    }
    assert expected <= names


def test_hard_delete_is_blocked_on_records_and_querysets():
    with pytest.raises(HardDeleteNotAllowed):
        ProtectedModel.delete(object())
    with pytest.raises(HardDeleteNotAllowed):
        ProtectedQuerySet.delete(object())


def test_no_current_user_by_default():
    assert get_current_user() is None


def test_current_user_is_set_and_cleared():
    user = FakeUser()
    token = set_current_user(user)
    assert get_current_user() is user
    reset_current_user(token)
    assert get_current_user() is None


def test_anonymous_user_is_ignored():
    token = set_current_user(FakeUser(authenticated=False))
    assert get_current_user() is None
    reset_current_user(token)