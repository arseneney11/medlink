from django.apps import AppConfig


class AccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.access"

    def ready(self):
        from django.db.models.signals import post_migrate

        from . import signals

        post_migrate.connect(signals.sync_permissions_after_migrate, sender=self)