from datetime import timedelta
from io import StringIO

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.utils import timezone

from apps.core.current_user import reset_current_user, set_current_user
from apps.facilities.management.commands.seed_demo_facility import DEPARTMENTS
from apps.facilities.models import Department, Facility, FacilityMembership

pytestmark = pytest.mark.django_db


def test_audit_fields_record_who_created_a_facility(user):
    token = set_current_user(user)
    try:
        facility = Facility.objects.create(name="Audit Clinic", code="audit")
    finally:
        reset_current_user(token)
    assert facility.created_by == user
    assert facility.updated_by == user


def test_user_sees_only_facilities_they_belong_to(user, kigali, huye):
    FacilityMembership.objects.create(user=user, facility=kigali)
    assert list(Facility.objects.for_user(user)) == [kigali]


def test_ended_membership_gives_no_access(user, kigali):
    today = timezone.localdate()
    FacilityMembership.objects.create(
        user=user, facility=kigali,
        starts_on=today - timedelta(days=60), ends_on=today - timedelta(days=1),
    )
    assert not Facility.objects.for_user(user).exists()


def test_membership_that_has_not_started_gives_no_access(user, kigali):
    FacilityMembership.objects.create(
        user=user, facility=kigali, starts_on=timezone.localdate() + timedelta(days=5)
    )
    assert not Facility.objects.for_user(user).exists()


def test_switched_off_membership_gives_no_access(user, kigali):
    FacilityMembership.objects.create(user=user, facility=kigali, is_active=False)
    assert not Facility.objects.for_user(user).exists()


def test_user_can_work_in_two_facilities(user, kigali, huye):
    FacilityMembership.objects.create(user=user, facility=kigali)
    FacilityMembership.objects.create(user=user, facility=huye)
    assert set(Facility.objects.for_user(user)) == {kigali, huye}


def test_inactive_facility_is_hidden(user):
    closed = Facility.objects.create(name="Closed Clinic", code="closed", is_active=False)
    FacilityMembership.objects.create(user=user, facility=closed)
    assert not Facility.objects.for_user(user).exists()


def test_a_user_has_one_membership_per_facility(user, kigali):
    FacilityMembership.objects.create(user=user, facility=kigali)
    with pytest.raises(IntegrityError):
        FacilityMembership.objects.create(user=user, facility=kigali)


def test_department_code_is_unique_within_a_facility_only(kigali, huye):
    Department.objects.create(facility=kigali, code="lab", name="Laboratory")
    Department.objects.create(facility=huye, code="lab", name="Laboratory")
    with pytest.raises(IntegrityError):
        Department.objects.create(facility=kigali, code="lab", name="Lab Two")


def test_membership_department_must_belong_to_the_same_facility(user, kigali, huye):
    lab = Department.objects.create(facility=huye, code="lab", name="Laboratory")
    membership = FacilityMembership(user=user, facility=kigali, department=lab)
    with pytest.raises(ValidationError):
        membership.full_clean()


def test_end_date_cannot_be_before_start_date(user, kigali):
    today = timezone.localdate()
    with pytest.raises(IntegrityError):
        FacilityMembership.objects.create(
            user=user, facility=kigali, starts_on=today, ends_on=today - timedelta(days=1)
        )


def test_departments_can_be_scoped_to_a_facility_or_a_user(user, kigali, huye):
    opd = Department.objects.create(facility=kigali, code="opd", name="OPD")
    Department.objects.create(facility=huye, code="opd", name="OPD")
    FacilityMembership.objects.create(user=user, facility=kigali)
    assert list(Department.objects.for_facility(kigali)) == [opd]
    assert list(Department.objects.for_user(user)) == [opd]


def test_seed_command_is_safe_to_run_twice():
    call_command("seed_demo_facility", stdout=StringIO())
    call_command("seed_demo_facility", stdout=StringIO())
    assert Department.objects.filter(facility__code="nyarugenge").count() == len(DEPARTMENTS)