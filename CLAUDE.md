# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

meetup-cfp is a multi-meetup Call for Proposals platform built with Django and Temporal. Speakers submit talk proposals to one or more meetups within a single organization. Meetup organizers review, track, and manage submissions through role-based dashboards. The public surface is submission forms only — no event listings or talk history.

The submission lifecycle is workflow-owned: every submission target is backed by a durable Temporal workflow, and Django is the web and read layer.

See `spec.md` for the full specification and `plan.md`/`todo.md` for the TDD implementation roadmap (24 steps, none started yet — the repo currently contains only planning documents).

## Tech Stack

- **Backend**: Django 6.0 (Python 3.12+)
- **Orchestration**: Temporal (`temporalio` Python SDK; dev server locally, self-hosted in prod)
- **Frontend**: Tailwind CSS 4.x (`django-tailwind-cli`, no Node.js), HTMX 2.x, Alpine.js
- **Database**: SQLite (dev), PostgreSQL 16 (prod)
- **Auth**: `django-allauth` 65.x (Django auth + GitHub & Google OAuth)
- **Package Management**: `uv`
- **Deployment**: Docker Compose (Gunicorn + Nginx + PostgreSQL + Temporal server + worker)

## Django Apps

| App | Purpose |
|-----|---------|
| `core` | Organization singleton, global form fields, base mixins, Temporal worker entrypoint (`run_worker`) |
| `meetups` | Meetup CRUD, branding, events, CFP windows, webhook config and delivery |
| `submissions` | Proposals, custom questions, dynamic forms, file uploads, withdrawal, intake workflow |
| `reviews` | Voting, notes, status transitions, lifecycle workflow |
| `users` | Auth integration, MeetupRole model, permission checks |
| `dashboard` | Authenticated views, filtering, export (CSV/JSON), warnings |

Import direction: `reviews` and `dashboard` may import from `submissions` and `meetups`; `submissions` from `meetups` and `core`; nothing imports from `dashboard`. Apps that own Temporal code keep workflows in `workflows.py`, activities in `activities.py`, and Django-free dataclasses in `messages.py`.

## Essential Commands

```bash
# Setup
uv sync
uv run python manage.py migrate
uv run python manage.py seed_global_fields
uv run python manage.py createsuperuser
uv run python manage.py tailwind build

# Development (three terminals)
temporal server start-dev
uv run python manage.py run_worker
uv run python manage.py runserver

# Testing
uv run pytest
uv run pytest path/to/test_file.py::TestClass::test_method  # single test
uv run pytest -x  # stop on first failure

# Linting & formatting
uv run ruff check .
uv run ruff format .
uv run mypy .

# Task runner (once the Justfile exists)
just check  # ruff + format check + pytest

# Docker (production)
docker compose up --build
```

## Architecture Notes

### Temporal Ownership of the Lifecycle

Django never writes `SubmissionMeetup.status` directly. All transitions go through `reviews/services.py`, which sends a `request_transition` Update (via update-with-start on workflow ID `lifecycle-{submission_meetup_id}`) to that row's `SubmissionLifecycleWorkflow`. The Update validator enforces the normative transition table: rejected transitions never enter workflow history, return the error synchronously, and write no audit row. Accepted transitions run activities that write the status + `StatusChange` audit row to PostgreSQL and deliver webhooks. PostgreSQL is the read model — dashboards, filters, and exports query the mirrored `status` column, never workflows.

New submissions flow through `SubmissionIntakeWorkflow` (`intake-{submission_uuid}`): one activity persists all records in a single transaction, then lifecycle workflows start as `ABANDON` children. Views validate; workflows persist. File contents never pass through workflow inputs — storage paths only.

Workflow code must be deterministic (no ORM, no I/O, no clock/random outside Temporal APIs); all side effects live in sync activities running on the worker's thread pool.

### Permission Model

Five-tier hierarchy where each level inherits the one below: **Read → Reviewer → Write → Admin → Super-Admin**. Roles are per-meetup via `MeetupRole(user, meetup, role)`. Super-Admin is a boolean flag on the User model, separate from Django's `is_superuser`. Check with rank comparison (`>=`), never equality. Role assignment matrix: no role assigns at or above its own rank; Write assigns Reviewer only.

### Submission Data Model

A `Submission` holds speaker info and proposal content (one record). `SubmissionMeetup` is the junction table linking it to each targeted meetup — per-meetup status, votes, notes, and scheduled dates live there. Custom question answers are stored in `SubmissionFieldResponse` with a polymorphic FK (exactly one of `global_field`, `standard_field`, `custom_question`); files live on `FileUpload`. The (submission, meetup, event) uniqueness rule uses `nulls_distinct=False`, which is PostgreSQL-only — it's mirrored in `clean()` so SQLite dev/test behaves identically.

### CFP Windows and Grace Period

`cfp_is_open` drives display (the form disappears at `cfp_close_date`); `accepts_submissions_now` drives submit-time validation and extends acceptance through `grace_period_minutes` past close. Deactivation and archival have no grace.

### Duplicate Detection

Same normalized email + title + same (meetup, event) target = blocked, all-or-nothing across a multi-submit. Withdrawn rows do NOT count — withdraw-and-resubmit is the supported revision path.

### Webhooks

Per-meetup `webhook_url` (+ optional `webhook_secret` for an `X-CFP-Signature` HMAC-SHA256 header). Events: `submission.received` and `submission.status_changed`. Delivered by a Temporal activity with backoff retries capped near 24 hours; delivery never blocks or rolls back a transition. Payloads carry submission id/title/speaker name but never speaker email.

### Media Access

Headshot uploads are public (nginx serves `media/headshots/` directly). All other uploads route through an authenticated Django view (Read+ on a targeted meetup, or super-admin) that hands off via `X-Accel-Redirect` in production and `FileResponse` in dev.

### Branding Cascade

Organization → Meetup. Templates resolve branding through `effective_*` properties (meetup field if set, else org field), never raw fields.

## Testing Approach

Follow TDD. Test YOUR application logic — business rules, validation, permissions, transitions, workflow behavior — not Django or Temporal themselves.

- **Workflow tests**: `WorkflowEnvironment.start_time_skipping()` with mocked activities; activity and service logic is tested synchronously without Temporal.
- **Key boundaries**: transition table enforcement (validator rejects, no audit row), duplicate detection (withdrawn excluded), grace-period window math, dynamic form assembly (union + required-ORed), role hierarchy and assignment matrix, export column naming and privacy, webhook payload shape and signing, bulk-action all-or-nothing pre-validation.

## Session History

`.ai-sessions/` holds session summaries and `lessons.md`. Before starting implementation work, read the most recent summary (sort filenames lexicographically) and honor its "Suggested Skills for Next Session" section.
