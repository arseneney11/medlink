from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


@login_required
def home(request):
    return render(request, "home.html")


def health(request):
    """Used by CI, Docker and (later) the load balancer to confirm the app and database are up."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})