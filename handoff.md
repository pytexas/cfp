# Handoff: meetup-cfp Implementation

## Current State

The specification has been reviewed and rearchitected, the plan has been run, and zero implementation exists.
The repo currently contains only planning documents: `spec.md`, `plan.md`, `todo.md`, and `CLAUDE.md`.
No Django project, no apps, no code, no tests.

Branch: `portfolio-audit` (clean tree).
Do the implementation work here or branch from here; never commit to `main`.

The next agent starts at Step 1 of `plan.md` (project scaffolding).

## The Headline Change: Django-only to Temporal App

The review rearchitected this project from a Django-only CFP into a Django + Temporal application (commit `4fb43ee`, "Rearchitect as Temporal app, apply spec review, regen 24-step plan").
This is the single most important thing to understand before writing any code.

What changed and why:

Django is now the web and read layer only.
Every write to a submission's lifecycle flows through a durable Temporal workflow executed by a dedicated worker service.
The reason is correctness under concurrency and durability: the status state machine and its audit trail are owned by a workflow per submission-target, so a transition is validated once, in one place, and either applied atomically or rejected with no side effects.
PostgreSQL mirrors the `status` column as the read model, so dashboards, filters, and exports never touch workflows.

Concretely:

- Two workflows. `SubmissionIntakeWorkflow` (`intake-{submission_uuid}`, short-lived) persists all records for a new submission in one transaction, then starts the lifecycle workflows and fires `submission.received` webhooks.
  `SubmissionLifecycleWorkflow` (`lifecycle-{submission_meetup_id}`, long-running entity) owns the status state machine for one `SubmissionMeetup` row.
- Status transitions arrive as a Temporal Update, `request_transition(new_status, actor, scheduled_date)`.
  The Update validator enforces the normative transition table.
  Rejected updates never enter workflow history, return the error synchronously, and write no audit row.
- Django code never writes `SubmissionMeetup.status` directly.
  It calls `reviews/services.request_transition`, which delivers the Update via update-with-start (workflow id `lifecycle-{submission_meetup_id}`), so seeded rows and completed workflows self-heal.
- One `worker` service (same image as `web`) runs `manage.py run_worker` against task queue `cfp-main`.
- Workflow code is deterministic: no ORM, no I/O, no clock or random outside Temporal APIs.
  All side effects live in sync activities on the worker's thread pool.
  Workflows live in `workflows.py`, activities in `activities.py`, and Django-free dataclasses in `messages.py`, per owning app.
- File contents never flow through workflow inputs or results.
  Views save uploads to storage first and pass storage paths to the intake workflow.

If you have only read the original Django-only spec, discard that model.
The current `spec.md` (Temporal Architecture section) is authoritative.

## Resolved Decisions (Build These As Stated)

These were the spec's Open Questions, now resolved in `spec.md`:

1. Alpine.js stays in the stack, reserved for client-only UI state (Select All, collapsible groups, file-input re-select notice).
2. Headshot uploads are publicly fetchable (nginx serves `media/headshots/` directly); all other uploads stay auth-gated through a Django view that hands off via `X-Accel-Redirect`.
3. Withdrawn rows are excluded from the duplicate-submission check, so withdraw-and-resubmit is the supported revision path.
4. Build on Django 6.0 (Python 3.12+).

## Open Questions Carried Forward (Decisions, Not Implementer Picks)

The following remain open in the spec.
The plan builds the spec's stated default for each; treat these as documented defaults to confirm with Mason, not silent choices to make yourself.
Do not quietly deviate; if a default looks wrong mid-implementation, flag it rather than picking your own answer.

- Rate limiting beyond CAPTCHA (e.g. `django-ratelimit` per-IP on POST endpoints): not planned; CAPTCHA only.
- Non-core global field management: the spec lets super-admins create additional non-core global fields (stored in `SubmissionFieldResponse`), and the plan builds that.
  If management should instead be limited to relabeling and reordering the six core fields, the `global_field` FK and `is_core` flag can be dropped.
- Acceptance-rate formula: accepted-lineage / (accepted-lineage + Rejected), excluding Waitlisted and in-flight rows.
  Marked "confirm or adjust" in the spec; the plan implements it as written.
- Post-submission editing: the withdrawal token only withdraws.
  Withdraw-and-resubmit is the current answer; whether the token should also allow editing responses is unresolved.
- Data retention / hard delete: no purge-on-request flow is specified.
  Whether a super-admin (or anyone) can hard-delete a speaker's submissions and files is unresolved.
- PostgreSQL version: pinned at 16 (fine until November 2028); no decision to bump to 17 before starting.
- Timezone scope: a single org-wide `TIME_ZONE` drives CFP window display and "this month" / "upcoming" math.
  Whether per-meetup timezones matter is unresolved.

## Known Risks

- Temporal semantics are now load-bearing.
  Determinism violations, non-idempotent activities, and validator/state-mutation mistakes will surface as subtle non-determinism or double-writes, not obvious crashes.
  The transition table (`reviews/transitions.py`) and all `messages.py` modules must stay import-safe for the workflow sandbox (no Django imports).
  Activities must be idempotent because retries and replays are normal.
- Django 6.0 is the current release, not an LTS.
  Third-party package support (allauth, tailwind-cli, django-stubs) should be verified against 6.0 during Step 1 rather than assumed.
- Multi-meetup data isolation is a correctness and privacy requirement.
  Per-meetup roles gate every read and write; exports and the submission-detail "other meetups" panel must never leak another meetup's votes, notes, or reviewer identities.
  The (submission, meetup, event) uniqueness rule relies on `nulls_distinct=False`, which is PostgreSQL-only, so it is mirrored in `clean()` for SQLite dev/test parity.

## Stack Context

Multi-meetup Call for Proposals platform.
Speakers submit talk proposals to one or more meetups within a single organization; organizers review and track them through role-based dashboards.
The public surface is submission forms only (no event listings, no talk history).

- Backend: Django 6.0 (Python 3.12+).
- Orchestration: Temporal (`temporalio` Python SDK; `temporal server start-dev` in development, self-hosted server in Docker Compose in production).
- Frontend: Tailwind CSS 4.x via `django-tailwind-cli` (no Node.js), HTMX 2.x, Alpine.js 3.x.
- Auth: `django-allauth` 65.x (Django auth plus GitHub and Google OAuth); Super-Admin is a boolean flag on the user model, separate from Django's `is_superuser`.
- Database: SQLite in development, PostgreSQL 16 in production.
- Package management: `uv`.
- Deployment: Docker Compose (web, worker, temporal, temporal-ui, db, nginx).

Permission hierarchy: Read to Reviewer to Write to Admin to Super-Admin, per-meetup via `MeetupRole`, checked with rank comparison (`>=`), never equality.

## Exact Next Action

Execute Step 1 of `plan.md` (Project Scaffolding & Configuration): initialize `pyproject.toml` with `uv`, run `django-admin startproject meetup_cfp .`, split settings into base/dev/prod, create the six app shells, and get `just check` passing on a smoke test.

## Reference Map

- `spec.md`: authoritative specification (read the Temporal Architecture, Data Model, Permission Model, and Submission Lifecycle sections first).
- `plan.md`: 24 TDD steps, each with a code-generation prompt, exact file paths, and acceptance criteria; a Current Status table; Architecture Decisions; and Implementation Guidelines.
- `todo.md`: per-step checklist mirroring the plan.
- `CLAUDE.md`: condensed architecture notes and commands.
- `.ai-sessions/`: session summaries and `lessons.md`; read the most recent summary before starting.
