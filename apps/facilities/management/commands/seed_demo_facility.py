from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.facilities.models import Department, Facility, FacilityMembership, FacilityType

# (code, name, is_clinical), a starter set taken from Module 1 §2 and the non-clinical modules.
DEPARTMENTS = [
    ("reception", "Reception and Registration", False),
    ("opd", "Outpatient Department (OPD)", True),
    ("emergency", "Accidents and Emergency", True),
    ("ipd", "Inpatient Department (IPD)", True),
    ("lab", "Laboratory", True),
    ("imaging", "Radiology and Imaging", True),
    ("pharmacy", "Pharmacy", True),
    ("dental", "Dental and Orthodontics", True),
    ("billing", "Billing and Finance", False),
    ("stores", "Stores and Inventory", False),
    ("hr", "Human Resources", False),
]


class Command(BaseCommand):
    help = "Create a demo facility with starter departments. Safe to run more than once."

    def add_arguments(self, parser):
        parser.add_argument("--user", help="Username to give access to the demo facility")

    def handle(self, *args, **options):
        user = None
        if options["user"]:
            User = get_user_model()
            try:
                user = User.objects.get(username=options["user"])
            except User.DoesNotExist:
                raise CommandError(f"No user named {options['user']!r}.")

        facility, _ = Facility.objects.get_or_create(
            code="nyarugenge",
            defaults={
                "name": "Nyarugenge Polyclinic",
                "facility_type": FacilityType.POLYCLINIC,
                "district": "Nyarugenge",
            },
        )
        for code, name, is_clinical in DEPARTMENTS:
            Department.objects.get_or_create(
                facility=facility, code=code, defaults={"name": name, "is_clinical": is_clinical}
            )
        if user:
            FacilityMembership.objects.get_or_create(user=user, facility=facility)

        self.stdout.write(self.style.SUCCESS(f"{facility.name}: {len(DEPARTMENTS)} departments ready."))