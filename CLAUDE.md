# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

meetup-cfp is a multi-meetup Call for Proposals platform built with Django. Speakers submit talk proposals to one or more meetups within a single organization. Meetup organizers review, track, and manage submissions through role-based dashboards. The public surface is submission forms only — no event listings or talk history.

See `spec.md` for the full specification including data models, business rules, and UI flows.

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Tailwind CSS (`django-tailwind-cli`, no Node.js), HTMX, Alpine.js
- **Database**: SQLite (dev), PostgreSQL 16 (prod)
- **Auth**: `django-allauth` (Django auth + GitHub & Google OAuth)
- **Package Management**: `uv`
- **Deployment**: Docker Compose (Gunicorn + Nginx + PostgreSQL)

## Django Apps

| App | Purpose |
|-----|---------|
| `core` | Organization singleton, global form fields, base mixins |
| `meetups` | Meetup CRUD, branding, events, CFP windows |
| `submissions` | Proposals, custom questions, dynamic forms, file uploads, withdrawal |
| `reviews` | Voting (thumbs up/down), notes, communication tracking, status transitions |
| `users` | Auth integration, MeetupRole model, permission checks |
| `dashboard` | Authenticated views, filtering, export (CSV/JSON), warnings |

## Essential Commands

```bash
# Setup
uv sync
uv run python manage.py migrate
uv run python manage.py seed_global_fields
uv run python manage.py createsuperuser
uv run python manage.py tailwind build

# Development
uv run python manage.py runserver

# Testing
uv run pytest
uv run pytest path/to/test_file.py::TestClass::test_method  # single test
uv run pytest -x  # stop on first failure

# Linting & formatting
uv run ruff check .
uv run ruff format .
uv run mypy .

# Docker (production)
docker compose up --build
```

## Architecture Notes

### Permission Model

Five-tier hierarchy where each level inherits the one below: **Read → Reviewer → Write → Admin → Super-Admin**. Roles are per-meetup via `MeetupRole(user, meetup, role)`. Super-Admin is a boolean flag on the User model, separate from Django's `is_superuser`. Permission checks must enforce this hierarchy — don't check roles with equality, check with `>=`.

### Submission Data Model

A `Submission` holds speaker info and proposal content (one record). `SubmissionMeetup` is the junction table linking it to each targeted meetup — this is where per-meetup status, votes, notes, and scheduled dates live. No data duplication across meetups. Custom question answers are stored in `SubmissionFieldResponse` with a polymorphic FK (exactly one of `global_field`, `standard_field`, or `custom_question`).

### Dynamic Form Assembly (HTMX)

The multi-submit form (`/submit/`) uses HTMX to load additional fields when meetup checkboxes change. The endpoint `POST /submit/dynamic-fields/` accepts selected meetup IDs and returns an HTML fragment with the union of optional standard fields plus custom questions grouped by meetup. This is the most complex frontend interaction.

### Status Lifecycle

Two phases: **Review** (Submitted → Under Review → Accepted/Rejected/Waitlisted/Withdrawn) and **Post-Acceptance** (Accepted → Email Sent → Speaker Accepted → Scheduled → Presented). All transitions are manual. Every transition creates a `StatusChange` audit log entry. `scheduled_date` is required when moving to "Scheduled."

### Branding Cascade

Organization → Meetup. Meetups inherit org branding (logo, colors) unless they explicitly override fields. Templates should resolve branding with fallback logic (meetup field if set, else org field).

### Withdrawal

Speakers get a secret UUID-based URL. No account needed. The withdrawal page lets them select which meetups to withdraw from (per-meetup, not all-or-nothing).

## Testing Approach

Follow TDD. Key testable boundaries:
- **Submission validation**: duplicate detection (email + title + meetup), CFP window enforcement, required field checks
- **Permission checks**: role hierarchy, per-meetup scoping, super-admin bypass
- **Status transitions**: valid transition enforcement, audit log creation
- **Dynamic form assembly**: correct field sets for meetup combinations
- **Export generation**: CSV/JSON format correctness with custom question columns
- **Withdrawal flow**: token validation, per-meetup withdrawal

Test YOUR application logic. Don't test Django framework behavior (ORM queries returning results, form rendering, etc.). Focus on business rules, data validation, and permission enforcement.
