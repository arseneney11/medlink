from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.access.models import MembershipRole, Role
from apps.access.registry import DEFAULT_ROLES
from apps.access.services import create_default_roles
from apps.facilities.models import Facility, FacilityMembership


class Command(BaseCommand):
    help = "Create default roles for facilities (never overwrites edits) and optionally give roles to a user."

    def add_arguments(self, parser):
        parser.add_argument("--facility", help="Facility code. Default: all facilities.")
        parser.add_argument("--user", help="Username to give roles to.")
        parser.add_argument("--roles", default="", help="Comma-separated role codes, e.g. doctor,receptionist")

    def handle(self, *args, **options):
        facilities = Facility.objects.all()
        if options["facility"]:
            facilities = facilities.filter(code=options["facility"])
            if not facilities.exists():
                raise CommandError(f"No facility with code {options['facility']!r}.")
        for facility in facilities:
            create_default_roles(facility)

        role_codes = [c.strip() for c in options["roles"].split(",") if c.strip()]
        if options["user"] or role_codes:
            if not (options["user"] and role_codes):
                raise CommandError("Use --user and --roles together.")
            if facilities.count() != 1:
                raise CommandError("Giving roles needs exactly one facility: add --facility CODE.")
            facility = facilities.get()
            User = get_user_model()
            try:
                user = User.objects.get(username=options["user"])
            except User.DoesNotExist:
                raise CommandError(f"No user named {options['user']!r}.")
            membership, _ = FacilityMembership.objects.get_or_create(user=user, facility=facility)
            for code in role_codes:
                try:
                    role = Role.objects.get(facility=facility, code=code)
                except Role.DoesNotExist:
                    valid = ", ".join(r[0] for r in DEFAULT_ROLES)
                    raise CommandError(f"No role {code!r} in {facility.name}. Default roles: {valid}")
                MembershipRole.objects.get_or_create(membership=membership, role=role)

        self.stdout.write(self.style.SUCCESS(f"Roles ready for {facilities.count()} facility(ies)."))