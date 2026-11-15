from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.facilities.models import FacilityMembership, FacilityScopedModel


class Permission(models.Model):
    """One thing a person may be allowed to do. Defined in registry.py, never edited by hand."""

    code = models.CharField(max_length=60, unique=True)
    module = models.CharField(max_length=30)
    action = models.CharField(max_length=30)
    label = models.CharField(max_length=150)

    class Meta:
        ordering = ["module", "action"]

    def __str__(self):
        return self.label


class Role(FacilityScopedModel):
    """A named set of permissions, owned by one facility (Module 21 §21.2, §21.6)."""

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=40)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["facility", "code"], name="unique_role_code_per_facility"),
        ]

    def __str__(self):
        return f"{self.name} ({self.facility.name})"


class MembershipRole(BaseModel):
    """Gives one role to one person at one facility. Who granted it is recorded automatically."""

    membership = models.ForeignKey(
        FacilityMembership, on_delete=models.PROTECT, related_name="role_assignments"
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="assignments")

    class Meta:
        ordering = ["membership", "role"]
        constraints = [
            models.UniqueConstraint(fields=["membership", "role"], name="one_assignment_per_role"),
        ]

    def __str__(self):
        return f"{self.membership}: {self.role.name}"

    def clean(self):
        if self.membership_id and self.role_id and self.role.facility_id != self.membership.facility_id:
            raise ValidationError({"role": "This role belongs to a different facility."})

    def save(self, *args, **kwargs):
        # A database constraint cannot express "same facility", so we enforce it here too.
        self.clean()
        super().save(*args, **kwargs)