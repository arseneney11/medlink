from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .middleware import FACILITY_SESSION_KEY
from .models import Facility


@login_required
@require_POST
def switch(request):
    """Choose which facility you are working in. Only facilities you belong to are allowed."""
    try:
        facility = Facility.objects.for_user(request.user).filter(pk=request.POST.get("facility")).first()
    except (ValidationError, ValueError):
        facility = None
    if facility is None:
        raise PermissionDenied("You do not have access to that facility.")
    request.session[FACILITY_SESSION_KEY] = str(facility.pk)
    return redirect("core:home")