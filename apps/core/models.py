import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .current_user import get_current_user
from .exceptions import HardDeleteNotAllowed


class UUIDModel(models.Model):
    """Random, non-guessable primary key. Human numbers (patient no., invoice no.)
    are separate fields on the models that need them."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    """Every record knows who created it, who last changed it, and when."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user is not None:
            if self._state.adding and self.created_by_id is None:
                self.created_by = user
            self.updated_by = user
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = {*update_fields, "updated_by", "updated_at"}
        super().save(*args, **kwargs)


class ProtectedQuerySet(models.QuerySet):
    def delete(self):
        raise HardDeleteNotAllowed(
            "Records of this type cannot be deleted. Use void(reason=...) instead."
        )

    def active(self):
        return self.filter(voided_at__isnull=True)

    def voided(self):
        return self.filter(voided_at__isnull=False)


ProtectedManager = models.Manager.from_queryset(ProtectedQuerySet)


class ActiveManager(ProtectedManager):
    """Default manager: hides voided records from everyday queries."""

    def get_queryset(self):
        return super().get_queryset().filter(voided_at__isnull=True)


class ProtectedModel(BaseModel):
    """For clinical and financial records. They can be voided, never deleted."""

    voided_at = models.DateTimeField(null=True, blank=True, editable=False, db_index=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="+",
    )
    void_reason = models.TextField(blank=True, editable=False)

    objects = ActiveManager()
    all_objects = ProtectedManager()

    class Meta:
        abstract = True

    @property
    def is_voided(self):
        return self.voided_at is not None

    def delete(self, *args, **kwargs):
        raise HardDeleteNotAllowed(
            f"{self.__class__.__name__} records cannot be deleted. Use void(reason=...) instead."
        )

    def void(self, reason, user=None):
        reason = (reason or "").strip()
        if not reason:
            raise ValueError("A reason is required to void a record.")
        if self.is_voided:
            raise ValueError("This record is already voided.")
        self.voided_at = timezone.now()
        self.voided_by = user or get_current_user()
        self.void_reason = reason
        self.save(update_fields=["voided_at", "voided_by", "void_reason"])