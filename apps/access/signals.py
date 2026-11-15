from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import create_default_roles, sync_permissions


def sync_permissions_after_migrate(sender, **kwargs):
    sync_permissions()


@receiver(post_save, sender="facilities.Facility")
def create_roles_for_new_facility(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        create_default_roles(instance)