from .models import Facility

FACILITY_SESSION_KEY = "facility_id"


class CurrentFacilityMiddleware:
    """Works out which facility the signed-in user is working in.

    Sets request.user_facilities (all they can access) and request.facility
    (the one they are working in, or None if they still need to choose)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_facilities = []
        request.facility = None

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            facilities = list(Facility.objects.for_user(user))
            request.user_facilities = facilities
            chosen = request.session.get(FACILITY_SESSION_KEY)
            for facility in facilities:
                if str(facility.pk) == chosen:
                    request.facility = facility
                    break
            else:
                if len(facilities) == 1:
                    request.facility = facilities[0]

        return self.get_response(request)