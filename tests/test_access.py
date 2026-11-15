from datetime import timedelta
from io import StringIO

import pytest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from apps.access.models import MembershipRole, Permission, Role
from apps.access.permissions import PermissionSet, require_permission
from apps.access.registry import ALL_CODES, DEFAULT_ROLES
from apps.access.services import create_default_roles
from apps.facilities.models import FacilityMembership

pytestmark = pytest.mark.django_db


def assign(user, facility, *role_codes):
    membership, _ = FacilityMembership.objects.get_or_create(user=user, facility=facility)
    for code in role_codes:
        role = Role.objects.get(facility=facility, code=code)
        MembershipRole.objects.create(membership=membership, role=role)
    return membership


def codes_of(facility, role_code):
    return set(Role.objects.get(facility=facility, code=role_code).permissions.values_list("code", flat=True))


# --- the vocabulary and the defaults -------------------------------------------------

def test_permission_table_matches_the_registry():
    assert set(Permission.objects.values_list("code", flat=True)) == set(ALL_CODES)


def test_every_default_role_uses_known_permissions():
    for code, _name, _description, codes in DEFAULT_ROLES:
        assert set(codes) <= ALL_CODES, code


def test_a_new_facility_gets_the_default_roles(kigali):
    assert Role.objects.filter(facility=kigali).count() == len(DEFAULT_ROLES)


def test_default_roles_never_overwrite_a_hospitals_edits(kigali):
    doctor = Role.objects.get(facility=kigali, code="doctor")
    doctor.permissions.remove(Permission.objects.get(code="clinical.sign"))
    create_default_roles(kigali)
    assert Role.objects.filter(facility=kigali).count() == len(DEFAULT_ROLES)
    assert not doctor.permissions.filter(code="clinical.sign").exists()


# --- giving roles to people (Module 21 §21.6) ----------------------------------------

def test_a_role_can_only_be_given_inside_its_own_facility(user, kigali, huye):
    membership = FacilityMembership.objects.create(user=user, facility=kigali)
    with pytest.raises(ValidationError):
        MembershipRole.objects.create(membership=membership, role=Role.objects.get(facility=huye, code="doctor"))


def test_user_gets_permissions_from_their_roles(user, kigali):
    assign(user, kigali, "doctor")
    permissions = PermissionSet(user, kigali)
    assert "clinical.sign" in permissions
    assert "billing.void" not in permissions


def test_several_roles_add_up(user, kigali):
    assign(user, kigali, "doctor", "receptionist")
    permissions = PermissionSet(user, kigali)
    assert "clinical.sign" in permissions
    assert "patients.create" in permissions


def test_permissions_do_not_carry_over_to_another_facility(user, kigali, huye):
    assign(user, kigali, "doctor")
    assert "clinical.sign" in PermissionSet(user, kigali)
    assert "clinical.sign" not in PermissionSet(user, huye)


def test_an_ended_membership_removes_permissions(user, kigali):
    today = timezone.localdate()
    membership = FacilityMembership.objects.create(
        user=user, facility=kigali, starts_on=today - timedelta(days=60), ends_on=today - timedelta(days=1)
    )
    MembershipRole.objects.create(membership=membership, role=Role.objects.get(facility=kigali, code="doctor"))
    assert "clinical.view" not in PermissionSet(user, kigali)


def test_a_switched_off_role_grants_nothing(user, kigali):
    assign(user, kigali, "doctor")
    Role.objects.filter(facility=kigali, code="doctor").update(is_active=False)
    assert "clinical.view" not in PermissionSet(user, kigali)


# --- rules written in the guidebook --------------------------------------------------

def test_doctor_cannot_void_invoices(kigali):  # Module 1 §3.16
    assert "billing.void" not in codes_of(kigali, "doctor")


def test_nurse_cannot_sign_or_edit_clinical_notes(kigali):  # Module 21 §21.7
    codes = codes_of(kigali, "nurse")
    assert "clinical.sign" not in codes
    assert "clinical.edit" not in codes


def test_accountant_cannot_read_clinical_notes(kigali):  # Module 21 §21.7
    assert "clinical.view" not in codes_of(kigali, "accountant")


def test_system_administrator_has_no_clinical_access_by_default(kigali):  # Module 21 §21.2
    clinical = {"patients", "clinical", "prescriptions", "laboratory", "imaging"}
    assert not {c for c in codes_of(kigali, "system_admin") if c.split(".")[0] in clinical}


def test_auditor_can_only_view(kigali):  # Module 21 §21.2
    assert {c.split(".")[1] for c in codes_of(kigali, "auditor")} == {"view"}


# --- enforcing permissions in views --------------------------------------------------

def test_require_permission_blocks_then_allows(rf, user, kigali):
    @require_permission("clinical.view")
    def view(request):
        return HttpResponse("ok")

    request = rf.get("/")
    request.user = user
    request.permissions = PermissionSet(user, kigali)
    with pytest.raises(PermissionDenied):
        view(request)

    assign(user, kigali, "doctor")
    request.permissions = PermissionSet(user, kigali)
    assert view(request).status_code == 200


def test_unknown_permission_codes_are_rejected_when_the_view_is_defined():
    with pytest.raises(ImproperlyConfigured):
        require_permission("patient.view")


def test_request_carries_the_users_permissions(client, user, kigali):
    assign(user, kigali, "receptionist")
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert "patients.create" in response.wsgi_request.permissions
    assert b"Receptionist" in response.content


def test_no_facility_means_no_permissions(client, user):
    client.force_login(user)
    response = client.get(reverse("core:home"))
    assert "patients.view" not in response.wsgi_request.permissions


# --- the setup command ---------------------------------------------------------------

def test_setup_roles_gives_roles_to_a_user(user):
    call_command("seed_demo_facility", stdout=StringIO())
    call_command("setup_roles", facility="nyarugenge", user="nurse1", roles="doctor,receptionist", stdout=StringIO())
    assert MembershipRole.objects.filter(membership__user=user).count() == 2


def test_setup_roles_rejects_unknown_role_codes(user):
    call_command("seed_demo_facility", stdout=StringIO())
    with pytest.raises(CommandError):
        call_command("setup_roles", facility="nyarugenge", user="nurse1", roles="wizard", stdout=StringIO())