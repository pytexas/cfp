# meetup-cfp Implementation Plan

## Current Status

| Step | Description | Status |
|------|-------------|--------|
| 1 | Project Scaffolding & Configuration | Not Started |
| 2 | Core App — Organization & Global Fields | Not Started |
| 3 | Users App — Custom User & Role Model | Not Started |
| 4 | Meetups App — Meetup & Event Models | Not Started |
| 5 | Submissions App — Submission & Field Response Models | Not Started |
| 6 | Reviews App — Votes, Notes, Transition Table | Not Started |
| 7 | Permission System & Test Factories | Not Started |
| 8 | Temporal Foundation — Client, Worker, Test Harness | Not Started |
| 9 | Submission Lifecycle Workflow & Transition Service | Not Started |
| 10 | Submission Intake Workflow & Intake Service | Not Started |
| 11 | Webhook Delivery | Not Started |
| 12 | Public Pages — Org Landing & Meetup Pages | Not Started |
| 13 | Dynamic Multi-Submit Form (HTMX) | Not Started |
| 14 | Submission Validation & Intake Wiring | Not Started |
| 15 | Withdrawal Flow | Not Started |
| 16 | Dashboard — Authentication & Layout | Not Started |
| 17 | Dashboard — Meetup Submissions View | Not Started |
| 18 | Dashboard — Submission Detail & Reviews | Not Started |
| 19 | Dashboard — Bulk Actions | Not Started |
| 20 | Dashboard — Export (CSV/JSON) | Not Started |
| 21 | Dashboard — Super-Admin Views & Warnings | Not Started |
| 22 | Media Access Control | Not Started |
| 23 | Management Commands & Data Seeding | Not Started |
| 24 | Docker & Production Configuration | Not Started |

---

## Architecture Decisions

- **Project name**: `meetup_cfp` (the Django project package)
- **Apps live at**: top-level (e.g., `core/`, `meetups/`, not nested under project)
- **Test location**: each app has a `tests/` package (e.g., `core/tests/test_models.py`)
- **Settings split**: `meetup_cfp/settings/base.py`, `dev.py`, `prod.py`
- **Justfile**: used as the task runner for common commands
- **pytest**: with `pytest-django` and `pytest-asyncio` (configured in `pyproject.toml`)
- **Factory Boy**: for test fixtures via `factory_boy`
- **ruff**: for linting and formatting; **mypy**: for type checking
- **Temporal**: `temporalio` Python SDK; one task queue `cfp-main`; one worker process (`manage.py run_worker`)
- **Workflow code layout**: each owning app keeps workflows in `workflows.py` and activities in `activities.py` (SDK sandbox reloads workflow modules, keep them lean)
- **Transitions**: the transition table is a pure, deterministic module (`reviews/transitions.py`) imported by both Django code and workflow code; all side effects live in activities
- **Transition delivery**: Django never writes `SubmissionMeetup.status` directly; it calls `reviews/services.py` which sends a `request_transition` Update to the lifecycle workflow using update-with-start (self-healing for seeded rows and completed workflows)
- **Large data rule**: file contents never flow through workflow history; views persist uploads and pass storage paths to the intake workflow

---

## Step 1: Project Scaffolding & Configuration

**Validator consults:** none

**Goal**: Initialize the Django 6.0 project with all tooling configured. No business logic yet — just a working skeleton that runs tests, lints, and serves a blank page.

```text
Prompt for code-generation LLM:

### Step 1: Project Scaffolding & Configuration

Set up the Django project skeleton with all tooling. No business logic — just a working foundation.

1. Initialize pyproject.toml with uv:
   - Create pyproject.toml with:
     - Project metadata (name="meetup-cfp", version="0.1.0", python requires ">=3.12")
     - Dependencies: django>=6.0, django-allauth, django-tailwind-cli, gunicorn, psycopg[binary], django-htmx, whitenoise, temporalio, httpx
     - Dev dependencies: pytest, pytest-django, pytest-asyncio, factory-boy, ruff, mypy, django-stubs, coverage
     - Ruff config: line-length=120, target python 3.12, isort settings
     - Mypy config: django-stubs plugin, strict optional, warn unused ignores
     - Pytest config: DJANGO_SETTINGS_MODULE=meetup_cfp.settings.dev, pythonpath=["."], asyncio_mode="auto"
   - Run `uv sync` to install all dependencies

2. Create Django project structure:
   - Run `uv run django-admin startproject meetup_cfp .` (note the dot — project in current dir)
   - This creates: manage.py, meetup_cfp/__init__.py, settings.py, urls.py, asgi.py, wsgi.py

3. Split settings into base/dev/prod:
   - Create meetup_cfp/settings/ package:
     - meetup_cfp/settings/__init__.py (empty)
     - meetup_cfp/settings/base.py — move content from settings.py here, then:
       - Set INSTALLED_APPS with: django defaults, allauth, django_htmx, tailwind_cli
       - Set TAILWIND_CLI_VERSION for Tailwind 4.x
       - Add django_htmx.middleware.HtmxMiddleware to MIDDLEWARE
       - Set AUTH_USER_MODEL = "users.CustomUser"
       - Set STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT
       - Set DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
       - Set USE_TZ = True and TIME_ZONE from env (default "America/Chicago")
       - Set LOGIN_REDIRECT_URL = "/dashboard/"
       - Add Temporal settings read from env: TEMPORAL_ADDRESS (default "localhost:7233"), TEMPORAL_NAMESPACE (default "default"), TEMPORAL_TASK_QUEUE (default "cfp-main")
     - meetup_cfp/settings/dev.py — imports base, sets DEBUG=True, SQLite DB, ALLOWED_HOSTS=["*"]
     - meetup_cfp/settings/prod.py — imports base, sets DEBUG=False, reads DATABASE_URL from env, reads SECRET_KEY from env, ALLOWED_HOSTS from env
   - Delete the original meetup_cfp/settings.py file

4. Create the six app directories (empty shells for now):
   - Run: `uv run python manage.py startapp core`
   - Run: `uv run python manage.py startapp meetups`
   - Run: `uv run python manage.py startapp submissions`
   - Run: `uv run python manage.py startapp reviews`
   - Run: `uv run python manage.py startapp users`
   - Run: `uv run python manage.py startapp dashboard`
   - Add all six apps to INSTALLED_APPS in base.py

5. Create a minimal users app so AUTH_USER_MODEL works:
   - Create users/models.py with a CustomUser model that extends AbstractUser:
     - Add `is_superadmin = models.BooleanField(default=False)`
     - That's it for now — just enough to not break migrations
   - Create users/admin.py registering CustomUser with Django admin

6. Create Justfile with common commands:
   - Create Justfile with recipes:
     - `dev`: `uv run python manage.py runserver`
     - `worker`: `uv run python manage.py run_worker` (command exists from Step 8; recipe can be added now)
     - `test`: `uv run pytest`
     - `test-v`: `uv run pytest -v`
     - `lint`: `uv run ruff check .`
     - `format`: `uv run ruff format .`
     - `types`: `uv run mypy .`
     - `check`: `uv run ruff check . && uv run ruff format --check . && uv run pytest`
     - `migrate`: `uv run python manage.py migrate`
     - `makemigrations`: `uv run python manage.py makemigrations`

7. Run initial migrations:
   - Run `uv run python manage.py makemigrations users`
   - Run `uv run python manage.py migrate`

8. Create a smoke test to verify the project works:
   - Create conftest.py at the project root (empty, pytest-django auto-discovers)
   - Create core/tests/__init__.py
   - Create core/tests/test_smoke.py:
     - Test that the Django app starts and can serve a 200 response from the root URL
   - Set up meetup_cfp/urls.py with a simple TemplateView for "/" pointing to a minimal base template
   - Create templates/base.html with minimal HTML5 boilerplate
   - Create templates/home.html extending base.html with placeholder text

9. Verify everything works:
   - Run `just check` (ruff + pytest should all pass)
   - Run `just migrate` to confirm migrations are clean
```

---

## Step 2: Core App — Organization & Global Fields

**Validator consults:**
- Skills: python:python

**Goal**: Build the Organization singleton and GlobalFormField/StandardOptionalField models with seed data management command. These are foundational data structures used by every other app.

```text
Prompt for code-generation LLM:

### Step 2: Core App — Organization & Global Fields

Build the Organization singleton and form field configuration models. These are used by every other app.

**NOTE**: The project skeleton from Step 1 is already in place. The users app has a minimal CustomUser model. All six app directories exist. Pytest is configured and running.

1. RED: Write model tests for Organization singleton:
   - Create core/tests/test_models.py:
     - Test that Organization.save() forces pk=1 (saving a second instance overwrites the first, never creates a second row)
     - Test that Organization.get_instance() returns the singleton (create with placeholders if missing)
     - Test that slug is auto-generated from name if not provided

2. GREEN: Implement Organization model:
   - Create core/models.py:
     - Organization model with fields per spec: name, slug, description, logo (ImageField), primary_color (CharField, default="#000000"), secondary_color (CharField, default="#ffffff")
     - Override save() to force pk=1 (singleton per spec)
     - Add get_instance() classmethod (get_or_create with pk=1 and placeholder values)
     - Add __str__ returning name
   - Create a data migration that creates the pk=1 row with placeholder values
   - Register Organization in core/admin.py

3. RED: Write model tests for GlobalFormField:
   - Update core/tests/test_models.py:
     - Test valid field_type choices include: short_text, long_text, email, url, single_select, multi_select, file_upload
     - Test that sort_order is respected in default ordering
     - Test that options field stores and retrieves a JSON list for select types
     - Test that is_active defaults to True and is_core defaults to False
     - Test that a core field (is_core=True) cannot be deactivated: setting is_active=False and calling clean() raises ValidationError
     - Test that deleting a core field raises ProtectedError or ValidationError (delete() override)

4. GREEN: Implement GlobalFormField model:
   - Add to core/models.py:
     - FIELD_TYPE_CHOICES constant: short_text, long_text, email, url, single_select, multi_select, file_upload
     - GlobalFormField with: label, field_type (CharField with choices), is_required (BooleanField), options (JSONField, default=list), sort_order (IntegerField), is_active (BooleanField, default=True), is_core (BooleanField, default=False)
     - clean() rejects is_active=False when is_core=True
     - delete() raises for core fields
     - Meta: ordering = ["sort_order"]
     - __str__ returning label

5. RED: Write model tests for StandardOptionalField:
   - Add to core/tests/test_models.py:
     - Test that StandardOptionalField stores label, field_type, options, sort_order
     - Test ordering by sort_order

6. GREEN: Implement StandardOptionalField model:
   - Add to core/models.py:
     - StandardOptionalField with: label, field_type, options (JSONField, default=list), sort_order (IntegerField)
     - Meta: ordering = ["sort_order"]
     - __str__ returning label

7. RED: Write tests for the seed_global_fields management command:
   - Create core/tests/test_commands.py:
     - Test that running seed_global_fields creates the 6 core global fields (Name, Email, Talk Title, Abstract, Description, Speaker Bio) with is_core=True and correct field types (Email is field_type="email")
     - Test that running it twice is idempotent (doesn't create duplicates)
     - Test that it creates the 5 standard optional fields (Talk Length, Experience Level, Speaker Headshot, Speaker Links, Prior Speaking Experience) with correct types (Speaker Links is "url", Speaker Headshot is "file_upload")
     - Test that Talk Length has correct options: ["15 min", "30 min", "45 min", "60 min"]
     - Test that Experience Level has correct options: ["Beginner", "Intermediate", "Advanced"]

8. GREEN: Implement seed_global_fields management command:
   - Create core/management/__init__.py, core/management/commands/__init__.py
   - Create core/management/commands/seed_global_fields.py:
     - Use get_or_create keyed on label to ensure idempotency
     - Create the 6 core global fields (is_core=True, is_required=True) and the 5 standard optional fields

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations core`
   - Run `uv run python manage.py migrate`
   - Run `just check` to confirm all tests pass and linting is clean
