"""Project-level views used to verify the frontend stack is wired up.

These are placeholders for the setup smoke test; real feature views live in
their respective apps (see spec.md).
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone


def home(request: HttpRequest) -> HttpResponse:
    """Landing page: a Python-logo gradient hero (navbar comes from base.html)."""
    return render(request, "home.html")


def ping(request: HttpRequest) -> HttpResponse:
    """Return an HTML fragment for the HTMX round-trip demo."""
    return render(request, "_ping.html", {"now": timezone.now()})
