"""Template context processors shared across all pages."""

from django.http import HttpRequest


def navigation(request: HttpRequest) -> dict[str, list[str]]:
    """Provide the site nav links to every template.

    Registered in ``TEMPLATES`` so the reusable navbar partial
    (``partials/_navbar.html``) renders on any page without each view
    having to pass the links itself.
    """
    return {
        "nav_links": ["Home", "Meetups", "Speakers", "Schedule", "Sponsors", "About"],
    }
