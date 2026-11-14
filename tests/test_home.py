import pytest
from django.urls import reverse


def test_home_redirects_anonymous_users_to_login(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_home_renders_for_signed_in_users(client, django_user_model):
    user = django_user_model.objects.create_user(username="nurse1", password="a-long-password-1")
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    assert b"Medlink is running." in response.content