```

---

## Step 3: Users App — Custom User & Role Model

**Validator consults:**
- Skills: python:python

**Goal**: Build the MeetupRole model and permission-checking utilities. The permission hierarchy (Read → Reviewer → Write → Admin → Super-Admin) is central to the entire dashboard.

```text
Prompt for code-generation LLM:

### Step 3: Users App — Custom User & Role Model

Build the MeetupRole model and permission-checking utilities. The role hierarchy is central to the dashboard.

**NOTE**: Step 1 created a minimal CustomUser model with just is_superadmin. Step 2 built the Organization and field models. The users app already exists with a basic CustomUser.

1. RED: Write tests for the role hierarchy:
   - Create users/tests/__init__.py
   - Create users/tests/test_permissions.py:
     - Test that ROLE_HIERARCHY defines correct ordering: read < reviewer < write < admin < superadmin
     - Test has_meetup_role(user, meetup, "reviewer") returns True when user has "reviewer" role on that meetup
     - Test has_meetup_role(user, meetup, "reviewer") returns True when user has "write" role (rank comparison with >=, never equality)
     - Test has_meetup_role(user, meetup, "write") returns False when user has "reviewer" role
     - Test has_meetup_role returns True for any role when user.is_superadmin is True
     - Test has_meetup_role returns False when user has no role on that meetup
     - Test has_meetup_role returns False for a different meetup than the one the role is assigned to
     - Test get_user_role(user, meetup) returns the correct role string
     - Test get_user_role returns None when no role assigned
     - Test get_user_role returns "superadmin" when user.is_superadmin

2. GREEN: Implement MeetupRole and permission utilities:
   - Update users/models.py:
     - Keep existing CustomUser with is_superadmin
     - Add ROLE_CHOICES: ("read", "Read"), ("reviewer", "Reviewer"), ("write", "Write"), ("admin", "Admin")
     - Add ROLE_HIERARCHY dict mapping role names to numeric levels: read=0, reviewer=1, write=2, admin=3, superadmin=4
     - Create MeetupRole model:
       - user: FK → CustomUser
       - meetup: FK → "meetups.Meetup" (string reference — the meetups model lands in Step 4)
       - role: CharField with ROLE_CHOICES
       - Unique constraint on (user, meetup)
       - __str__ returning "{user} - {meetup} ({role})"
   - Create users/permissions.py:
     - has_meetup_role(user, meetup, required_role) → bool (superadmin bypass, then rank comparison via ROLE_HIERARCHY)
     - get_user_role(user, meetup) → str | None
   - Register MeetupRole in users/admin.py

3. RED: Write tests for permission decorators/mixins:
   - Create users/tests/test_mixins.py:
     - Test that a view protected with MeetupRoleRequiredMixin returns 403 when user has insufficient role
     - Test that it returns 200 when user has sufficient role
     - Test that it returns 302 (redirect to login) when user is not authenticated
     - Test that super-admin always gets 200

4. GREEN: Implement permission mixin:
   - Create users/mixins.py:
     - MeetupRoleRequiredMixin (for class-based views):
       - required_role attribute (set by each view)
       - get_meetup() method that extracts meetup from URL kwargs (slug)
       - dispatch() checks: authenticated → has_meetup_role → proceed or 403

5. Run migrations and verify:
   - Run `uv run python manage.py makemigrations users`
   - Run `uv run python manage.py migrate`
   - Run `just check`

Note: MeetupRole has a FK to Meetup which doesn't exist yet. Django handles string references in ForeignKey, but migrations depend on the meetups app. If migrations fail, create a temporary minimal Meetup model (name + slug) in the meetups app first; Step 4 fills it out.
```

---

## Step 4: Meetups App — Meetup & Event Models

**Validator consults:**
- Skills: python:python

**Goal**: Build the Meetup and Event models with CFP window logic (year-round vs time-boxed), the grace period, webhook configuration fields, plus MeetupOptionalFieldConfig and CustomQuestion.

```text
Prompt for code-generation LLM:

### Step 4: Meetups App — Meetup & Event Models

Build the Meetup and Event models with CFP window logic, grace period, webhook configuration, and the per-meetup form configuration models.

**NOTE**: Steps 1-3 are complete. CustomUser and MeetupRole exist. Organization, GlobalFormField, and StandardOptionalField exist in core. The MeetupRole FK to Meetup is a string reference awaiting this step.

1. RED: Write tests for Meetup model and CFP logic:
   - Create meetups/tests/__init__.py
   - Create meetups/tests/test_models.py:
     - Test Meetup creation with required fields (name, slug, description)
     - Test that slug must be unique
     - Test cfp_is_open returns True when cfp_mode="year_round" and is_active=True
     - Test cfp_is_open returns False when is_active=False (regardless of mode)
     - Test cfp_is_open returns True when cfp_mode="time_boxed" and cfp_open_date <= now() < cfp_close_date
     - Test cfp_is_open returns False when time_boxed and now() is outside the window (before open and after close)
     - Test clean() raises ValidationError when cfp_mode="time_boxed" and either date is missing
     - Test clean() raises ValidationError when cfp_open_date >= cfp_close_date
     - Test accepts_submissions_now returns True when cfp_is_open is True
     - Test accepts_submissions_now returns True when time_boxed, now() is past cfp_close_date but within grace_period_minutes
     - Test accepts_submissions_now returns False when now() is past cfp_close_date + grace_period_minutes
     - Test accepts_submissions_now returns False for a deactivated meetup even within the grace window
     - Test grace_period_minutes defaults to 0 (accepts_submissions_now === cfp_is_open when grace is 0)
     - Test effective_logo property returns meetup logo if set, else org logo
     - Test effective_primary_color / effective_secondary_color return meetup color if set, else org color

2. GREEN: Implement Meetup model:
   - Create meetups/models.py:
     - CFP_MODE_CHOICES: ("year_round", "Year Round"), ("time_boxed", "Time Boxed")
     - Meetup model with all fields per spec:
       - name, slug (unique), description (TextField)
       - logo (ImageField, blank=True, null=True)
       - primary_color, secondary_color (CharField, blank=True)
       - is_active (BooleanField, default=True)
       - cfp_mode (CharField, default="year_round")
       - cfp_open_date, cfp_close_date (DateTimeField, null=True, blank=True)
       - grace_period_minutes (PositiveIntegerField, default=0)
       - webhook_url (URLField, blank=True)
       - webhook_secret (CharField, blank=True)
       - created_at, updated_at (auto)
     - cfp_is_open property: is_active AND (year_round OR open <= now() < close) — display semantics, no grace
     - accepts_submissions_now property: is_active AND (year_round OR open <= now() < close + grace_period_minutes) — submit-time semantics
     - clean() validating time_boxed date requirements and open < close
     - effective_logo, effective_primary_color, effective_secondary_color properties with org fallback
     - __str__, Meta ordering by name
   - Register in meetups/admin.py

3. RED: Write tests for Event model and CFP logic:
   - Add to meetups/tests/test_models.py:
     - Test Event creation with FK to Meetup
     - Test Event slug is unique within a meetup (unique constraint on (meetup, slug))
     - Test Event cfp_is_open returns True when within date window, parent meetup is_active, and not archived
     - Test Event cfp_is_open returns False when outside date window
     - Test Event cfp_is_open returns False when is_archived=True
     - Test Event cfp_is_open returns False when parent meetup is deactivated
     - Test Event accepts_submissions_now honors grace_period_minutes exactly like Meetup
     - Test Event accepts_submissions_now returns False for an archived event even within the grace window

4. GREEN: Implement Event model:
   - Add to meetups/models.py:
     - Event model per spec:
       - meetup (FK → Meetup)
       - name, slug, description, date (DateField)
       - cfp_open_date, cfp_close_date (DateTimeField)
       - grace_period_minutes (PositiveIntegerField, default=0)
       - is_archived (BooleanField, default=False)
       - created_at (auto)
     - cfp_is_open and accepts_submissions_now properties (parent meetup is_active + not archived + window/grace)
     - UniqueConstraint on (meetup, slug)
   - Register in meetups/admin.py

5. RED: Write tests for MeetupOptionalFieldConfig:
   - Add to meetups/tests/test_models.py:
     - Test that MeetupOptionalFieldConfig links a Meetup to a StandardOptionalField with is_enabled and is_required flags
     - Test that the unique constraint prevents duplicate configurations
     - Test a helper get_enabled_fields(meetup) returns only enabled standard fields for that meetup
     - Test the same standard field can be required on one meetup and optional on another

6. GREEN: Implement MeetupOptionalFieldConfig:
   - Add to meetups/models.py:
     - MeetupOptionalFieldConfig: meetup (FK), standard_field (FK → StandardOptionalField), is_enabled (BooleanField, default=True), is_required (BooleanField, default=False)
     - UniqueConstraint on (meetup, standard_field)
     - Add get_enabled_fields helper (manager method or module function)

7. RED: Write tests for CustomQuestion:
   - Create submissions/tests/__init__.py
   - Create submissions/tests/test_models.py:
     - Test CustomQuestion creation with meetup FK
     - Test CustomQuestion with event FK (scoped to event)
     - Test CustomQuestion with event=None (applies to meetup default CFP)
     - Test ordering by sort_order
     - Test deactivated question (is_active=False) is excluded by the active-questions helper but the row still exists

8. GREEN: Implement CustomQuestion model:
   - Create submissions/models.py (start of submissions app):
     - CustomQuestion model per spec:
       - meetup (FK → Meetup)
       - event (FK → Event, null=True, blank=True)
       - label, field_type (reusing FIELD_TYPE_CHOICES from core), is_required, options (JSONField), sort_order, is_active
     - Meta: ordering = ["sort_order"]

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations meetups submissions users`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 5: Submissions App — Submission & Field Response Models

**Validator consults:**
- Skills: python:python

**Goal**: Build the Submission, SubmissionMeetup, SubmissionFieldResponse, and FileUpload models. This is the data backbone for proposals.

```text
Prompt for code-generation LLM:

### Step 5: Submissions App — Submission & Field Response Models

Build the core submission data models. These store all proposal data and per-meetup tracking.

**NOTE**: Steps 1-4 are complete. Meetup, Event, CustomQuestion, GlobalFormField, StandardOptionalField all exist.

1. RED: Write tests for Submission model:
   - Update submissions/tests/test_models.py:
     - Test Submission creation with required fields (speaker_name, speaker_email, title, abstract, description, speaker_bio)
     - Test that withdrawal_token is auto-generated UUID v4 on creation and is unique
     - Test __str__ returns "{title} by {speaker_name}"

