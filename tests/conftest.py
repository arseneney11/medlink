import pytest

from apps.facilities.models import Facility

PASSWORD = "a-long-password-1"


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username="nurse1", password=PASSWORD)


@pytest.fixture
def kigali():
    return Facility.objects.create(name="Kigali Clinic", code="kigali")


@pytest.fixture
def huye():
    return Facility.objects.create(name="Huye Hospital", code="huye")