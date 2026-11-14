import uuid

import pytest
from django.urls import reverse

PASSWORD = "a-long-password-1"


@pytest.mark.django_db
def test_user_has_uuid_key_and_timestamps(django_user_model):
    user = django_user_model.objects.create_user(username="doctor1", password=PASSWORD)
    assert isinstance(user.pk, uuid.UUID)
    assert user.created_at is not None


@pytest.mark.django_db
def test_login_with_correct_password(client, django_user_model):
    django_user_model.objects.create_user(username="doctor1", password=PASSWORD)
    response = client.post(reverse("accounts:login"), {"username": "doctor1", "password": PASSWORD})
    assert response.status_code == 302
    assert response.url == reverse("core:home")


@pytest.mark.django_db
def test_login_with_wrong_password_stays_on_page(client, django_user_model):
    django_user_model.objects.create_user(username="doctor1", password=PASSWORD)
    response = client.post(reverse("accounts:login"), {"username": "doctor1", "password": "wrong"})
    assert response.status_code == 200
    assert b"Wrong username or password" in response.content


@pytest.mark.django_db
def test_deactivated_user_cannot_sign_in(client, django_user_model):
    django_user_model.objects.create_user(username="left1", password=PASSWORD, is_active=False)
    response = client.post(reverse("accounts:login"), {"username": "left1", "password": PASSWORD})
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_ends_the_session(client, django_user_model):
    user = django_user_model.objects.create_user(username="doctor1", password=PASSWORD)
    client.force_login(user)
    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert client.get(reverse("core:home")).status_code == 302