2. GREEN: Implement Submission model:
   - Update submissions/models.py:
     - STATUS_CHOICES: submitted, under_review, accepted, rejected, waitlisted, withdrawn, email_sent, speaker_accepted, scheduled, presented
     - Submission model per spec:
       - speaker_name, speaker_email (EmailField)
       - title, abstract (TextField), description (TextField), speaker_bio (TextField)
       - withdrawal_token (UUIDField, default=uuid4, unique=True, editable=False)
       - created_at, updated_at (auto)

3. RED: Write tests for SubmissionMeetup:
   - Add to submissions/tests/test_models.py:
     - Test SubmissionMeetup creation linking Submission to Meetup
     - Test the logical uniqueness rule: creating a second row with the same (submission, meetup, event=None) raises ValidationError via clean()
     - Test SubmissionMeetup with event=None (default meetup CFP) and with event set can coexist for the same submission and meetup
     - Test default status is "submitted"
     - Test scheduled_date is nullable

4. GREEN: Implement SubmissionMeetup model:
   - Add to submissions/models.py:
     - SubmissionMeetup:
       - submission (FK → Submission)
       - meetup (FK → Meetup)
       - event (FK → Event, null=True, blank=True)
       - status (CharField, choices=STATUS_CHOICES, default="submitted")
       - scheduled_date (DateField, null=True, blank=True)
       - created_at, updated_at (auto)
     - clean() enforcing the (submission, meetup, event) uniqueness rule treating NULL event as a value (matching nulls_distinct=False semantics), save() calls full_clean()
     - Add the DB-level UniqueConstraint with nulls_distinct=False in a migration that applies only on PostgreSQL (check connection.vendor in a RunPython/RunSQL guard) — SQLite dev/test relies on the clean() enforcement, PostgreSQL production gets the real constraint per spec

5. RED: Write tests for SubmissionFieldResponse:
   - Add to submissions/tests/test_models.py:
     - Test that exactly one of global_field, standard_field, custom_question must be set
     - Test that setting two FKs raises ValidationError (via clean method)
     - Test that setting zero FKs raises ValidationError
     - Test storing text response in value_text
     - Test storing a multi-select answer as a JSON list string in value_text

6. GREEN: Implement SubmissionFieldResponse model:
   - Add to submissions/models.py:
     - SubmissionFieldResponse:
       - submission (FK → Submission)
       - global_field (FK → GlobalFormField, null=True, blank=True)
       - standard_field (FK → StandardOptionalField, null=True, blank=True)
       - custom_question (FK → CustomQuestion, null=True, blank=True)
       - value_text (TextField, blank=True) — all non-file responses; NO value_file field (files live on FileUpload)
     - Override clean() to enforce exactly-one-FK, save() calls full_clean()
     - Add a CheckConstraint mirroring the exactly-one-FK rule

7. RED: Write tests for FileUpload model:
   - Add to submissions/tests/test_models.py:
     - Test FileUpload creation linked to Submission and one-to-one with SubmissionFieldResponse
     - Test original_filename, content_type, and size_bytes are stored correctly
     - Test a second FileUpload for the same field_response is rejected (OneToOneField)

8. GREEN: Implement FileUpload model:
   - Add to submissions/models.py:
     - FileUpload:
       - submission (FK → Submission)
       - field_response (OneToOneField → SubmissionFieldResponse)
       - file (FileField, upload_to="uploads/")
       - original_filename (CharField), content_type (CharField), size_bytes (PositiveBigIntegerField)
       - uploaded_at (auto)

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations submissions`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 6: Reviews App — Votes, Notes, Transition Table

**Validator consults:**
- Skills: python:python

**Goal**: Build the Review, Note, and StatusChange models plus the pure transition-table module. The transition module must be deterministic and side-effect free — the lifecycle workflow imports it in Step 9.

```text
Prompt for code-generation LLM:

### Step 6: Reviews App — Votes, Notes, Transition Table

Build the review infrastructure: votes, notes, the audit model, and the pure transition table.

**NOTE**: Steps 1-5 complete. All submission data models exist. STATUS_CHOICES defined in submissions app. IMPORTANT: reviews/transitions.py must be a pure module (constants and functions only, no Django imports, no I/O) because the Temporal lifecycle workflow imports it inside the workflow sandbox in Step 9.

1. RED: Write tests for the transition table:
   - Create reviews/tests/__init__.py
   - Create reviews/tests/test_transitions.py — encode the spec's normative table exactly:
     - Test allowed: submitted → under_review, submitted → withdrawn
     - Test allowed: under_review → accepted / rejected / waitlisted / withdrawn
     - Test allowed: waitlisted → accepted / rejected / under_review / withdrawn
     - Test allowed: rejected → under_review (undo), rejected → withdrawn
     - Test allowed: accepted → email_sent, accepted → under_review (undo), accepted → withdrawn
     - Test allowed: email_sent → speaker_accepted / withdrawn
     - Test allowed: speaker_accepted → scheduled / withdrawn
     - Test allowed: scheduled → presented, scheduled → speaker_accepted (unschedule), scheduled → withdrawn
     - Test terminal: presented and withdrawn allow nothing (including withdrawn → withdrawn)
     - Test disallowed samples: submitted → accepted, under_review → email_sent, presented → under_review
     - Test validate_transition("speaker_accepted", "scheduled", scheduled_date=None) raises TransitionError (date required)
     - Test validate_transition("speaker_accepted", "scheduled", scheduled_date=<date>) passes
     - Test validate_transition error message names the current status and the allowed targets
     - Test is_terminal("presented") and is_terminal("withdrawn") return True, others False

2. GREEN: Implement the pure transition module:
   - Create reviews/transitions.py (NO Django imports — pure Python):
     - VALID_TRANSITIONS dict matching the spec's normative table exactly (as tested above)
     - TransitionError exception (carries from_status, to_status, allowed list)
     - is_valid_transition(from_status, to_status) → bool
     - validate_transition(from_status, to_status, scheduled_date=None) → None or raises TransitionError (enforces the scheduled_date-required rule for → scheduled)
     - is_terminal(status) → bool
     - CLEARS_SCHEDULED_DATE rule: scheduled → speaker_accepted clears the date (expose a helper clears_scheduled_date(from_status, to_status) → bool)

3. RED: Write tests for the persistence service:
   - Create reviews/tests/test_persistence.py:
     - Test apply_transition(submission_meetup_id, new_status, actor_id, scheduled_date) updates SubmissionMeetup.status and creates a StatusChange row with old/new status
     - Test apply_transition with actor_id=None records changed_by=None (speaker withdrawal)
     - Test apply_transition to "scheduled" sets scheduled_date
     - Test apply_transition scheduled → speaker_accepted clears scheduled_date
     - Test apply_transition re-validates and raises TransitionError if the DB row's status doesn't allow the move (defense in depth — the workflow validator is the primary gate)

4. GREEN: Implement the persistence service:
   - Create reviews/persistence.py:
     - apply_transition(submission_meetup_id, new_status, actor_id=None, scheduled_date=None) → dict:
       - Load the row, validate via reviews/transitions.validate_transition
       - Update status (and scheduled_date per the rules) and create StatusChange, in one transaction.atomic block
       - Return a small dict: {"old_status": ..., "new_status": ...}
     - This function becomes the body of the persist activity in Step 9 — keep it callable with plain scalar arguments

5. RED: Write tests for Review (Vote) model:
   - Create reviews/tests/test_models.py:
     - Test Review creation with submission_meetup and reviewer
     - Test unique constraint prevents same reviewer voting twice on same submission_meetup
     - Test vote choices are thumbs_up and thumbs_down
     - Test record_vote helper updates the existing row on re-vote (latest vote wins, no second row)
     - Test vote_summary helper returns correct counts (e.g., {"thumbs_up": 3, "thumbs_down": 1})

6. GREEN: Implement Review model:
   - Create reviews/models.py:
     - VOTE_CHOICES: ("thumbs_up", "Thumbs Up"), ("thumbs_down", "Thumbs Down")
     - Review: submission_meetup (FK), reviewer (FK → CustomUser), vote (CharField), created_at, updated_at
     - UniqueConstraint on (submission_meetup, reviewer)
     - record_vote(submission_meetup, reviewer, vote) helper using update_or_create

7. GREEN: Implement Note and StatusChange models:
   - Add to reviews/models.py:
     - Note: submission_meetup (FK), author (FK → CustomUser), body (TextField), created_at; Meta ordering = ["created_at"]
     - StatusChange: submission_meetup (FK), changed_by (FK → CustomUser, null=True — null means speaker via token), old_status, new_status, changed_at (auto); Meta ordering = ["-changed_at"]

8. Run migrations and verify:
   - Run `uv run python manage.py makemigrations reviews`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 7: Permission System & Test Factories

**Validator consults:**
- Skills: python:python

**Goal**: Build comprehensive permission checks (including the role assignment matrix) and test factories for all models to make future testing easier.

```text
Prompt for code-generation LLM:

### Step 7: Permission System & Test Factories

Build test factories for all models and comprehensive permission integration tests.

**NOTE**: Steps 1-6 complete. All models exist. Basic permission functions exist in users/permissions.py. This step adds factories, the role assignment matrix, and thorough integration tests.

1. Create test factories for all models:
   - Create tests/__init__.py (project-level test utilities)
   - Create tests/factories.py:
     - UserFactory (sequential usernames/emails), SuperAdminFactory (is_superadmin=True)
     - OrganizationFactory, MeetupFactory (is_active=True, cfp_mode="year_round"), EventFactory
     - GlobalFormFieldFactory, StandardOptionalFieldFactory, MeetupOptionalFieldConfigFactory, CustomQuestionFactory
     - SubmissionFactory, SubmissionMeetupFactory, MeetupRoleFactory, ReviewFactory, NoteFactory, StatusChangeFactory

2. RED: Write integration tests for permission checks across all role levels:
   - Create users/tests/test_permissions_integration.py:
     - Test that a "read" user can view submissions but cannot vote, add notes, or change status
     - Test that a "reviewer" user can view, vote, and add notes, but cannot change status or export
     - Test that a "write" user can additionally change status, run bulk actions, and export
     - Test that an "admin" user can additionally edit meetup settings and manage events/custom questions
     - Test that a super-admin passes every check on any meetup without an explicit role
     - Test that a user with "admin" on meetup A and "read" on meetup B gets correct permissions on each
     - Test that a user with no role on a meetup fails every check for it

3. RED: Write tests for the role assignment matrix:
   - Add to users/tests/test_permissions_integration.py:
     - Test can_assign_role(super_admin, meetup, "admin") is True (super-admin assigns anything)
     - Test can_assign_role(admin_user, meetup, "write"/"reviewer"/"read") is True
     - Test can_assign_role(admin_user, meetup, "admin") is False (never at or above own rank)
     - Test can_assign_role(write_user, meetup, "reviewer") is True
     - Test can_assign_role(write_user, meetup, "write"/"read") is False (Write assigns Reviewer only, per spec)
     - Test can_assign_role(reviewer_user, meetup, anything) is False

4. GREEN: Create helper functions for common permission checks:
   - Update users/permissions.py:
     - can_view_submissions(user, meetup) → bool (read+)
     - can_vote(user, meetup) → bool (reviewer+)
     - can_add_notes(user, meetup) → bool (reviewer+)
     - can_manage_submissions(user, meetup) → bool (write+)
     - can_export(user, meetup) → bool (write+)
     - can_manage_meetup_settings(user, meetup) → bool (admin+)
     - can_manage_events(user, meetup) → bool (admin+)
     - can_assign_role(user, meetup, target_role) → bool implementing the assignment matrix (super-admin: any; admin: write/reviewer/read; write: reviewer only; below write: nothing)
     - is_super_admin(user) → bool

5. REFACTOR: Ensure all permission functions are clean:
   - All use the hierarchy comparison, super-admin bypass is consistent, no duplication

6. Run `just check` to verify all tests pass
```

