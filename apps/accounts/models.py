from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimestampedModel, UUIDModel


class User(UUIDModel, TimestampedModel, AbstractUser):
    """A person who signs in to Medlink. One account per person, never shared."""

    phone = models.CharField(max_length=30, blank=True)
    employee_number = models.CharField(max_length=40, blank=True)
    job_title = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.get_full_name() or self.username