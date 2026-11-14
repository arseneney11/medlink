import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_reports_ok(client):
    response = client.get(reverse("core:health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