---

## Step 8: Temporal Foundation — Client, Worker, Test Harness

**Validator consults:**
- MCPs: mcp__temporal-docs__search_temporal_knowledge_sources
- Skills: temporal:temporal-developer, python:python

**Goal**: Stand up the Temporal plumbing: client helper, the `run_worker` management command, and the async test harness. Ends with a trivial round-trip workflow test proving the harness works, which is deleted or kept as a smoke test.

```text
Prompt for code-generation LLM:

### Step 8: Temporal Foundation — Client, Worker, Test Harness

Stand up the Temporal client, worker entrypoint, and test harness. No business workflows yet.

**NOTE**: Steps 1-7 complete. temporalio and pytest-asyncio are installed (Step 1). TEMPORAL_ADDRESS / TEMPORAL_NAMESPACE / TEMPORAL_TASK_QUEUE settings exist. Follow the temporal-developer skill's Python guidance: sync activities on a ThreadPoolExecutor, workflows in separate modules from activities, workflow modules import activities via workflow.unsafe.imports_passed_through().

1. GREEN: Create the client helper (no test — thin configuration wiring):
   - Create core/temporal.py:
     - async get_temporal_client() → temporalio.client.Client:
       - Connect using settings.TEMPORAL_ADDRESS and settings.TEMPORAL_NAMESPACE
       - Cache the client instance per process (module-level, lazily created)
     - TASK_QUEUE constant read from settings.TEMPORAL_TASK_QUEUE
     - sync_execute(coro) helper that runs an awaitable from synchronous Django view code (asgiref async_to_sync)

2. GREEN: Create the worker registry and run_worker command:
   - Create core/worker.py:
     - WORKFLOWS: list = [] and ACTIVITIES: list = [] — central registry appended to in Steps 9-11
     - build_worker(client) → Worker configured with task_queue from settings, workflows=WORKFLOWS, activities=ACTIVITIES, and a ThreadPoolExecutor(max_workers=…) as activity_executor (activities are sync functions using the Django ORM)
   - Create core/management/commands/run_worker.py:
     - Connects via get_temporal_client(), builds the worker, runs it until interrupted (asyncio.run)

3. RED: Write a harness smoke test:
   - Create core/tests/test_temporal_harness.py:
     - Using temporalio.testing.WorkflowEnvironment.start_time_skipping():
       - Define a trivial inline echo workflow in the test module
       - Run a Worker for it on a test task queue and execute it, asserting the result round-trips
     - This test exists to prove the async test harness, sandbox, and worker wiring function — keep it as the Temporal smoke test

4. GREEN: Make the smoke test pass:
   - Fix pytest-asyncio configuration (asyncio_mode="auto" from Step 1), event-loop scope, or sandbox passthrough issues until the smoke test passes
   - Note: WorkflowEnvironment downloads a test server binary on first run; if the environment blocks downloads, document using `temporal server start-dev` plus WorkflowEnvironment.from_client as fallback

5. Wire up and verify:
   - Add `worker` recipe to Justfile if not present: `uv run python manage.py run_worker`
   - Run `just check`
```

---

## Step 9: Submission Lifecycle Workflow & Transition Service

**Validator consults:**
- MCPs: mcp__temporal-docs__search_temporal_knowledge_sources
- Skills: temporal:temporal-developer, python:python

**Goal**: The heart of the Temporal architecture: one entity workflow per SubmissionMeetup owning the status state machine, with `request_transition` as a workflow Update validated against the transition table. Ends with the Django-side service that delivers transitions via update-with-start.

```text
Prompt for code-generation LLM:

### Step 9: Submission Lifecycle Workflow & Transition Service

Build SubmissionLifecycleWorkflow (entity workflow per SubmissionMeetup) and the Django service that sends transitions to it.

**NOTE**: Steps 1-8 complete. reviews/transitions.py is pure (workflow-safe) and reviews/persistence.py has apply_transition. The worker registry exists in core/worker.py. Workflow IDs: "lifecycle-{submission_meetup_id}". Per spec: the update validator enforces the normative table; rejected updates never enter history and write no audit row; terminal statuses complete the workflow.

1. GREEN: Create the persist activity (thin wrapper, logic already tested in Step 6):
   - Create reviews/activities.py:
     - @activity.defn persist_transition(input: PersistTransitionInput) → PersistTransitionResult:
       - Dataclass input: submission_meetup_id, new_status, actor_id (int | None), scheduled_date (str | None, ISO date)
       - Calls reviews/persistence.apply_transition (sync, Django ORM — runs on the activity thread pool)
   - Define the dataclasses in reviews/messages.py (shared by workflow and Django code; keep it Django-free so the sandbox can import it)

2. RED: Write workflow tests:
   - Create reviews/tests/test_lifecycle_workflow.py (async tests, WorkflowEnvironment.start_time_skipping, mocked activities):
     - Test a legal transition: start workflow with initial_status="submitted", send request_transition(new_status="under_review", actor_id=1) — the mocked persist_transition activity is called once with the right input and the update returns the new status
     - Test an illegal transition: request_transition(new_status="presented") from "submitted" is REJECTED by the update validator — the caller gets an error naming current status and allowed targets, and the mocked activity was NEVER called
     - Test scheduled_date rule: request_transition to "scheduled" without a date is rejected by the validator; with a date it succeeds
     - Test unschedule: from "scheduled", request_transition to "speaker_accepted" succeeds (persist activity receives scheduled_date=None per the clears rule)
     - Test terminal completion: transitioning to "withdrawn" (and separately to "presented") causes the workflow to complete
     - Test the current_status query returns the workflow's tracked status after transitions
     - Test webhook scheduling hook: after a persisted transition the workflow records a pending webhook delivery (in Step 9 this is a no-op list in state; Step 11 turns it into an activity — assert the state via query or by workflow completion result)

3. GREEN: Implement the lifecycle workflow:
   - Create reviews/workflows.py:
     - Import activities and reviews.transitions via workflow.unsafe.imports_passed_through()
     - @workflow.defn class SubmissionLifecycleWorkflow:
       - @workflow.init __init__(self, input: LifecycleInput) — dataclass input: submission_meetup_id, initial_status (state initialized before any update arrives, per SDK guidance)
       - @workflow.run run(input) → waits with workflow.wait_condition until is_terminal(self.status), then returns final status
       - @workflow.update request_transition(req: TransitionRequest) → TransitionResult:
         - Executes persist_transition activity (start_to_close_timeout ~30s), updates self.status, appends any webhook delivery to a pending list (processed by the main loop in Step 11)
       - @request_transition.validator validate_request(req): calls reviews.transitions.validate_transition(self.status, req.new_status, req.scheduled_date) — raise to reject; validators must not mutate state or run activities
       - @workflow.query current_status() → str
   - Register SubmissionLifecycleWorkflow and persist_transition in core/worker.py registries

4. RED: Write tests for the Django-side transition service:
   - Create reviews/tests/test_services.py:
     - Test request_transition service builds workflow id "lifecycle-{id}" and uses update-with-start (execute_update_with_start / start-if-not-running semantics) passing initial_status from the DB row — so rows without a running workflow (seed data, completed workflows) self-heal
     - Test a rejected update surfaces as a domain TransitionRejected error carrying the validator's message (translate the SDK's update-failed error)
     - Test actor propagation: authenticated user id passed through; None for speaker withdrawal
     - Mock the Temporal client at the service boundary — the workflow behavior itself is covered by the tests in sub-step 2

5. GREEN: Implement the transition service:
   - Create reviews/services.py:
     - request_transition(submission_meetup, new_status, actor=None, scheduled_date=None) → dict:
       - Reads submission_meetup.status as initial_status for the start branch
       - Uses core/temporal.get_temporal_client + sync_execute to run the update-with-start against workflow id "lifecycle-{submission_meetup.id}"
       - Translates WorkflowUpdateFailedError into TransitionRejected (message names current status and allowed targets, per the access/error contract)
     - This is the ONLY path Django code may use to change a submission status

6. REFACTOR: Confirm module hygiene:
   - reviews/workflows.py contains only the workflow class; reviews/activities.py only activities; reviews/messages.py only dataclasses
   - Run `just check`
```

---

## Step 10: Submission Intake Workflow & Intake Service

**Validator consults:**
- MCPs: mcp__temporal-docs__search_temporal_knowledge_sources
- Skills: temporal:temporal-developer, python:python

**Goal**: The durable intake path: one activity persists all records in a single transaction, then lifecycle workflows start per target. Ends with the Django-side service the submission views call in Step 14.

```text
Prompt for code-generation LLM:

### Step 10: Submission Intake Workflow & Intake Service

Build SubmissionIntakeWorkflow and the intake service. Views wire in at Step 14.

**NOTE**: Steps 1-9 complete. Lifecycle workflow works. Workflow IDs: "intake-{submission_uuid}" where submission_uuid is generated by the caller before starting (it becomes the withdrawal_token). LARGE DATA RULE: uploaded file contents never flow through workflow history — the view saves files to media storage first and passes storage paths in the intake input.

1. RED: Write tests for the persist activity's service function:
   - Create submissions/tests/test_intake_persistence.py:
     - Test persist_intake(payload) creates Submission (with the provided withdrawal_token), one SubmissionMeetup per target, SubmissionFieldResponse rows for optional/custom answers, and FileUpload rows for provided storage paths — all in ONE transaction
     - Test the returned payload lists submission_meetup_ids with their meetup ids and initial status "submitted"
     - Test idempotency: calling persist_intake twice with the same withdrawal_token does not duplicate rows (get_or_create keyed on the token) — activities must be safely retryable
     - Test a mid-payload integrity error rolls back everything (no partial rows)

2. GREEN: Implement intake persistence:
   - Create submissions/persistence.py:
     - persist_intake(payload: dict) → dict, wrapped in transaction.atomic, idempotent on withdrawal_token
   - Create submissions/activities.py:
     - @activity.defn persist_submission(input) wrapping persist_intake
   - Create submissions/messages.py with the intake dataclasses (Django-free): IntakeInput (speaker fields, core answers, targets [{meetup_id, event_id}], field answers, file references [{field_ref, storage_path, original_filename, content_type, size_bytes}], withdrawal_token), IntakeResult (submission_id, submission_meetup_ids, webhook targets)

3. RED: Write intake workflow tests:
   - Create submissions/tests/test_intake_workflow.py (WorkflowEnvironment, mocked persist activity):
     - Test the workflow calls persist_submission once, then starts one SubmissionLifecycleWorkflow child per submission_meetup_id with workflow id "lifecycle-{id}", parent_close_policy=ABANDON (children outlive the intake workflow)
     - Test each child receives initial_status="submitted"
     - Test duplicate intake start: executing the workflow twice with the same workflow id is a no-op the second time (workflow id reuse policy) — assert only one persist call across both attempts
     - Test the workflow result carries submission_id and the confirmation data the view needs
     - Test webhook scheduling hook: targets with a webhook_url are recorded for submission.received delivery (no-op list until Step 11)

4. GREEN: Implement the intake workflow:
   - Create submissions/workflows.py:
     - @workflow.defn class SubmissionIntakeWorkflow:
       - @workflow.run run(input: IntakeInput) → IntakeResult:
         - Execute persist_submission activity (start_to_close_timeout ~30s)
         - For each submission_meetup_id: start_child_workflow(SubmissionLifecycleWorkflow, id="lifecycle-{id}", parent_close_policy=ABANDON); treat already-started as success
         - Record pending submission.received webhook deliveries (activity wired in Step 11)
         - Return IntakeResult
   - Register workflow and activity in core/worker.py

5. RED: Write tests for the Django-side intake service:
   - Create submissions/tests/test_intake_service.py:
     - Test start_intake(validated_data) generates the withdrawal_token, saves uploaded files to media storage, builds IntakeInput with storage paths (never raw bytes), starts "intake-{token}" and returns the workflow result
     - Test the service passes each target's webhook_url presence through to the input (meetup lookup)
     - Mock the Temporal client at the service boundary

6. GREEN: Implement the intake service:
   - Create submissions/services.py:
     - start_intake(validated_form_data, targets, uploaded_files) → IntakeResult:
       - uuid4 withdrawal_token, persist files via default_storage, build IntakeInput, execute the workflow synchronously via sync_execute (the view waits for the result to render confirmation, per spec)

7. Run `just check`
```

