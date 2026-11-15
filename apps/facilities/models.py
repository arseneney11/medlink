from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import BaseModel


class FacilityType(models.TextChoices):
    HOSPITAL = "hospital", "Hospital"
    POLYCLINIC = "polyclinic", "Polyclinic"
    HEALTH_CENTRE = "health_centre", "Health centre"
    CLINIC = "clinic", "Clinic"


class FacilityQuerySet(models.QuerySet):
    def for_user(self, user):
        """Active facilities where this user currently has access."""
        if user is None or not user.is_authenticated:
            return self.none()
        allowed = FacilityMembership.objects.current().filter(user=user).values("facility_id")
        return self.filter(is_active=True, pk__in=allowed)


class Facility(BaseModel):
    """A hospital, polyclinic, health centre or clinic using Medlink (Module 21 §21.6)."""

    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=20, unique=True, help_text="Short unique code, e.g. nyarugenge")
    facility_type = models.CharField(
        max_length=20, choices=FacilityType.choices, default=FacilityType.CLINIC
    )
    district = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = FacilityQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "facilities"

    def __str__(self):
        return self.name


class FacilityScopedQuerySet(models.QuerySet):
    def for_facility(self, facility):
        return self.filter(facility=facility)

    def for_user(self, user):
        return self.filter(facility__in=Facility.objects.for_user(user))


class FacilityScopedModel(BaseModel):
    """Base for every record that belongs to one facility."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)

    objects = FacilityScopedQuerySet.as_manager()

    class Meta:
        abstract = True


class Department(FacilityScopedModel):
    """A clinical or non-clinical department, activated per facility (Module 1 §2)."""

    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=30)
    is_clinical = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["facility", "code"], name="unique_department_code_per_facility"),
            models.UniqueConstraint(fields=["facility", "name"], name="unique_department_name_per_facility"),
        ]

    def __str__(self):
        return f"{self.name} ({self.facility.name})"


class MembershipQuerySet(models.QuerySet):
    def current(self, on=None):
        """Memberships that are switched on and inside their start/end dates."""
        on = on or timezone.localdate()
        return self.filter(is_active=True, starts_on__lte=on).filter(
            Q(ends_on__isnull=True) | Q(ends_on__gte=on)
        )


class FacilityMembership(BaseModel):
    """Lets one user work in one facility. A user can have several (Module 21 §21.6)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="facility_memberships"
    )
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT, related_name="memberships")
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.PROTECT, related_name="memberships"
    )
    starts_on = models.DateField(default=timezone.localdate)
    ends_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = MembershipQuerySet.as_manager()

    class Meta:
        ordering = ["facility__name", "user__username"]
        constraints = [
            models.UniqueConstraint(fields=["user", "facility"], name="one_membership_per_user_per_facility"),
            models.CheckConstraint(
                condition=Q(ends_on__isnull=True) | Q(ends_on__gte=F("starts_on")),
                name="membership_end_not_before_start",
            ),
        ]

    def __str__(self):
        return f"{self.user} at {self.facility}"

    def clean(self):
        if self.department_id and self.facility_id and self.department.facility_id != self.facility_id:
            raise ValidationError({"department": "This department belongs to a different facility."})