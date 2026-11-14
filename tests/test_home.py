from django.urls import reverse


def test_home_page_renders(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    assert b"Medlink is running." in response.content