---

## Step 11: Webhook Delivery

**Validator consults:**
- MCPs: mcp__temporal-docs__search_temporal_knowledge_sources
- Skills: temporal:temporal-developer, python:python

**Goal**: Per-meetup webhook notifications: payload builder, HMAC signing, the delivery activity with a retry policy, wired into both workflows. Delivery never blocks or rolls back a transition.

```text
Prompt for code-generation LLM:

### Step 11: Webhook Delivery

Build webhook payloads, signing, and the delivery activity; wire delivery into the intake and lifecycle workflows.

**NOTE**: Steps 1-10 complete. Both workflows track pending webhook deliveries as state. Spec contract: events are "submission.received" and "submission.status_changed" (every applied transition, including speaker withdrawal); payload has event, meetup slug, event_slug (nullable), submission (id, title, speaker name — NO speaker email), old_status/new_status for status changes, ISO 8601 occurred_at; X-CFP-Signature header (hex HMAC-SHA256 of the body) exactly when webhook_secret is set; retries with exponential backoff capped at roughly 24 hours; failure never blocks the transition.

1. RED: Write tests for payload building and signing:
   - Create meetups/tests/test_webhooks.py:
     - Test build_payload("submission.received", …) produces the exact key set: event, meetup, event_slug, submission {id, title, speaker_name}, occurred_at — and NO speaker_email anywhere
     - Test build_payload("submission.status_changed", …) additionally carries old_status and new_status
     - Test occurred_at is ISO 8601
     - Test sign_payload(body, secret) returns hex HMAC-SHA256 and matches a known vector
     - Test build_headers includes X-CFP-Signature exactly when a secret is provided, omits it otherwise

2. GREEN: Implement payload building and signing:
   - Create meetups/webhooks.py (pure functions):
     - build_payload(event, meetup_slug, event_slug, submission_data, old_status=None, new_status=None, occurred_at=…) → dict
     - sign_payload(body_bytes, secret) → str
     - build_headers(body_bytes, secret | None) → dict

3. RED: Write tests for the delivery activity function:
   - Add to meetups/tests/test_webhooks.py:
     - Test deliver(url, payload, secret) POSTs JSON with the signature header (mock httpx)
     - Test a non-2xx response raises (so Temporal retries per policy)
     - Test no delivery is attempted (and the workflow never schedules the activity) when webhook_url is unset — covered again at the workflow level below

4. GREEN: Implement the delivery activity:
   - Add to meetups/activities.py:
     - @activity.defn deliver_webhook(input: WebhookDeliveryInput): sync httpx POST, raise on non-2xx
     - WebhookDeliveryInput dataclass in meetups/messages.py: url, secret (optional), payload dict
   - Define WEBHOOK_RETRY_POLICY (module constant next to the workflows that use it): exponential backoff, initial interval ~5s, backoff coefficient 2, maximum interval ~1h, maximum attempts sized to span roughly 24 hours

5. RED: Write workflow integration tests:
   - Update reviews/tests/test_lifecycle_workflow.py:
     - Test an applied transition on a meetup WITH webhook_url schedules deliver_webhook with a submission.status_changed payload (mock the activity, assert input)
     - Test a meetup WITHOUT webhook_url schedules nothing
     - Test the update result returns as soon as persist_transition completes — a slow/failing webhook activity does not delay or fail the update (deliver in the workflow main loop from the pending list, wrap in try/except so exhausted retries are logged, never raised)
   - Update submissions/tests/test_intake_workflow.py:
     - Test intake schedules one submission.received delivery per target meetup with a webhook_url configured
     - Test intake completes successfully even when a delivery activity fails permanently

6. GREEN: Wire delivery into both workflows:
   - reviews/workflows.py: after persist_transition, enqueue the delivery; the main run loop drains pending deliveries via execute_activity(deliver_webhook, retry_policy=WEBHOOK_RETRY_POLICY) guarded by try/except; workflow completes only after terminal status AND pending deliveries have been attempted
   - submissions/workflows.py: same drain pattern for submission.received
   - The persist activity result must carry the data the payload needs (meetup slug, event slug, webhook config, submission title/speaker name) so the workflow never queries the DB directly

7. Run `just check`
```

---

## Step 12: Public Pages — Org Landing & Meetup Pages

**Validator consults:**
- Skills: python:python

**Goal**: Build the public-facing read-only pages: organization landing page, individual meetup pages, and event pages. No submission forms yet — just the display.

```text
Prompt for code-generation LLM:

### Step 12: Public Pages — Org Landing & Meetup Pages

Build the public-facing pages for browsing meetups. Forms come in later steps.

**NOTE**: Steps 1-11 complete. All models, permissions, factories, and workflows exist. There's a minimal base template from Step 1.

1. Set up Tailwind CSS:
   - Run `uv run python manage.py tailwind build` to generate initial CSS
   - Update templates/base.html:
     - Add the tailwind_cli template tags in <head>
     - Add basic layout structure: nav, main content area, footer
     - Add HTMX and Alpine.js script tags (vendored static files or CDN for now)
   - Configure static file handling for the Tailwind output

2. RED: Write view tests for the org landing page:
   - Create core/tests/test_views.py:
     - Test GET "/" returns 200
     - Test the page shows the organization name (singleton always exists via data migration)
     - Test the page lists only active meetups
     - Test deactivated meetups are NOT shown
     - Test meetups with open CFP show a visual indicator
     - Test the "Submit to Multiple Meetups" link is present

3. GREEN: Implement org landing page:
   - Create core/views.py:
     - OrgLandingView: Organization singleton + active meetups → template
   - Create templates/core/landing.html:
     - Organization name, logo, description; active meetups linking to /meetups/{slug}/; "Submit to Multiple Meetups" button linking to /submit/
   - Wire up in meetup_cfp/urls.py: path("", OrgLandingView, name="landing")

4. RED: Write view tests for meetup page:
   - Create meetups/tests/test_views.py:
     - Test GET "/meetups/{slug}/" returns 200 for active meetup
     - Test 404 for deactivated meetup and for non-existent slug
     - Test page shows meetup name and description
     - Test page shows "CFP Closed" message when CFP is not open (cfp_is_open drives display — grace does NOT keep the form rendered)
     - Test page uses meetup branding if set, falls back to org branding (effective_* properties)

5. GREEN: Implement meetup page:
   - Create meetups/views.py:
     - MeetupDetailView: look up active Meetup by slug (404 otherwise), pass cfp_is_open to template
   - Create templates/meetups/detail.html: name, logo, description; form placeholder when open, closed message otherwise
   - Wire up: path("meetups/<slug:slug>/", ...)

6. RED: Write view tests for event page:
   - Add to meetups/tests/test_views.py:
     - Test GET "/meetups/{meetup_slug}/events/{event_slug}/" returns 200
     - Test page shows event name, description, date, and CFP open/close dates
     - Test 404 for non-existent event slug and for deactivated parent meetup
     - Test archived event shows "Archived" message and no form (200, not 404)
     - Test closed-CFP event shows a message instead of the form

7. GREEN: Implement event page:
   - Add EventDetailView to meetups/views.py; create templates/meetups/event_detail.html
   - Wire up: path("meetups/<slug:meetup_slug>/events/<slug:event_slug>/", ...)

8. Run `just check`
```

---

## Step 13: Dynamic Multi-Submit Form (HTMX)

**Validator consults:**
- Skills: python:python

**Goal**: Build the multi-submit form with HTMX-powered dynamic field loading. This is the most complex frontend interaction.

```text
Prompt for code-generation LLM:

### Step 13: Dynamic Multi-Submit Form (HTMX)

Build the multi-submit form at /submit/ with HTMX dynamic field loading.

**NOTE**: Steps 1-12 complete. Public pages exist. HTMX and Alpine.js are in the base template.

1. RED: Write tests for the dynamic field assembly logic:
   - Create submissions/tests/test_form_assembly.py:
     - Test get_dynamic_fields([meetup_a]) returns meetup_a's enabled optional fields and custom questions
     - Test get_dynamic_fields([meetup_a, meetup_b]) returns UNION of optional fields (no duplicates) when both meetups enable the same field
     - Test the required flag is ORed: a field required by ANY selected meetup is marked required in the result
     - Test custom questions are grouped by meetup
     - Test get_dynamic_fields with no meetups returns empty results
     - Test inactive custom questions are excluded
     - Test event-scoped custom questions are excluded (multi-submit never includes events)

2. GREEN: Implement dynamic field assembly:
   - Create submissions/form_assembly.py:
     - get_dynamic_fields(meetup_ids) → dict:
       - "optional_fields": list of {field, is_required} where is_required is ORed across the selected meetups' MeetupOptionalFieldConfig rows
       - "custom_questions": dict of {meetup: [CustomQuestion, ...]} (meetup-level only, is_active=True)

3. RED: Write tests for the HTMX dynamic fields endpoint:
   - Create submissions/tests/test_views.py:
     - Test POST "/submit/dynamic-fields/" with open-CFP meetup ids returns 200 with the HTML fragment (partial, not a full page)
     - Test the fragment contains the union optional fields and custom questions grouped by meetup name
     - Test required-if-any-requires marking appears in the fragment
     - Test tampered input returns 400 with an empty-fragment error: unknown meetup id, inactive meetup, closed-CFP meetup
     - Test empty selection returns an empty fragment (200)

4. GREEN: Implement HTMX dynamic fields endpoint:
   - Create submissions/views.py:
     - dynamic_fields_view: parse meetup_ids, reject tampered ids with 400, render submissions/partials/dynamic_fields.html
   - Create templates/submissions/partials/dynamic_fields.html: inputs by field_type (text, textarea, email, url, select, multi-select, file), custom questions under meetup headings
   - Wire up: path("submit/dynamic-fields/", ...)

5. GREEN: Build the multi-submit form page:
   - Add MultiSubmitView (GET): global core fields + checkboxes for each active meetup with an OPEN CFP
   - Create templates/submissions/multi_submit.html:
     - Global required fields always visible
     - Meetup checkboxes with hx-post="/submit/dynamic-fields/", hx-trigger="change", hx-target="#dynamic-fields", hx-include on the checkbox group
     - "Select All" button (Alpine.js — Alpine is a confirmed keeper per spec)
     - <div id="dynamic-fields"></div> target, CAPTCHA placeholder, file-input re-select notice placeholder, submit button
   - Wire up: path("submit/", ...)

6. GREEN: Build single-meetup and event submission forms:
   - MeetupDetailView passes global + enabled optional + meetup default-CFP custom questions when CFP is open
   - EventDetailView passes global + meetup's enabled optional + THE EVENT'S custom questions (never the meetup's default-CFP questions)
   - Templates: templates/submissions/meetup_submit_form.html and event_submit_form.html (included by the detail pages), each with CAPTCHA placeholder and hidden target identifier

7. Run `just check`
```

