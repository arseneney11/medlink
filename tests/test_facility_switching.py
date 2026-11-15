import pytest
from django.urls import reverse

from apps.facilities.models import FacilityMembership

pytestmark = pytest.mark.django_db


def test_a_single_facility_is_selected_automatically(client, user, kigali):
    FacilityMembership.objects.create(user=user, facility=kigali)
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert response.wsgi_request.facility == kigali
    assert b"Kigali Clinic" in response.content


def test_user_without_a_facility_sees_a_clear_message(client, user):
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert response.wsgi_request.facility is None
    assert b"not linked to a facility" in response.content


def test_user_with_two_facilities_must_choose(client, user, kigali, huye):
    FacilityMembership.objects.create(user=user, facility=kigali)
    FacilityMembership.objects.create(user=user, facility=huye)
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert response.wsgi_request.facility is None
    assert b"Switch facility" in response.content


def test_user_can_switch_to_a_facility_they_belong_to(client, user, kigali, huye):
    FacilityMembership.objects.create(user=user, facility=kigali)
    FacilityMembership.objects.create(user=user, facility=huye)
    client.force_login(user)
    response = client.post(reverse("facilities:switch"), {"facility": str(huye.pk)})
    assert response.status_code == 302
    assert client.get(reverse("core:home")).wsgi_request.facility == huye


def test_user_cannot_switch_to_a_facility_without_access(client, user, kigali, huye):
    FacilityMembership.objects.create(user=user, facility=kigali)
    client.force_login(user)
    response = client.post(reverse("facilities:switch"), {"facility": str(huye.pk)})
    assert response.status_code == 403
    assert client.get(reverse("core:home")).wsgi_request.facility == kigali