---

## Step 14: Submission Validation & Intake Wiring

**Validator consults:**
- Skills: python:python

**Goal**: Make the forms functional: validation (duplicates excluding withdrawn, CFP windows with grace, file limits), CAPTCHA verification, and wiring the POST handlers to the intake service from Step 10.

```text
Prompt for code-generation LLM:

### Step 14: Submission Validation & Intake Wiring

Implement submission processing: validation, duplicate detection, CAPTCHA, and record creation through the intake workflow.

**NOTE**: Steps 1-13 complete. Forms render. submissions/services.start_intake exists and starts SubmissionIntakeWorkflow. Views must NOT create submission rows directly — validation happens in the view, persistence happens in the workflow's activity.

1. RED: Write tests for duplicate detection logic:
   - Create submissions/tests/test_validation.py:
     - Test detect_duplicate returns True when same email + title + meetup (event=None) already exists
     - Test normalization: email and title matching is case-insensitive and whitespace-trimmed
     - Test returns False for same email + title but DIFFERENT meetup (multi-submit is allowed)
     - Test returns False for a meetup's default CFP when the existing row targets one of its events (independent targets)
     - Test returns True for same (meetup, event) pair on event submissions
     - Test a WITHDRAWN row does NOT count as a duplicate (withdraw-and-resubmit is supported, per spec)

2. GREEN: Implement duplicate detection:
   - Create submissions/validation.py:
     - detect_duplicates(email, title, targets) → list of conflicting target descriptors:
       - Normalize email/title (lower, strip)
       - Query SubmissionMeetup joined to Submission per (meetup, event) target
       - EXCLUDE rows with status="withdrawn"
       - Return the conflicting targets so the form error can name them

3. RED: Write tests for CFP window enforcement (submit-time):
   - Add to submissions/tests/test_validation.py:
     - Test validate_targets_open passes for open CFPs
     - Test raises listing the closed target for: closed time-boxed meetup, deactivated meetup, archived event, closed event
     - Test grace period: a time-boxed meetup past cfp_close_date but within grace_period_minutes PASSES
     - Test past close + grace fails
     - Test deactivation and archival have NO grace (deactivated meetup within its grace window still fails)
     - Test all-or-nothing: one closed target among several open ones rejects the whole set, naming the closed one

4. GREEN: Implement CFP validation:
   - Add to submissions/validation.py:
     - validate_targets_open(targets) using Meetup.accepts_submissions_now / Event.accepts_submissions_now — raises ValidationError naming which target(s) closed

5. RED: Write tests for file validation and CAPTCHA:
   - Add to submissions/tests/test_validation.py:
     - Test validate_upload rejects files over 10 MB with a field-level error naming the limit
     - Test validate_upload rejects disallowed types (allowed: jpg, jpeg, png, webp, pdf)
     - Test headshot-labeled fields accept image types only (a PDF on a headshot field is rejected)
   - Create submissions/tests/test_captcha.py:
     - Test verify_captcha returns True/False based on the provider response (mock httpx)
     - Test the dummy backend used under tests always passes when configured

6. GREEN: Implement file validation and CAPTCHA verification:
   - Add validate_upload to submissions/validation.py (size, extension/content_type, headshot image-only rule)
   - Create submissions/captcha.py:
     - verify_captcha(token, remote_ip) → bool posting to the provider verify endpoint (hCaptcha or Turnstile, keys from settings)
     - A dummy backend selected via settings for tests/dev without keys

7. RED: Write tests for the form submission views:
   - Add to submissions/tests/test_views.py:
     - Test POST "/submit/" with valid data calls start_intake (mock it), then renders confirmation with the withdrawal link
     - Test POST with missing required global fields re-renders with errors, creates nothing, intake never called
     - Test required-if-any-requires enforcement across selected meetups; required custom questions per meetup enforced
     - Test duplicate conflict re-renders naming the conflicting meetup/event
     - Test no-meetup-selected re-renders with a validation error
     - Test CAPTCHA failure re-renders with an error, non-file inputs preserved, intake never called
     - Test closed-CFP target (race condition) rejects all-or-nothing with the target named
     - Test POST to "/meetups/{slug}/" (single-meetup) and to the event URL work the same way with their scoped field sets

8. GREEN: Implement form submission POST handlers:
   - Update submissions/views.py:
     - MultiSubmitView POST: assemble targets, run all validation (fields, files, CAPTCHA, duplicates, windows), then submissions/services.start_intake; success renders confirmation (withdrawal link prominent); any failure re-renders with errors and preserved non-file inputs
     - meetup_submit and event_submit POST handlers sharing the same validation pipeline
     - SubmitConfirmationView with the withdrawal URL
   - Wire up all URLs

9. Run `just check`
```

---

## Step 15: Withdrawal Flow

**Validator consults:**
- Skills: python:python

**Goal**: Implement the speaker withdrawal flow using UUID tokens. Withdrawals are transitions: they go through the Step 9 transition service, with `actor=None`.

```text
Prompt for code-generation LLM:

### Step 15: Withdrawal Flow

Implement the speaker withdrawal system with UUID-based secret URLs, delivering withdrawals as workflow transitions.

**NOTE**: Steps 1-14 complete. Submissions are created via the intake workflow. reviews/services.request_transition exists (update-with-start; actor=None produces changed_by=None on the audit row).

1. RED: Write tests for withdrawal logic:
   - Create submissions/tests/test_withdrawal.py:
     - Test get_submission_by_token returns the Submission for a valid token, None for invalid
     - Test get_withdrawal_context lists every SubmissionMeetup with meetup/event name, status, and an is_actionable flag (False for "withdrawn" and "presented")
     - Test withdraw_targets calls reviews/services.request_transition(new_status="withdrawn", actor=None) once per selected actionable target (mock the service)
     - Test withdraw_targets skips already-withdrawn and presented targets even if their ids are posted (defense against tampering)
     - Test withdraw_targets ignores submission_meetup ids that don't belong to this submission

2. GREEN: Implement withdrawal logic:
   - Create submissions/withdrawal.py:
     - get_submission_by_token(token) → Submission | None
     - get_withdrawal_context(submission) → list of dicts
     - withdraw_targets(submission, submission_meetup_ids) → results, routing each through reviews/services.request_transition with actor=None

3. RED: Write tests for withdrawal views:
   - Create submissions/tests/test_withdrawal_views.py:
     - Test GET "/withdraw/{token}/" returns 200 showing talk title and speaker name
     - Test GET with unknown or malformed token returns 404
     - Test the page lists all targets with checkboxes; withdrawn/presented entries rendered disabled
     - Test POST with selected targets withdraws them and shows confirmation
     - Test POST with no selections shows an error

4. GREEN: Implement withdrawal views:
   - Add WithdrawalView (GET form / POST process) and confirmation rendering to submissions/views.py
   - Create templates/submissions/withdrawal.html (disabled checkboxes for non-actionable entries) and withdrawal_confirmation.html
   - Wire up: path("withdraw/<uuid:token>/", ...)

5. Run `just check`
```

---

## Step 16: Dashboard — Authentication & Layout

**Validator consults:**
- Skills: python:python

**Goal**: Set up django-allauth authentication, dashboard base template, and the authenticated layout with navigation, honoring the access error contract.

```text
Prompt for code-generation LLM:

### Step 16: Dashboard — Authentication & Layout

Set up authentication with django-allauth and the dashboard shell.

**NOTE**: Steps 1-15 complete. Public pages and submission flow work. CustomUser has is_superadmin. MeetupRole and permission helpers exist.

1. Configure django-allauth:
   - Update meetup_cfp/settings/base.py:
     - INSTALLED_APPS: allauth, allauth.account, allauth.socialaccount, providers.github, providers.google
     - allauth.account.middleware.AccountMiddleware in MIDDLEWARE (required by allauth 65.x)
     - Email-based auth settings; SOCIALACCOUNT_PROVIDERS reading client ids/secrets from env
     - LOGIN_URL = "/accounts/login/", LOGIN_REDIRECT_URL = "/dashboard/"
   - Add to meetup_cfp/urls.py: path("accounts/", include("allauth.urls"))

2. RED: Write tests for dashboard access control (the spec's access error contract):
   - Create dashboard/tests/__init__.py
   - Create dashboard/tests/test_views.py:
     - Test GET "/dashboard/" redirects to login for anonymous users
     - Test GET "/dashboard/" returns 200 for super-admin (summary view)
     - Test GET "/dashboard/" for an authenticated non-super-admin shows their meetup list, NOT the super-admin summary
     - Test an authenticated user with no roles anywhere gets a 200 empty state listing no meetups (per spec — not a 403)
     - Test GET "/dashboard/meetups/{slug}/" returns 200 for user with a role on that meetup
     - Test 403 for an authenticated user with no role on that meetup
     - Test 200 for super-admin without an explicit role

3. GREEN: Implement dashboard base views:
   - Create dashboard/views.py:
     - DashboardHomeView (LoginRequiredMixin): super-admin → summary shell; others → list of their meetups (empty state when none)
     - MeetupDashboardView (LoginRequiredMixin + MeetupRoleRequiredMixin, required_role="read"): shell
   - Create templates/dashboard/base.html (nav: home, user's meetups, logout, role badge), home.html, meetup_dashboard.html (shell)
   - Wire up: path("dashboard/", ...), path("dashboard/meetups/<slug:slug>/", ...)

4. REFACTOR: Create allauth template overrides for consistent styling:
   - templates/account/login.html, signup.html, logout.html (extend base.html, Tailwind styled)

5. Run `just check`
```

---

## Step 17: Dashboard — Meetup Submissions View

**Validator consults:**
- Skills: python:python

**Goal**: Build the submissions table view with filtering, sorting, and search. This is the main working view for organizers.

```text
Prompt for code-generation LLM:

### Step 17: Dashboard — Meetup Submissions View

Build the submissions table with filtering, sorting, and search for the meetup dashboard.

**NOTE**: Steps 1-16 complete. Dashboard shell exists with auth. All models and factories available.

1. RED: Write tests for submission filtering logic:
   - Create dashboard/tests/test_filters.py:
     - Test filter_submissions with no filters returns all submission-meetups for a meetup
     - Test filter by status returns only matching rows
     - Test filter by date range (submitted after/before)
     - Test search by title and by speaker name (case-insensitive partial match)
     - Test sorting by submitted date (asc/desc), by title, and by vote count
     - Test vote count annotations (thumbs_up_count, thumbs_down_count) are correct
     - Test combining filters: status + date range + search

2. GREEN: Implement submission filtering:
   - Create dashboard/filters.py:
     - filter_submissions(meetup, params) → QuerySet over SubmissionMeetup with select_related("submission") and vote-count annotations, applying status/date/search/sort parameters

3. RED: Write tests for the submissions list view:
   - Add to dashboard/tests/test_views.py:
     - Test the meetup dashboard shows the submissions table with columns: Title, Speaker, Status, Submitted Date, Scheduled Date, Vote Summary
     - Test filter parameters in the URL change the rows displayed
     - Test pagination (25 per page)
     - Test Write+ users see bulk action checkboxes and the export button; Read/Reviewer users see neither

4. GREEN: Implement submissions list view:
   - Update MeetupDashboardView to use filter_submissions, paginate, and pass the user's role
   - Update templates/dashboard/meetup_dashboard.html: filter controls (status dropdown, date pickers, search box) via HTMX table-fragment reload; table per spec; conditional bulk checkboxes and export button; pagination

5. Run `just check`
```

---

## Step 18: Dashboard — Submission Detail & Reviews

**Validator consults:**
- Skills: python:python

**Goal**: Build the submission detail page with voting, notes, status controls (through the transition service), history, and the other-meetups panel.

```text
Prompt for code-generation LLM:

### Step 18: Dashboard — Submission Detail & Reviews

Build the submission detail page with all review functionality. Status changes go through reviews/services.request_transition — never direct status writes.

**NOTE**: Steps 1-17 complete. Submission list view works. Review, Note, StatusChange models and the transition service exist.

1. RED: Write tests for submission detail view:
   - Create dashboard/tests/test_submission_detail.py:
     - Test GET "/dashboard/meetups/{slug}/submissions/{id}/" returns 200 for a user with a role
     - Test 403 for a user without a role on this meetup
     - Test 404 when the submission id does not target this meetup (per spec)
     - Test the page displays all submitted fields including optional-field and custom-question responses and uploaded file links
     - Test the status badge shows the current status
     - Test the other-meetups panel appears for Write+ with per-target status, and never exposes other meetups' votes/notes
     - Test Read/Reviewer users do NOT see the other-meetups panel

2. GREEN: Implement submission detail view:
   - Add SubmissionDetailView to dashboard/views.py (required_role="read"; look up SubmissionMeetup by slug + id, 404 when not targeting this meetup)
   - Create templates/dashboard/submission_detail.html: proposal info, status badge, file links
   - Wire up URL

3. RED: Write tests for voting:
   - Add to dashboard/tests/test_submission_detail.py:
     - Test Reviewer+ sees vote buttons; Read does not
     - Test POST vote creates a Review row; voting again with the other value UPDATES the same row (no delete, latest wins)
     - Test vote counts update; all votes listed with reviewer names (visible to all roles)
     - Test Read user POSTing a vote gets 403 with no side effects

4. GREEN: Implement voting:
   - Add VoteView (POST, Reviewer+) using reviews record_vote helper; return HTMX fragment with updated votes
   - Update the template with vote buttons and the votes list; wire up URL

5. RED: Write tests for notes:
   - Add to dashboard/tests/test_submission_detail.py:
     - Test Reviewer+ sees the add-note form; Read does not
     - Test POST note creates a Note; notes display chronologically with author and timestamp
     - Test empty note body is rejected

6. GREEN: Implement notes:
   - AddNoteView (POST, Reviewer+), HTMX fragment refresh; template notes section; URL

7. RED: Write tests for status management through the workflow service:
   - Add to dashboard/tests/test_submission_detail.py (mock reviews/services.request_transition at the view boundary):
     - Test Write+ sees status controls offering ONLY the transitions legal from the current status; Read/Reviewer see none
     - Test POST status change calls request_transition with the acting user
     - Test a TransitionRejected from the service renders the error naming current status and allowed targets (no 500)
     - Test transitioning to "scheduled" requires the date picker value; missing date shows a validation error and never calls the service? No — the service/validator owns the rule: assert the rejection surfaces as a form error either way
     - Test "Mark Email Sent" button performs exactly the accepted → email_sent transition
     - Test the status history log lists StatusChange rows; changed_by=None renders as "Speaker"
     - Test Reviewer POSTing a status change gets 403 and request_transition is never called

8. GREEN: Implement status management:
   - ChangeStatusView (POST, Write+): calls reviews/services.request_transition(submission_meetup, new_status, actor=request.user, scheduled_date=…), translates TransitionRejected into form errors, returns HTMX fragment with updated badge, controls, and history
   - Template: status dropdown/buttons built from reviews/transitions.VALID_TRANSITIONS[current], date picker shown for the scheduled transition, "Mark Email Sent" convenience button, history log with "Speaker" rendering
   - Wire up URL

9. Run `just check`
```

---

## Step 19: Dashboard — Bulk Actions

**Validator consults:**
- Skills: python:python

**Goal**: Bulk status changes with the spec's all-or-nothing contract: pre-validate every row, send nothing if any row fails.

```text
Prompt for code-generation LLM:

### Step 19: Dashboard — Bulk Actions

Implement bulk operations on the submissions list with all-or-nothing pre-validation.

**NOTE**: Steps 1-18 complete. Per spec: "If any selected row cannot legally make the transition, the whole bulk action is rejected with an error listing the offending rows; no partial application." Pre-validate against the DB read model, then deliver per-row workflow updates; a row that changed between validation and delivery is rejected by its workflow's validator and reported alongside applied rows.

1. RED: Write tests for bulk status change:
   - Create dashboard/tests/test_bulk_actions.py (mock reviews/services.request_transition):
     - Test bulk change with all-valid rows calls request_transition once per row and reports all applied
     - Test ONE invalid row rejects the WHOLE batch: the response lists the offending row(s) and request_transition is NEVER called
     - Test each applied change produces its own audit row (service contract — assert per-row service calls)
     - Test a row whose request_transition raises TransitionRejected (validation-to-delivery race) is reported as an error while the other rows still apply
     - Test Reviewer gets 403 (no side effects); Write+ succeeds
     - Test empty selection returns an error

2. GREEN: Implement bulk logic:
   - Create dashboard/bulk_actions.py:
     - bulk_change_status(submission_meetup_ids, new_status, actor) → {"applied": [...], "rejected": [...], "errors": [...]}:
       - Phase 1: load all rows, validate each with reviews/transitions.is_valid_transition against DB status; ANY failure → return rejected list, send nothing
       - Phase 2: call reviews/services.request_transition per row, catching TransitionRejected per row into errors

3. GREEN: Implement bulk action view:
   - BulkActionView (POST, Write+): calls bulk_change_status, returns HTMX fragment refreshing the table with an applied/rejected/errors message
   - Update meetup_dashboard.html: bulk action bar (Alpine.js shows it when checkboxes selected), status dropdown, apply button, results message
   - Wire up URL

4. Run `just check`
```

---

## Step 20: Dashboard — Export (CSV/JSON)

**Validator consults:**
- Skills: python:python

**Goal**: Implement CSV and JSON export of submission data with the spec's column naming and privacy rules.

```text
Prompt for code-generation LLM:

### Step 20: Dashboard — Export (CSV/JSON)

Implement data export respecting current filters, permissions, and the privacy contract.

**NOTE**: Steps 1-19 complete. Submissions list with filtering works. filter_submissions exists.

1. RED: Write tests for CSV export:
   - Create dashboard/tests/test_export.py:
     - Test CSV headers: all six core global field labels, Status, Scheduled Date, Thumbs Up, Thumbs Down, then one column per non-core field/question in scope
     - Test dynamic column naming: "{field label}" for standard fields, "{meetup slug}: {question label}" for custom questions (per spec)
     - Test one row per submission-meetup combination
     - Test cells are EMPTY when a question does not apply to that row's target
     - Test export respects current filters (status, date range, search)
     - Test Write+ gets the file; Reviewer and Read get 403
     - Test export includes NO per-reviewer vote identities (counts only) and NO notes

2. GREEN: Implement CSV export:
   - Create dashboard/export.py:
     - generate_csv(meetup, queryset) → HttpResponse (text/csv, Content-Disposition): fixed columns + dynamic columns with the spec's naming, empty cells for non-applicable questions

3. RED: Write tests for JSON export:
   - Add to dashboard/tests/test_export.py:
     - Test nested structure: submission as parent with meetup-specific children (status, scheduled date, vote counts, responses)
     - Test filter state respected
     - Test role enforcement matches CSV (Write+ only)
     - Test no reviewer identities and no cross-meetup notes in the output

4. GREEN: Implement JSON export:
   - Add generate_json(meetup, queryset) → HttpResponse (application/json) to dashboard/export.py

5. GREEN: Implement export view and wire up UI:
   - ExportView (GET with format=csv|json, Write+): reuse filter_submissions with current parameters, dispatch to the generator
   - Update the meetup dashboard template with the export button + format dropdown
   - Wire up URL

6. Run `just check`
```

---

## Step 21: Dashboard — Super-Admin Views & Warnings

**Validator consults:**
- Skills: python:python

**Goal**: Build the super-admin dashboard (metrics with the spec's acceptance-rate formula), warnings, and management views for meetups, global fields, roles, and per-meetup settings/events.

```text
Prompt for code-generation LLM:

### Step 21: Dashboard — Super-Admin Views & Warnings

Build the super-admin dashboard, metrics, warnings, and management views.

**NOTE**: Steps 1-20 complete. Per-meetup dashboards work fully. Metrics formulas come straight from the spec.

1. RED: Write tests for dashboard warnings:
   - Create dashboard/tests/test_warnings.py:
     - Test get_meetup_warnings returns "no upcoming speaker" when no submission-meetup has status "scheduled" with scheduled_date today or later (org timezone)
     - Test no warning when a scheduled submission has today's date or a future date
     - Test past scheduled dates do not count
     - Test get_all_warnings covers all active meetups

2. GREEN: Implement warning logic:
   - Create dashboard/warnings.py: get_meetup_warnings(meetup), get_all_warnings()

3. RED: Write tests for the metrics:
   - Create dashboard/tests/test_metrics.py:
     - Test acceptance rate = accepted-lineage (accepted, email_sent, speaker_accepted, scheduled, presented) / (accepted-lineage + rejected)
     - Test submitted, under_review, waitlisted, and withdrawn rows are excluded from numerator AND denominator
     - Test zero denominator returns "n/a"
     - Test submissions-this-month counts Submission rows with created_at in the current calendar month in the ORG timezone (boundary case: a UTC timestamp that falls in last month org-local time is excluded)

4. GREEN: Implement metrics:
   - Create dashboard/metrics.py: acceptance_rate(), submissions_this_month(), total_submissions()

5. RED: Write tests for the super-admin dashboard view:
   - Add to dashboard/tests/test_views.py:
     - Test super-admin sees summary cards (total, this month, acceptance rate), per-meetup breakdown with status counts, warning alerts, and the recent activity feed (20 most recent items across submissions, status changes, and votes, newest first)
     - Test non-super-admin never sees the summary content (they get their meetup list)

6. GREEN: Implement super-admin dashboard:
   - Update DashboardHomeView using metrics/warnings modules; build the activity feed by merging recent Submission, StatusChange, and Review rows sorted by timestamp, sliced to 20
   - Update templates/dashboard/home.html with the summary section and quick links (manage meetups, global fields, users)

7. RED: Write tests for management views:
   - Create dashboard/tests/test_management.py:
     - Test super-admin can create/edit/deactivate meetups; non-super-admin gets 403
     - Test global field management: relabel/reorder core fields allowed; deleting or deactivating a core field is blocked; creating additional non-core global fields works
     - Test role assignment respects can_assign_role (an admin assigning "admin" is rejected; write assigning "reviewer" works)
     - Test meetup Admin can edit meetup settings (info, branding, webhook_url/secret, grace period), toggle optional fields (enabled + required flags), and CRUD custom questions; Write cannot (403)
     - Test meetup Admin can create/edit/archive events and manage event-scoped custom questions

8. GREEN: Implement management views:
   - Super-admin: MeetupManagementView (+create/edit/deactivate), global fields view, user role management view (enforcing can_assign_role)
   - Meetup admin: MeetupSettingsView (info, branding, webhook config, grace period, optional field toggles, custom questions), EventManagementView (CRUD + archive + event questions)
   - Templates and URLs for all of the above

9. Run `just check`
```

---

## Step 22: Media Access Control

**Validator consults:**
- Skills: python:python

**Goal**: Enforce the spec's media contract: headshot files public, everything else through an authenticated view that hands off to nginx via X-Accel-Redirect (with a direct-serve fallback in development).

```text
Prompt for code-generation LLM:

### Step 22: Media Access Control

Implement the authenticated media view and the public-headshot carve-out.

**NOTE**: Steps 1-21 complete. FileUpload rows exist with content_type and a storage path. Per spec: headshot-labeled uploads are public (nginx serves them directly in production); all other uploads route through an authenticated Django view (Read+ on a targeted meetup, or super-admin) that responds with X-Accel-Redirect to an internal nginx location.

1. RED: Write tests for upload path routing:
   - Create submissions/tests/test_media_paths.py:
     - Test files for headshot-labeled fields are stored under "headshots/" (public prefix)
     - Test all other uploads are stored under "protected/" (internal prefix)

2. GREEN: Implement upload path routing:
   - Add an upload_to callable for FileUpload.file that inspects the field_response's field label/kind and routes to "headshots/" or "protected/"
   - Update the intake persistence (Step 10's submissions/persistence.py) to preserve this routing when it records storage paths

3. RED: Write tests for the protected media view:
   - Create submissions/tests/test_media_views.py:
     - Test unauthenticated request to a protected file URL redirects to login
     - Test authenticated user with NO role on any targeted meetup gets 403
     - Test user with Read+ on ANY meetup the submission targets gets 200
     - Test super-admin gets 200
     - Test production mode responds with an X-Accel-Redirect header pointing at the internal location instead of file bytes
     - Test dev mode (DEBUG=True) serves the file directly (FileResponse)
     - Test headshot URLs are NOT routed through the protected view

4. GREEN: Implement the protected media view:
   - Create submissions/media_views.py:
     - protected_media(request, path): resolve the FileUpload, check has_meetup_role(user, meetup, "read") across the submission's targets (or is_superadmin), then X-Accel-Redirect (prod) / FileResponse (dev)
   - Wire up: path("media/protected/<path:path>", ...) and leave /media/headshots/ to static/nginx serving

5. Run `just check`
```

---

## Step 23: Management Commands & Data Seeding

**Validator consults:**
- Skills: python:python

**Goal**: Build remaining management commands and ensure the app can be bootstrapped cleanly. Seeded rows need no special workflow handling — the transition service's update-with-start self-heals them.

```text
Prompt for code-generation LLM:

### Step 23: Management Commands & Data Seeding

Finalize management commands and ensure clean bootstrapping.

**NOTE**: Steps 1-22 complete. seed_global_fields exists from Step 2. Seeded SubmissionMeetup rows have no running lifecycle workflow; that is fine — reviews/services.request_transition uses update-with-start with the DB status as initial state.

1. RED: Write tests for seed_global_fields idempotency edge cases:
   - Update core/tests/test_commands.py:
     - Test running seed_global_fields three times yields the same rows (fully idempotent)
     - Test core-field protection survives seeding (fields remain is_core=True, required)

2. GREEN: Harden seed_global_fields if any test fails

3. RED: Write tests for a create_test_data management command:
   - Add to core/tests/test_commands.py:
     - Test create_test_data creates sample meetups (mixed cfp modes, one with webhook_url and grace period set), events, submissions with multi-meetup targeting, users with each role, votes, and notes
     - Test it is idempotent
     - Test it refuses to run when DEBUG=False

4. GREEN: Implement create_test_data:
   - Create core/management/commands/create_test_data.py per the tests (DEBUG guard first)

5. Verify the full bootstrap sequence works:
   - Run: migrate → seed_global_fields → create_test_data → runserver (and run_worker against `temporal server start-dev`)
   - Add a smoke test or manually verify: landing page, multi-submit form, a dashboard status change end-to-end through the worker

6. Run `just check`
```

---

## Step 24: Docker & Production Configuration

**Validator consults:** none

**Goal**: Docker Compose for production: web, worker, Temporal server + UI, PostgreSQL, nginx (public headshots + internal protected media). Plus the README with documented timezone behavior.

```text
Prompt for code-generation LLM:

### Step 24: Docker & Production Configuration

Set up Docker Compose for production deployment and write the README.

**NOTE**: Steps 1-23 complete. The application is fully functional in development against `temporal server start-dev`.

1. Create Dockerfile:
   - Base image: python:3.12-slim
   - Install system deps (libpq-dev for psycopg), install uv
   - Copy pyproject.toml and uv.lock, run `uv sync --no-dev`
   - Copy application code, run `manage.py tailwind build` and `collectstatic`
   - Default command: gunicorn meetup_cfp.wsgi:application

2. Create docker-compose.yml with all services from the spec:
   - web: builds from Dockerfile, depends on db + temporal, reads .env
   - worker: same image, command `python manage.py run_worker`, depends on db + temporal + web (waits for migrations)
   - temporal: temporalio/auto-setup image, sharing the PostgreSQL instance (DB env vars pointing at db), NOT publicly exposed
   - temporal-ui: temporalio/ui, bound to localhost/internal network only (operator access)
   - db: postgres:16 with postgres_data volume and healthcheck
   - nginx: nginx:alpine, ports 80/443, proxies to web, serves static and media volumes
   - Volumes: postgres_data, static_files, media_files

3. Create nginx configuration:
   - nginx/nginx.conf:
     - Upstream web:8000; proxy all app requests
     - /static/ served from static_files volume
     - /media/headshots/ served PUBLICLY from media_files volume (spec: headshots are public)
     - /internal-media/ as an `internal` location over media_files — target of X-Accel-Redirect from the protected media view; direct requests get 404
     - Security headers

4. Create .env.example:
   - DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DEBUG, TIME_ZONE
   - CAPTCHA_SITE_KEY, CAPTCHA_SECRET_KEY
   - GITHUB_CLIENT_ID/SECRET, GOOGLE_CLIENT_ID/SECRET
   - TEMPORAL_ADDRESS=temporal:7233, TEMPORAL_NAMESPACE=default, TEMPORAL_TASK_QUEUE=cfp-main

5. Create entrypoint scripts:
   - docker/entrypoint-web.sh: wait for db → migrate → seed_global_fields → collectstatic → gunicorn
   - docker/entrypoint-worker.sh: wait for db + temporal + web health → run_worker

6. Update production settings:
   - Verify prod.py handles DATABASE_URL, STATIC_ROOT/MEDIA_ROOT, SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, CSRF_TRUSTED_ORIGINS, WhiteNoise fallback

7. Write the README:
   - Setup (dev and Docker), architecture overview (Django read layer + Temporal workflows + worker), webhook contract summary
   - REQUIRED per spec: document timezone behavior — UTC storage (USE_TZ=True), single org-wide display timezone via TIME_ZONE, CFP window checks against timezone-aware now()

8. Test Docker build:
   - `docker compose build` succeeds; `docker compose up` starts all six services; the app is reachable via nginx; a submission flows through the worker end-to-end

9. Run `just check` one final time
```

---

## Implementation Guidelines

### TDD Discipline
- Every feature starts with a failing test (RED)
- Write the minimum code to make it pass (GREEN)
- Clean up only after tests pass (REFACTOR)
- Never skip the RED phase — it catches design issues early

### File Conventions
- Every Python file starts with a 2-line ABOUTME comment
- Models in `app/models.py`, views in `app/views.py`
- Business logic in separate modules (`app/validation.py`, `app/services.py`, `app/persistence.py`)
- Temporal code: workflows in `app/workflows.py`, activities in `app/activities.py`, shared dataclasses in `app/messages.py` (Django-free)
- Tests in `app/tests/test_*.py`; factories in `tests/factories.py` at project root

### Temporal Discipline
- Workflow code is deterministic: no ORM, no I/O, no clock/random access outside Temporal APIs; all side effects live in activities
- `reviews/transitions.py` and the `messages.py` modules stay import-safe for the workflow sandbox (no Django imports)
- Activities are sync functions on the worker's thread pool and must be idempotent (retries and replays are normal)
- Django code never writes `SubmissionMeetup.status` directly — always `reviews/services.request_transition` (update-with-start)
- File contents never flow through workflow inputs/results — storage paths only
- Workflow tests use `WorkflowEnvironment.start_time_skipping()` with mocked activities; activity/service logic is tested synchronously without Temporal

### Testing Boundaries
- Test YOUR business logic: validation rules, permission checks, transition table, duplicate detection, form assembly, export formatting, webhook payloads, workflow behavior (validation, sequencing, idempotency)
- Do NOT test Django or Temporal themselves: model creation, ORM query mechanics, form rendering, SDK retry mechanics
- Use factories for test data; `pytest.mark.django_db` for database tests

### Key Patterns
- Permission checks: always `has_meetup_role` / helper functions, never raw role comparison; assignment via `can_assign_role`
- Status transitions: always through the workflow (via the service); the update validator is the gate, `reviews/persistence.apply_transition` re-validates as defense in depth
- Submission creation: views validate, the intake workflow persists — never create submission rows in views
- Branding: always `effective_*` properties in templates
- CFP checks: `cfp_is_open` for display, `accepts_submissions_now` (grace-aware) for submit-time validation

---

## Success Metrics

1. **All tests pass**: `just check` exits 0 (including async workflow tests)
2. **Clean lint and types**: `ruff check .`, `ruff format --check .`, `mypy .` report no issues
3. **All business rules enforced**: duplicate detection (withdrawn excluded), CFP windows with grace, role hierarchy + assignment matrix, normative transition table
4. **Workflow-owned lifecycle works**: transitions flow through `SubmissionLifecycleWorkflow` updates; illegal transitions are rejected with no audit row; every applied transition writes one
5. **Webhooks work**: configured meetups receive signed `submission.received` and `submission.status_changed` POSTs; failures retry without blocking transitions
6. **Public pages work**: landing, meetup detail, event detail, multi-submit with HTMX, withdrawal
7. **Dashboard works**: auth, submissions list, detail, voting, notes, status changes, bulk actions (all-or-nothing), export, super-admin views
8. **Media contract holds**: headshots public, protected files gated by role via X-Accel-Redirect
9. **Docker deploys**: `docker compose up` serves the full application including the Temporal server, UI, and worker
10. **Seed data works**: `seed_global_fields` and `create_test_data` run cleanly; seeded rows accept transitions via update-with-start
