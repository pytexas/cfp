# meetup-cfp Implementation Plan

## Current Status

| Step | Description | Status |
|------|-------------|--------|
| 1 | Project Scaffolding & Configuration | Not Started |
| 2 | Core App — Organization & Global Fields | Not Started |
| 3 | Users App — Custom User & Role Model | Not Started |
| 4 | Meetups App — Meetup & Event Models | Not Started |
| 5 | Submissions App — Submission & Field Response Models | Not Started |
| 6 | Reviews App — Voting, Notes, Status Transitions | Not Started |
| 7 | Permission System — Hierarchy Enforcement | Not Started |
| 8 | Public Pages — Org Landing & Meetup Pages | Not Started |
| 9 | Dynamic Multi-Submit Form (HTMX) | Not Started |
| 10 | Submission Validation & Duplicate Detection | Not Started |
| 11 | Withdrawal Flow | Not Started |
| 12 | Dashboard — Authentication & Layout | Not Started |
| 13 | Dashboard — Meetup Submissions View | Not Started |
| 14 | Dashboard — Submission Detail & Reviews | Not Started |
| 15 | Dashboard — Bulk Actions & Status Management | Not Started |
| 16 | Dashboard — Export (CSV/JSON) | Not Started |
| 17 | Dashboard — Super-Admin Views & Warnings | Not Started |
| 18 | Management Commands & Data Seeding | Not Started |
| 19 | Docker & Production Configuration | Not Started |

---

## Architecture Decisions

- **Project name**: `meetup_cfp` (the Django project package)
- **Apps live at**: top-level (e.g., `core/`, `meetups/`, not nested under project)
- **Test location**: each app has a `tests/` package (e.g., `core/tests/test_models.py`)
- **Settings split**: `meetup_cfp/settings/base.py`, `dev.py`, `prod.py`
- **Justfile**: used as the task runner for common commands
- **pytest**: with `pytest-django` as the test runner (configured in `pyproject.toml`)
- **Factory Boy**: for test fixtures via `factory_boy`
- **ruff**: for linting and formatting
- **mypy**: for type checking

---

## Step 1: Project Scaffolding & Configuration

**Goal**: Initialize the Django project with all tooling configured. No business logic yet — just a working skeleton that runs tests, lints, and serves a blank page.

```text
Prompt for code-generation LLM:

### Step 1: Project Scaffolding & Configuration

Set up the Django project skeleton with all tooling. No business logic — just a working foundation.

1. Initialize pyproject.toml with uv:
   - Create pyproject.toml with:
     - Project metadata (name="meetup-cfp", version="0.1.0", python requires ">=3.12")
     - Dependencies: django>=5.1, django-allauth, django-tailwind-cli, gunicorn, psycopg[binary], django-htmx, whitenoise
     - Dev dependencies: pytest, pytest-django, factory-boy, ruff, mypy, django-stubs, coverage
     - Ruff config: line-length=120, target python 3.12, isort settings
     - Mypy config: django-stubs plugin, strict optional, warn unused ignores
     - Pytest config: DJANGO_SETTINGS_MODULE=meetup_cfp.settings.dev, pythonpath=["."]
   - Run `uv sync` to install all dependencies

2. Create Django project structure:
   - Run `uv run django-admin startproject meetup_cfp .` (note the dot — project in current dir)
   - This creates: manage.py, meetup_cfp/__init__.py, settings.py, urls.py, asgi.py, wsgi.py

3. Split settings into base/dev/prod:
   - Create meetup_cfp/settings/ package:
     - meetup_cfp/settings/__init__.py (empty)
     - meetup_cfp/settings/base.py — move content from settings.py here, then:
       - Set INSTALLED_APPS with: django defaults, allauth, django_htmx, tailwind_cli
       - Set TAILWIND_CLI_VERSION = "4.0"
       - Add django_htmx.middleware.HtmxMiddleware to MIDDLEWARE
       - Set AUTH_USER_MODEL = "users.CustomUser"
       - Set STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT
       - Set DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
       - Set LOGIN_REDIRECT_URL = "/dashboard/"
       - Set ACCOUNT_AUTHENTICATION_METHOD = "email" (allauth)
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

**Goal**: Build the Organization singleton and GlobalFormField/StandardOptionalField models with seed data management command. These are foundational data structures used by every other app.

```text
Prompt for code-generation LLM:

### Step 2: Core App — Organization & Global Fields

Build the Organization singleton and form field configuration models. These are used by every other app.

**NOTE**: The project skeleton from Step 1 is already in place. The users app has a minimal CustomUser model. All six app directories exist. Pytest is configured and running.

1. RED: Write model tests for Organization singleton:
   - Create core/tests/test_models.py:
     - Test that only one Organization instance can exist (second create raises or returns existing)
     - Test that Organization has all required fields (name, slug, description, logo, primary_color, secondary_color)
     - Test that Organization.get_instance() class method returns the singleton (create if not exists)
     - Test that slug is auto-generated from name if not provided

2. GREEN: Implement Organization model:
   - Create core/models.py:
     - Organization model with fields per spec: name, slug, description, logo (ImageField), primary_color (CharField, default="#000000"), secondary_color (CharField, default="#ffffff")
     - Add get_instance() classmethod that does get_or_create
     - Override save() to enforce singleton (raise if pk exists and different instance)
     - Add __str__ returning name
   - Register Organization in core/admin.py

3. RED: Write model tests for GlobalFormField:
   - Create or update core/tests/test_models.py:
     - Test that GlobalFormField can be created with valid field_type choices
     - Test that sort_order is respected in default ordering
     - Test that options field stores and retrieves JSON for select types
     - Test that is_active defaults to True

4. GREEN: Implement GlobalFormField model:
   - Add to core/models.py:
     - FIELD_TYPE_CHOICES constant: short_text, long_text, single_select, multi_select, file_upload
     - GlobalFormField with: label, field_type (CharField with choices), is_required (BooleanField), options (JSONField, default=list), sort_order (IntegerField), is_active (BooleanField, default=True)
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
     - Test that running seed_global_fields creates the 6 default global fields (Name, Email, Talk Title, Abstract, Description, Speaker Bio)
     - Test that running it twice is idempotent (doesn't create duplicates)
     - Test that it creates the 5 standard optional fields (Talk Length, Experience Level, Speaker Headshot, Speaker Links, Prior Speaking Experience)
     - Test that Talk Length has correct options: ["15 min", "30 min", "45 min", "60 min"]
     - Test that Experience Level has correct options: ["Beginner", "Intermediate", "Advanced"]

8. GREEN: Implement seed_global_fields management command:
   - Create core/management/__init__.py
   - Create core/management/commands/__init__.py
   - Create core/management/commands/seed_global_fields.py:
     - Use get_or_create for each field to ensure idempotency
     - Create the 6 global fields with correct types and required flags
     - Create the 5 standard optional fields with correct types and options

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations core`
   - Run `uv run python manage.py migrate`
   - Run `just check` to confirm all tests pass and linting is clean
```

---

## Step 3: Users App — Custom User & Role Model

**Goal**: Build the MeetupRole model and permission-checking utilities. The permission hierarchy (Read → Reviewer → Write → Admin → Super-Admin) is central to the entire dashboard.

```text
Prompt for code-generation LLM:

### Step 3: Users App — Custom User & Role Model

Build the MeetupRole model and permission-checking utilities. The role hierarchy is central to the dashboard.

**NOTE**: Step 1 created a minimal CustomUser model with just is_superadmin. Step 2 built the Organization and field models. The users app already exists with a basic CustomUser.

1. RED: Write tests for the role hierarchy:
   - Create users/tests/__init__.py
   - Create users/tests/test_permissions.py:
     - Test that ROLE_HIERARCHY defines correct ordering: read < reviewer < write < admin
     - Test has_meetup_role(user, meetup, "reviewer") returns True when user has "reviewer" role on that meetup
     - Test has_meetup_role(user, meetup, "reviewer") returns True when user has "write" role (hierarchy: higher roles include lower)
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
       - meetup: FK → "meetups.Meetup" (as string reference — the meetups app model exists in Step 4, but Django handles forward references)
       - role: CharField with ROLE_CHOICES
       - Unique constraint on (user, meetup)
       - __str__ returning "{user} - {meetup} ({role})"
   - Create users/permissions.py:
     - has_meetup_role(user, meetup, required_role) → bool:
       - If user.is_superadmin: return True
       - Look up MeetupRole for (user, meetup)
       - Compare role level against required_role level using ROLE_HIERARCHY
     - get_user_role(user, meetup) → str | None:
       - If user.is_superadmin: return "superadmin"
       - Look up MeetupRole, return role or None
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

Note: MeetupRole has a FK to Meetup which doesn't exist yet. Django handles string references in ForeignKey, but migrations will need to be created after the meetups app models exist. For now, the tests should use a minimal Meetup model or mock. If migrations fail, create a temporary Meetup model in the meetups app first (just name and slug fields) to satisfy the FK.
```

---

## Step 4: Meetups App — Meetup & Event Models

**Goal**: Build the Meetup and Event models with CFP window logic (year-round vs time-boxed). Also build MeetupOptionalFieldConfig and CustomQuestion.

```text
Prompt for code-generation LLM:

### Step 4: Meetups App — Meetup & Event Models

Build the Meetup and Event models with CFP window logic, plus the per-meetup form configuration models.

**NOTE**: Steps 1-3 are complete. CustomUser and MeetupRole exist. Organization, GlobalFormField, and StandardOptionalField exist in core. The MeetupRole FK to Meetup is a string reference awaiting this step.

1. RED: Write tests for Meetup model and CFP logic:
   - Create meetups/tests/__init__.py
   - Create meetups/tests/test_models.py:
     - Test Meetup creation with required fields (name, slug, description)
     - Test that slug must be unique
     - Test cfp_is_open property returns True when cfp_mode="year_round" and is_active=True
     - Test cfp_is_open returns False when cfp_mode="year_round" and is_active=False
     - Test cfp_is_open returns True when cfp_mode="time_boxed" and current time is between cfp_open_date and cfp_close_date and is_active=True
     - Test cfp_is_open returns False when cfp_mode="time_boxed" and current time is outside the window
     - Test cfp_is_open returns False when cfp_mode="time_boxed" and dates are null
     - Test that deactivated meetup (is_active=False) always returns cfp_is_open=False
     - Test effective_logo property returns meetup logo if set, else org logo
     - Test effective_primary_color returns meetup color if set, else org color
     - Test effective_secondary_color returns meetup color if set, else org color

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
       - created_at, updated_at (auto)
     - cfp_is_open property implementing business logic
     - effective_logo, effective_primary_color, effective_secondary_color properties with org fallback
     - __str__, Meta ordering by name
   - Register in meetups/admin.py

3. RED: Write tests for Event model and CFP logic:
   - Add to meetups/tests/test_models.py:
     - Test Event creation with FK to Meetup
     - Test Event slug is unique within a meetup (unique_together)
     - Test Event cfp_is_open returns True when within date window and not archived
     - Test Event cfp_is_open returns False when outside date window
     - Test Event cfp_is_open returns False when is_archived=True

4. GREEN: Implement Event model:
   - Add to meetups/models.py:
     - Event model per spec:
       - meetup (FK → Meetup)
       - name, slug, description, date (DateField)
       - cfp_open_date, cfp_close_date (DateTimeField)
       - is_archived (BooleanField, default=False)
       - created_at (auto)
     - cfp_is_open property
     - unique_together = [("meetup", "slug")]
   - Register in meetups/admin.py

5. RED: Write tests for MeetupOptionalFieldConfig:
   - Add to meetups/tests/test_models.py:
     - Test that MeetupOptionalFieldConfig links a Meetup to a StandardOptionalField
     - Test that unique_together prevents duplicate configurations
     - Test a helper method get_enabled_fields(meetup) returns only enabled standard fields for that meetup

6. GREEN: Implement MeetupOptionalFieldConfig:
   - Add to meetups/models.py:
     - MeetupOptionalFieldConfig: meetup (FK), standard_field (FK → StandardOptionalField), is_enabled (BooleanField, default=True)
     - unique_together = [("meetup", "standard_field")]
     - Add get_enabled_fields classmethod or manager method

7. RED: Write tests for CustomQuestion:
   - Create submissions/tests/__init__.py
   - Create submissions/tests/test_models.py:
     - Test CustomQuestion creation with meetup FK
     - Test CustomQuestion with event FK (scoped to event)
     - Test CustomQuestion with event=None (applies to meetup default CFP)
     - Test ordering by sort_order

8. GREEN: Implement CustomQuestion model:
   - Create submissions/models.py (start of submissions app):
     - CustomQuestion model per spec:
       - meetup (FK → Meetup)
       - event (FK → Event, null=True, blank=True)
       - label, field_type (using same FIELD_TYPE_CHOICES from core), is_required, options (JSONField), sort_order, is_active
     - Meta: ordering = ["sort_order"]

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations meetups submissions`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 5: Submissions App — Submission & Field Response Models

**Goal**: Build the Submission, SubmissionMeetup, and SubmissionFieldResponse models. This is the data backbone for proposals.

```text
Prompt for code-generation LLM:

### Step 5: Submissions App — Submission & Field Response Models

Build the core submission data models. These store all proposal data and per-meetup tracking.

**NOTE**: Steps 1-4 are complete. Meetup, Event, CustomQuestion, GlobalFormField, StandardOptionalField all exist.

1. RED: Write tests for Submission model:
   - Update submissions/tests/test_models.py:
     - Test Submission creation with required fields (speaker_name, speaker_email, title, abstract, description, speaker_bio)
     - Test that withdrawal_token is auto-generated UUID on creation
     - Test that withdrawal_token is unique
     - Test __str__ returns "{title} by {speaker_name}"

2. GREEN: Implement Submission model:
   - Update submissions/models.py:
     - STATUS_CHOICES: submitted, under_review, accepted, rejected, waitlisted, withdrawn, email_sent, speaker_accepted, scheduled, presented
     - Submission model per spec:
       - speaker_name, speaker_email (EmailField)
       - title, abstract (TextField), description (TextField), speaker_bio (TextField)
       - withdrawal_token (UUIDField, default=uuid4, unique=True, editable=False)
       - created_at, updated_at (auto)
     - __str__ returning title and speaker_name

3. RED: Write tests for SubmissionMeetup:
   - Add to submissions/tests/test_models.py:
     - Test SubmissionMeetup creation linking Submission to Meetup
     - Test unique constraint on (submission, meetup, event) prevents duplicates
     - Test SubmissionMeetup with event=None (default meetup CFP)
     - Test SubmissionMeetup with event set (event-specific submission)
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
     - unique_together = [("submission", "meetup", "event")]

5. RED: Write tests for SubmissionFieldResponse:
   - Add to submissions/tests/test_models.py:
     - Test that exactly one of global_field, standard_field, custom_question must be set
     - Test that setting two FKs raises validation error (via clean method)
     - Test that setting zero FKs raises validation error
     - Test storing text response in value_text
     - Test storing file response in value_file

6. GREEN: Implement SubmissionFieldResponse model:
   - Add to submissions/models.py:
     - SubmissionFieldResponse:
       - submission (FK → Submission)
       - global_field (FK → GlobalFormField, null=True, blank=True)
       - standard_field (FK → StandardOptionalField, null=True, blank=True)
       - custom_question (FK → CustomQuestion, null=True, blank=True)
       - value_text (TextField, blank=True)
       - value_file (FileField, blank=True, upload_to="submissions/")
     - Override clean() to enforce exactly-one-FK constraint
     - Override save() to call full_clean()

7. RED: Write tests for FileUpload model:
   - Add to submissions/tests/test_models.py:
     - Test FileUpload creation linked to Submission and SubmissionFieldResponse
     - Test original_filename is stored correctly

8. GREEN: Implement FileUpload model:
   - Add to submissions/models.py:
     - FileUpload:
       - submission (FK → Submission)
       - field_response (FK → SubmissionFieldResponse)
       - file (FileField, upload_to="uploads/")
       - original_filename (CharField)
       - uploaded_at (auto)

9. Run migrations and verify:
   - Run `uv run python manage.py makemigrations submissions`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 6: Reviews App — Voting, Notes, Status Transitions

**Goal**: Build the Review, Note, and StatusChange models. Implement status transition validation logic.

```text
Prompt for code-generation LLM:

### Step 6: Reviews App — Voting, Notes, Status Transitions

Build the review infrastructure: votes, notes, and audited status transitions.

**NOTE**: Steps 1-5 complete. All submission data models exist. STATUS_CHOICES defined in submissions app.

1. RED: Write tests for valid status transitions:
   - Create reviews/tests/__init__.py
   - Create reviews/tests/test_transitions.py:
     - Test VALID_TRANSITIONS map defines allowed transitions
     - Test is_valid_transition("submitted", "under_review") returns True
     - Test is_valid_transition("submitted", "presented") returns False (can't skip)
     - Test is_valid_transition("under_review", "accepted") returns True
     - Test is_valid_transition("under_review", "rejected") returns True
     - Test is_valid_transition("under_review", "waitlisted") returns True
     - Test is_valid_transition("accepted", "email_sent") returns True
     - Test is_valid_transition("email_sent", "speaker_accepted") returns True
     - Test is_valid_transition("speaker_accepted", "scheduled") returns True
     - Test is_valid_transition("scheduled", "presented") returns True
     - Test is_valid_transition from any active status to "withdrawn" returns True
     - Test is_valid_transition("presented", "submitted") returns False (no backward)
     - Test transition_status function changes status and creates StatusChange audit log
     - Test transition_status raises ValueError for invalid transition
     - Test transition_status requires scheduled_date when transitioning to "scheduled"
     - Test transition_status raises ValueError when transitioning to "scheduled" without a date

2. GREEN: Implement status transition logic:
   - Create reviews/transitions.py:
     - VALID_TRANSITIONS dict mapping each status to its allowed next statuses:
       - submitted → [under_review, withdrawn]
       - under_review → [accepted, rejected, waitlisted, withdrawn]
       - accepted → [email_sent, withdrawn]
       - rejected → [under_review] (allow re-review)
       - waitlisted → [under_review, accepted, withdrawn]
       - email_sent → [speaker_accepted, withdrawn]
       - speaker_accepted → [scheduled, withdrawn]
       - scheduled → [presented, withdrawn]
       - presented → [] (terminal)
       - withdrawn → [] (terminal)
     - is_valid_transition(from_status, to_status) → bool
     - transition_status(submission_meetup, new_status, changed_by, scheduled_date=None) → StatusChange:
       - Validate transition is allowed
       - If new_status == "scheduled", require scheduled_date
       - Update submission_meetup.status
       - Set submission_meetup.scheduled_date if provided
       - Create and return StatusChange record

3. RED: Write tests for Review (Vote) model:
   - Create reviews/tests/test_models.py:
     - Test Review creation with submission_meetup and reviewer
     - Test unique constraint prevents same reviewer voting twice on same submission_meetup
     - Test vote choices are thumbs_up and thumbs_down
     - Test vote_summary helper returns correct counts (e.g., {thumbs_up: 3, thumbs_down: 1})

4. GREEN: Implement Review model:
   - Create reviews/models.py:
     - VOTE_CHOICES: ("thumbs_up", "Thumbs Up"), ("thumbs_down", "Thumbs Down")
     - Review: submission_meetup (FK), reviewer (FK → CustomUser), vote (CharField), created_at
     - unique_together = [("submission_meetup", "reviewer")]

5. RED: Write tests for Note model:
   - Add to reviews/tests/test_models.py:
     - Test Note creation with submission_meetup, author, body
     - Test ordering by created_at (newest first or oldest first — pick oldest first for chronological display)

6. GREEN: Implement Note model:
   - Add to reviews/models.py:
     - Note: submission_meetup (FK), author (FK → CustomUser), body (TextField), created_at
     - Meta: ordering = ["created_at"]

7. GREEN: Implement StatusChange model:
   - Add to reviews/models.py:
     - StatusChange: submission_meetup (FK), changed_by (FK → CustomUser), old_status, new_status, changed_at (auto)
     - Meta: ordering = ["-changed_at"]

8. Run migrations and verify:
   - Run `uv run python manage.py makemigrations reviews`
   - Run `uv run python manage.py migrate`
   - Run `just check`
```

---

## Step 7: Permission System — Hierarchy Enforcement

**Goal**: Build comprehensive permission checks that will be used throughout the dashboard. Create test fixtures (factories) for all models to make future testing easier.

```text
Prompt for code-generation LLM:

### Step 7: Permission System — Hierarchy Enforcement

Build test factories for all models and comprehensive permission integration tests.

**NOTE**: Steps 1-6 complete. All models exist. Basic permission functions exist in users/permissions.py. This step adds factories and thorough integration tests.

1. Create test factories for all models:
   - Create conftest.py at project root (or update existing):
     - Import and configure pytest-django
   - Create tests/__init__.py (project-level test utilities)
   - Create tests/factories.py:
     - UserFactory: creates CustomUser instances with sequential usernames/emails
     - SuperAdminFactory: UserFactory with is_superadmin=True
     - OrganizationFactory: creates Organization with defaults
     - MeetupFactory: creates Meetup with name, slug, is_active=True, cfp_mode="year_round"
     - EventFactory: creates Event linked to a Meetup
     - GlobalFormFieldFactory: creates GlobalFormField
     - StandardOptionalFieldFactory: creates StandardOptionalField
     - CustomQuestionFactory: creates CustomQuestion linked to a Meetup
     - SubmissionFactory: creates Submission with required fields
     - SubmissionMeetupFactory: creates SubmissionMeetup linking Submission to Meetup
     - MeetupRoleFactory: creates MeetupRole linking User to Meetup with a role
     - ReviewFactory: creates Review linked to SubmissionMeetup
     - NoteFactory: creates Note linked to SubmissionMeetup

2. RED: Write integration tests for permission checks across all role levels:
   - Create users/tests/test_permissions_integration.py:
     - Test that a "read" user can view submissions but cannot vote, add notes, or change status
     - Test that a "reviewer" user can view submissions, vote, and add notes, but cannot change status
     - Test that a "write" user can do everything reviewer can plus change status, add notes, and export
     - Test that an "admin" user can do everything write can plus edit meetup settings and manage custom questions
     - Test that a super-admin can access any meetup regardless of explicit role assignment
     - Test that a user with "admin" on meetup A and "read" on meetup B gets correct permissions on each
     - Test that a user with no role on a meetup gets no access

3. GREEN: Create helper functions for common permission checks:
   - Update users/permissions.py:
     - can_view_submissions(user, meetup) → bool (read+)
     - can_vote(user, meetup) → bool (reviewer+)
     - can_add_notes(user, meetup) → bool (reviewer+)
     - can_manage_submissions(user, meetup) → bool (write+)
     - can_export(user, meetup) → bool (write+)
     - can_manage_meetup_settings(user, meetup) → bool (admin+)
     - can_manage_events(user, meetup) → bool (admin+)
     - can_manage_roles(user, meetup) → bool (write+ for reviewer assignment, admin+ for others)
     - is_super_admin(user) → bool
   - Each function uses has_meetup_role internally

4. REFACTOR: Ensure all permission functions are clean and well-organized:
   - All use the hierarchy comparison
   - Super-admin bypass is consistent
   - No code duplication

5. Run `just check` to verify all tests pass
```

---

## Step 8: Public Pages — Org Landing & Meetup Pages

**Goal**: Build the public-facing read-only pages: organization landing page, individual meetup pages, and event pages. No submission forms yet — just the display.

```text
Prompt for code-generation LLM:

### Step 8: Public Pages — Org Landing & Meetup Pages

Build the public-facing pages for browsing meetups. Forms come in later steps.

**NOTE**: Steps 1-7 complete. All models, permissions, and factories exist. There's a minimal base template from Step 1.

1. Set up Tailwind CSS:
   - Run `uv run python manage.py tailwind build` to generate initial CSS
   - Update templates/base.html:
     - Add {% load tailwind_cli %} and {% tailwind_css %} in <head>
     - Add basic layout structure: nav, main content area, footer
     - Add HTMX script tag (CDN for now)
     - Add Alpine.js script tag (CDN for now)
   - Configure STATICFILES_DIRS in settings to include the Tailwind output

2. RED: Write view tests for the org landing page:
   - Create core/tests/test_views.py:
     - Test GET "/" returns 200
     - Test the page shows the organization name if an Organization exists
     - Test the page lists only active meetups
     - Test deactivated meetups are NOT shown
     - Test meetups with open CFP show a visual indicator
     - Test the "Submit to Multiple Meetups" link is present

3. GREEN: Implement org landing page:
   - Create core/views.py:
     - OrgLandingView (TemplateView or function-based):
       - Get Organization singleton (or None)
       - Get all active Meetups
       - Pass to template
   - Create templates/core/landing.html:
     - Organization name, logo, description
     - List of active meetups with name, description, logo
     - Each meetup links to /meetups/{slug}/
     - "Submit to Multiple Meetups" button linking to /submit/
   - Wire up in meetup_cfp/urls.py: path("", OrgLandingView, name="landing")

4. RED: Write view tests for meetup page:
   - Create meetups/tests/test_views.py:
     - Test GET "/meetups/{slug}/" returns 200 for active meetup
     - Test 404 for deactivated meetup
     - Test 404 for non-existent slug
     - Test page shows meetup name and description
     - Test page shows "CFP Closed" message when CFP is not open
     - Test page uses meetup branding if set, falls back to org branding

5. GREEN: Implement meetup page:
   - Create meetups/views.py:
     - MeetupDetailView:
       - Look up Meetup by slug, filter is_active=True (404 if not found)
       - Pass meetup and cfp_is_open status to template
   - Create templates/meetups/detail.html:
     - Meetup name, logo, description
     - If CFP open: placeholder for form (filled in Step 9/10)
     - If CFP closed: message
   - Wire up: path("meetups/<slug:slug>/", MeetupDetailView, name="meetup-detail")

6. RED: Write view tests for event page:
   - Add to meetups/tests/test_views.py:
     - Test GET "/meetups/{meetup_slug}/events/{event_slug}/" returns 200
     - Test 404 for archived event
     - Test 404 for non-existent event slug
     - Test page shows event name, description, date
     - Test page shows "CFP Closed" when event CFP is closed
     - Test page shows "Archived" message for archived events

7. GREEN: Implement event page:
   - Add to meetups/views.py:
     - EventDetailView:
       - Look up Event by meetup_slug + event_slug
       - 404 if meetup is deactivated or event doesn't exist
   - Create templates/meetups/event_detail.html
   - Wire up: path("meetups/<slug:meetup_slug>/events/<slug:event_slug>/", ...)

8. Run `just check` to verify everything passes
```

---

## Step 9: Dynamic Multi-Submit Form (HTMX)

**Goal**: Build the multi-submit form with HTMX-powered dynamic field loading. This is the most complex frontend interaction.

```text
Prompt for code-generation LLM:

### Step 9: Dynamic Multi-Submit Form (HTMX)

Build the multi-submit form at /submit/ with HTMX dynamic field loading.

**NOTE**: Steps 1-8 complete. Public pages exist. All models and factories are available. HTMX is included in base template.

1. RED: Write tests for the dynamic field assembly logic:
   - Create submissions/tests/test_form_assembly.py:
     - Test get_dynamic_fields([meetup_a]) returns meetup_a's enabled optional fields and custom questions
     - Test get_dynamic_fields([meetup_a, meetup_b]) returns UNION of optional fields (no duplicates) when both meetups enable the same field
     - Test get_dynamic_fields returns custom questions grouped by meetup
     - Test get_dynamic_fields with no meetups returns empty results
     - Test get_dynamic_fields excludes inactive custom questions
     - Test get_dynamic_fields excludes event-scoped custom questions (those are not part of multi-submit)

2. GREEN: Implement dynamic field assembly:
   - Create submissions/form_assembly.py:
     - get_dynamic_fields(meetup_ids) → dict:
       - "optional_fields": list of StandardOptionalField objects (union across all selected meetups, no duplicates)
       - "custom_questions": dict of {meetup_id: [CustomQuestion, ...]} (only meetup-level, no event questions)
     - Uses MeetupOptionalFieldConfig.objects.filter(meetup_id__in=meetup_ids, is_enabled=True)
     - Uses CustomQuestion.objects.filter(meetup_id__in=meetup_ids, event__isnull=True, is_active=True)

3. RED: Write tests for the HTMX dynamic fields endpoint:
   - Create submissions/tests/test_views.py:
     - Test POST "/submit/dynamic-fields/" with meetup_ids returns 200 with HTML fragment
     - Test the response contains the correct optional fields for selected meetups
     - Test the response contains custom questions grouped by meetup name
     - Test the response with no meetup_ids returns empty fragment
     - Test the response is a partial HTML template (not a full page)

4. GREEN: Implement HTMX dynamic fields endpoint:
   - Create submissions/views.py:
     - dynamic_fields_view (function-based):
       - Accept POST with meetup_ids (list of IDs)
       - Call get_dynamic_fields(meetup_ids)
       - Render partial template submissions/partials/dynamic_fields.html
       - Return HttpResponse with the fragment
   - Create templates/submissions/partials/dynamic_fields.html:
     - Render optional standard fields (inputs based on field_type)
     - Render custom questions grouped under meetup headings
     - Each field gets appropriate input type (text, textarea, select, multi-select, file)
   - Wire up: path("submit/dynamic-fields/", dynamic_fields_view, name="dynamic-fields")

5. GREEN: Build the multi-submit form page:
   - Create submissions/views.py (add to existing):
     - MultiSubmitView:
       - GET: show form with global fields + meetup checkboxes
       - Get all active meetups with open CFPs
       - Pass global fields to template
   - Create templates/submissions/multi_submit.html:
     - Global required fields (name, email, title, abstract, description, bio) always visible
     - Active meetup checkboxes with HTMX attributes:
       - hx-post="/submit/dynamic-fields/"
       - hx-trigger="change"
       - hx-target="#dynamic-fields"
       - hx-include="[name='meetup_ids']" (send all checked meetup IDs)
     - "Select All" button (Alpine.js toggle)
     - <div id="dynamic-fields"></div> target container
     - CAPTCHA placeholder (implemented later)
     - Submit button
   - Wire up: path("submit/", MultiSubmitView, name="multi-submit")

6. GREEN: Build single-meetup submission form:
   - Update meetups/views.py MeetupDetailView:
     - Pass the meetup's form fields to template (global + enabled optional + custom questions)
   - Create templates/submissions/meetup_submit_form.html (included in meetup detail):
     - All global fields
     - Meetup's enabled optional fields
     - Meetup's custom questions
     - CAPTCHA placeholder
     - Submit button
     - Hidden field with meetup ID

7. GREEN: Build event submission form:
   - Update meetups/views.py EventDetailView:
     - Pass event's form fields to template (global + meetup optional + event custom questions)
   - Create templates/submissions/event_submit_form.html:
     - All global fields
     - Meetup's enabled optional fields
     - Event's custom questions
     - CAPTCHA placeholder
     - Submit button

8. Run `just check` to verify all tests pass
```

---

## Step 10: Submission Validation & Duplicate Detection

**Goal**: Implement the form submission processing: validation, duplicate detection, CAPTCHA, and record creation.

```text
Prompt for code-generation LLM:

### Step 10: Submission Validation & Duplicate Detection

Implement submission processing with validation, duplicate detection, and record creation.

**NOTE**: Steps 1-9 complete. Forms exist and render. This step makes them functional.

1. RED: Write tests for duplicate detection logic:
   - Create submissions/tests/test_validation.py:
     - Test detect_duplicate returns True when same email + title + meetup already exists
     - Test detect_duplicate returns False when same email + title but DIFFERENT meetup (allowed)
     - Test detect_duplicate returns False when same email but different title + same meetup
     - Test detect_duplicate returns False when different email + same title + same meetup
     - Test detect_duplicate is case-insensitive on email
     - Test detect_duplicate handles event-specific submissions (same email + title + meetup + event)

2. GREEN: Implement duplicate detection:
   - Create submissions/validation.py:
     - detect_duplicate(email, title, meetup_id, event_id=None) → bool:
       - Query SubmissionMeetup joining Submission
       - Filter by email (case-insensitive), title, meetup, event
       - Exclude withdrawn submissions from duplicate check
       - Return True if exists

3. RED: Write tests for CFP window enforcement:
   - Add to submissions/tests/test_validation.py:
     - Test validate_cfp_open raises ValidationError for meetup with closed CFP
     - Test validate_cfp_open passes for meetup with open CFP
     - Test validate_cfp_open raises ValidationError for deactivated meetup
     - Test validate_cfp_open raises ValidationError for archived event
     - Test validate_cfp_open passes for event with open CFP

4. GREEN: Implement CFP validation:
   - Add to submissions/validation.py:
     - validate_cfp_open(meetup, event=None) → raises ValidationError or passes

5. RED: Write tests for submission creation service:
   - Create submissions/tests/test_services.py:
     - Test create_submission creates Submission record with correct fields
     - Test create_submission creates SubmissionMeetup for each selected meetup
     - Test create_submission creates SubmissionFieldResponse for optional field answers
     - Test create_submission creates SubmissionFieldResponse for custom question answers
     - Test create_submission generates a withdrawal_token
     - Test create_submission raises ValidationError when duplicate detected
     - Test create_submission raises ValidationError when CFP is closed for any selected meetup
     - Test create_submission with file upload creates FileUpload record

6. GREEN: Implement submission creation service:
   - Create submissions/services.py:
     - create_submission(form_data, meetup_ids, event_id=None) → Submission:
       - Validate CFP is open for each meetup/event
       - Check for duplicates per meetup
       - Create Submission record
       - Create SubmissionMeetup records for each meetup
       - Create SubmissionFieldResponse records for field answers
       - Handle file uploads
       - Return the created Submission
     - Uses @transaction.atomic for all-or-nothing creation

7. RED: Write tests for the form submission view:
   - Add to submissions/tests/test_views.py:
     - Test POST to "/submit/" with valid data creates submission and redirects to confirmation
     - Test POST with missing required fields returns form with errors
     - Test POST with duplicate email+title+meetup shows error message
     - Test POST with no meetups selected shows error
     - Test confirmation page shows withdrawal link
     - Test POST to "/meetups/{slug}/submit/" works for single-meetup submission

8. GREEN: Implement form submission views:
   - Update submissions/views.py MultiSubmitView:
     - POST handler: extract form data, call create_submission service
     - On success: redirect to confirmation page with withdrawal token
     - On error: re-render form with errors
   - Create submissions/views.py SubmitConfirmationView:
     - Show confirmation message with withdrawal URL
   - Create meetup_submit_view for single-meetup submissions
   - Create event_submit_view for event submissions
   - Wire up all URLs

9. Run `just check` to verify all tests pass
```

---

## Step 11: Withdrawal Flow

**Goal**: Implement the speaker withdrawal flow using UUID tokens.

```text
Prompt for code-generation LLM:

### Step 11: Withdrawal Flow

Implement the speaker withdrawal system with UUID-based secret URLs.

**NOTE**: Steps 1-10 complete. Submissions can be created. withdrawal_token exists on Submission model.

1. RED: Write tests for withdrawal logic:
   - Create submissions/tests/test_withdrawal.py:
     - Test get_submission_by_token returns the correct Submission for a valid token
     - Test get_submission_by_token returns None for an invalid token
     - Test get_withdrawal_context returns list of SubmissionMeetup records with their status
     - Test withdraw_from_meetups changes status to "withdrawn" for selected meetup IDs
     - Test withdraw_from_meetups does NOT change already-withdrawn entries
     - Test withdraw_from_meetups creates StatusChange audit log for each withdrawal
     - Test withdraw_from_meetups with all meetups effectively withdraws entire submission
     - Test withdraw_from_meetups ignores meetup IDs that don't belong to the submission

2. GREEN: Implement withdrawal logic:
   - Create submissions/withdrawal.py:
     - get_submission_by_token(token) → Submission | None
     - get_withdrawal_context(submission) → list of dicts with meetup name, status, is_withdrawn, submission_meetup_id
     - withdraw_from_meetups(submission, meetup_ids, event_ids=None) → list of StatusChange:
       - For each selected SubmissionMeetup: if not already withdrawn, transition to "withdrawn"
       - Create StatusChange records (changed_by=None for speaker-initiated)
       - Return list of created StatusChange entries

3. RED: Write tests for withdrawal views:
   - Add to submissions/tests/test_views.py or create test_withdrawal_views.py:
     - Test GET "/withdraw/{token}/" returns 200 with submission info
     - Test GET with invalid token returns 404
     - Test withdrawal page shows all meetups with checkboxes
     - Test already-withdrawn meetups are shown but disabled
     - Test POST "/withdraw/{token}/" with selected meetups withdraws them
     - Test POST redirects to confirmation page
     - Test POST with no selections shows error

4. GREEN: Implement withdrawal views:
   - Add to submissions/views.py:
     - WithdrawalView:
       - GET: look up submission by token, show withdrawal form
       - POST: process withdrawal selections
     - WithdrawalConfirmationView:
       - Show confirmation of what was withdrawn
   - Create templates/submissions/withdrawal.html:
     - Show talk title and speaker name
     - List all meetups/events with checkboxes
     - Disabled/greyed out checkboxes for already-withdrawn
     - Confirm button
   - Create templates/submissions/withdrawal_confirmation.html
   - Wire up: path("withdraw/<uuid:token>/", ...)

5. Run `just check` to verify all tests pass
```

---

## Step 12: Dashboard — Authentication & Layout

**Goal**: Set up django-allauth authentication, dashboard base template, and the authenticated layout with navigation.

```text
Prompt for code-generation LLM:

### Step 12: Dashboard — Authentication & Layout

Set up authentication with django-allauth and the dashboard shell.

**NOTE**: Steps 1-11 complete. All public pages and submission flow work. CustomUser has is_superadmin. MeetupRole model exists.

1. Configure django-allauth:
   - Update meetup_cfp/settings/base.py:
     - Add to INSTALLED_APPS: allauth, allauth.account, allauth.socialaccount, allauth.socialaccount.providers.github, allauth.socialaccount.providers.google
     - Add allauth.account.middleware.AccountMiddleware to MIDDLEWARE
     - Set ACCOUNT_EMAIL_REQUIRED = True
     - Set ACCOUNT_USERNAME_REQUIRED = False
     - Set ACCOUNT_AUTHENTICATION_METHOD = "email"
     - Set SOCIALACCOUNT_PROVIDERS config for GitHub and Google (reading client IDs from env vars)
     - Set LOGIN_URL = "/accounts/login/"
     - Set LOGIN_REDIRECT_URL = "/dashboard/"
   - Add to meetup_cfp/urls.py: path("accounts/", include("allauth.urls"))

2. RED: Write tests for dashboard access control:
   - Create dashboard/tests/__init__.py
   - Create dashboard/tests/test_views.py:
     - Test GET "/dashboard/" redirects to login for anonymous users
     - Test GET "/dashboard/" returns 200 for authenticated super-admin
     - Test GET "/dashboard/" returns 200 for authenticated user with at least one meetup role
     - Test GET "/dashboard/" returns 403 for authenticated user with NO meetup roles and NOT super-admin
     - Test GET "/dashboard/meetups/{slug}/" returns 200 for user with role on that meetup
     - Test GET "/dashboard/meetups/{slug}/" returns 403 for user with no role on that meetup
     - Test GET "/dashboard/meetups/{slug}/" returns 200 for super-admin (even without explicit role)

3. GREEN: Implement dashboard base views:
   - Create dashboard/views.py:
     - DashboardHomeView (LoginRequiredMixin):
       - Super-admin: show super-admin dashboard
       - Regular user: show list of meetups they have roles on
     - MeetupDashboardView (LoginRequiredMixin + MeetupRoleRequiredMixin):
       - required_role = "read"
       - Show meetup dashboard (just shell for now)
   - Create templates/dashboard/base.html:
     - Sidebar or top nav with: Dashboard home, list of user's meetups, logout
     - Main content area with {% block dashboard_content %}
     - Show user name and role badge
   - Create templates/dashboard/home.html
   - Create templates/dashboard/meetup_dashboard.html (shell)
   - Wire up: path("dashboard/", ...), path("dashboard/meetups/<slug:slug>/", ...)

4. REFACTOR: Create allauth template overrides for consistent styling:
   - Create templates/account/login.html (extends base.html, Tailwind styled)
   - Create templates/account/signup.html
   - Create templates/account/logout.html
   - These override allauth's default templates with project styling

5. Run `just check` to verify all tests pass
```

---

## Step 13: Dashboard — Meetup Submissions View

**Goal**: Build the submissions table view with filtering, sorting, and search. This is the main working view for organizers.

```text
Prompt for code-generation LLM:

### Step 13: Dashboard — Meetup Submissions View

Build the submissions table with filtering, sorting, and search for the meetup dashboard.

**NOTE**: Steps 1-12 complete. Dashboard shell exists with auth. All models and factories available.

1. RED: Write tests for submission filtering logic:
   - Create dashboard/tests/test_filters.py:
     - Test filter_submissions with no filters returns all submissions for a meetup
     - Test filter by status returns only matching submissions
     - Test filter by date range (submitted after/before) works correctly
     - Test search by title (case-insensitive partial match)
     - Test search by speaker name (case-insensitive partial match)
     - Test sorting by submitted date (ascending and descending)
     - Test sorting by title
     - Test sorting by vote count (thumbs_up - thumbs_down)
     - Test combining filters: status + date range + search

2. GREEN: Implement submission filtering:
   - Create dashboard/filters.py:
     - filter_submissions(meetup, params) → QuerySet:
       - Base: SubmissionMeetup.objects.filter(meetup=meetup).select_related("submission")
       - Apply status filter if present
       - Apply date range filter if present
       - Apply search (title OR speaker name icontains)
       - Apply sort_by parameter
       - Annotate with vote counts (thumbs_up_count, thumbs_down_count)
       - Return queryset

3. RED: Write tests for the submissions list view:
   - Add to dashboard/tests/test_views.py:
     - Test GET "/dashboard/meetups/{slug}/" shows submissions table
     - Test submissions table shows: title, speaker, status, submitted date, vote summary
     - Test filter parameters in URL update the displayed submissions
     - Test the view paginates results (if more than 25)
     - Test Write+ users see bulk action checkboxes
     - Test Read/Reviewer users do NOT see bulk action checkboxes
     - Test the export button is visible for Write+ users only

4. GREEN: Implement submissions list view:
   - Update dashboard/views.py MeetupDashboardView:
     - Use filter_submissions to get the queryset
     - Paginate (25 per page)
     - Pass user's role for template conditional rendering
   - Create/update templates/dashboard/meetup_dashboard.html:
     - Filter controls: status dropdown, date pickers, search box
     - Use HTMX for filter/search (hx-get to reload table fragment)
     - Submissions table with columns per spec
     - Vote summary column (thumbs up/down counts)
     - Bulk action checkboxes (conditionally shown)
     - Export button (conditionally shown)
     - Pagination controls

5. Run `just check` to verify all tests pass
```

---

## Step 14: Dashboard — Submission Detail & Reviews

**Goal**: Build the submission detail page with voting, notes, and communication tracking.

```text
Prompt for code-generation LLM:

### Step 14: Dashboard — Submission Detail & Reviews

Build the submission detail page with all review functionality.

**NOTE**: Steps 1-13 complete. Submission list view works. Review, Note, StatusChange models exist.

1. RED: Write tests for submission detail view:
   - Create dashboard/tests/test_submission_detail.py:
     - Test GET "/dashboard/meetups/{slug}/submissions/{id}/" returns 200 for user with role
     - Test 403 for user without role on this meetup
     - Test page displays all submitted fields (title, abstract, description, bio, optional fields, custom question responses)
     - Test page shows current status badge
     - Test page shows file upload links for uploaded files
     - Test page shows list of other meetups this submission targets (for Write+ only, without their votes/notes)

2. GREEN: Implement submission detail view:
   - Add to dashboard/views.py:
     - SubmissionDetailView (LoginRequiredMixin + MeetupRoleRequiredMixin):
       - required_role = "read"
       - Look up SubmissionMeetup by meetup slug + submission ID
       - Load all field responses
       - Load other targeted meetups (for Write+ context)
       - Pass user's role for conditional rendering
   - Create templates/dashboard/submission_detail.html:
     - Proposal info section: all fields displayed
     - Status badge
     - File downloads for uploaded files
   - Wire up URL

3. RED: Write tests for voting:
   - Add to dashboard/tests/test_submission_detail.py:
     - Test Reviewer+ can see vote buttons
     - Test Read user cannot see vote buttons
     - Test POST vote creates Review record
     - Test POST vote updates existing vote (change from up to down)
     - Test vote counts update after voting
     - Test all existing votes are displayed with reviewer names

4. GREEN: Implement voting:
   - Add to dashboard/views.py:
     - VoteView (function-based or CBV):
       - Accept POST with vote (thumbs_up/thumbs_down)
       - Create or update Review record
       - Return HTMX fragment with updated vote display
   - Update submission_detail.html:
     - Vote section with thumbs up/down buttons (HTMX POST)
     - List of all votes with reviewer names
     - Vote counts
   - Wire up URL

5. RED: Write tests for notes:
   - Add to dashboard/tests/test_submission_detail.py:
     - Test Reviewer+ can see "Add note" form
     - Test Read user cannot see "Add note" form
     - Test POST note creates Note record
     - Test notes display chronologically with author and timestamp
     - Test empty note body is rejected

6. GREEN: Implement notes:
   - Add to dashboard/views.py:
     - AddNoteView:
       - Accept POST with note body
       - Create Note record
       - Return HTMX fragment with updated notes list
   - Update submission_detail.html:
     - Notes section: chronological list
     - "Add note" form (HTMX POST)
   - Wire up URL

7. RED: Write tests for status management:
   - Add to dashboard/tests/test_submission_detail.py:
     - Test Write+ user sees status change controls
     - Test Read/Reviewer user does NOT see status change controls
     - Test POST status change calls transition_status
     - Test invalid transition shows error message
     - Test status history log is displayed
     - Test transitioning to "scheduled" shows date picker
     - Test transitioning to "scheduled" without date shows error

8. GREEN: Implement status management:
   - Add to dashboard/views.py:
     - ChangeStatusView:
       - Accept POST with new_status and optional scheduled_date
       - Call transition_status from reviews/transitions.py
       - Return HTMX fragment with updated status display and history
   - Update submission_detail.html:
     - Status change dropdown/buttons (showing only valid next statuses)
     - Date picker (visible for "scheduled" transition)
     - Status history log (StatusChange records)
     - "Mark Email Sent" convenience button
   - Wire up URL

9. Run `just check` to verify all tests pass
```

---

## Step 15: Dashboard — Bulk Actions & Status Management

**Goal**: Implement bulk status changes from the submissions list view.

```text
Prompt for code-generation LLM:

### Step 15: Dashboard — Bulk Actions & Status Management

Implement bulk operations on the submissions list.

**NOTE**: Steps 1-14 complete. Submission list and detail views work. Status transition logic exists.

1. RED: Write tests for bulk status change:
   - Create dashboard/tests/test_bulk_actions.py:
     - Test bulk status change updates all selected submissions
     - Test bulk status change creates StatusChange audit logs for each submission
     - Test bulk status change skips submissions where the transition is invalid (and reports which were skipped)
     - Test bulk status change requires Write+ permission
     - Test Reviewer cannot perform bulk actions (403)
     - Test bulk status change with no selections returns error

2. GREEN: Implement bulk status change:
   - Create dashboard/bulk_actions.py:
     - bulk_change_status(submission_meetup_ids, new_status, changed_by) → dict:
       - Returns {"changed": [...], "skipped": [...], "errors": [...]}
       - For each SubmissionMeetup: attempt transition, record success/skip/error
       - Uses transaction.atomic per individual change (not all-or-nothing)

3. GREEN: Implement bulk action view:
   - Add to dashboard/views.py:
     - BulkActionView:
       - Accept POST with action type + list of submission_meetup_ids
       - Call bulk_change_status
       - Return HTMX fragment refreshing the submissions table with result message
   - Update templates/dashboard/meetup_dashboard.html:
     - Bulk action bar (appears when checkboxes are selected, Alpine.js)
     - Status dropdown for bulk change
     - "Apply" button
     - Results message showing changed/skipped counts
   - Wire up URL

4. Run `just check` to verify all tests pass
```

---

## Step 16: Dashboard — Export (CSV/JSON)

**Goal**: Implement CSV and JSON export of submission data.

```text
Prompt for code-generation LLM:

### Step 16: Dashboard — Export (CSV/JSON)

Implement data export respecting current filters and permissions.

**NOTE**: Steps 1-15 complete. Submissions list with filtering works. filter_submissions function exists.

1. RED: Write tests for CSV export:
   - Create dashboard/tests/test_export.py:
     - Test CSV export contains correct headers (Title, Speaker Name, Speaker Email, Status, Submitted Date, Scheduled Date, Thumbs Up, Thumbs Down, plus columns for each custom question)
     - Test CSV export contains correct data for submissions
     - Test CSV export respects current filters (status, date range, search)
     - Test CSV export handles submissions with missing optional fields (empty cells)
     - Test CSV export handles custom questions with varying schemas across submissions
     - Test CSV export requires Write+ permission
     - Test Reviewer gets 403 on export attempt

2. GREEN: Implement CSV export:
   - Create dashboard/export.py:
     - generate_csv(meetup, queryset) → HttpResponse:
       - Build header row: fixed columns + dynamic columns for enabled optional fields + custom questions
       - Build data rows from queryset with field responses
       - Return HttpResponse with content_type="text/csv" and Content-Disposition header

3. RED: Write tests for JSON export:
   - Add to dashboard/tests/test_export.py:
     - Test JSON export has correct nested structure (submission as parent, meetup data as child)
     - Test JSON export includes all field responses
     - Test JSON export respects current filters
     - Test JSON export requires Write+ permission

4. GREEN: Implement JSON export:
   - Add to dashboard/export.py:
     - generate_json(meetup, queryset) → HttpResponse:
       - Build nested structure: each submission with its field responses and meetup-specific data
       - Return HttpResponse with content_type="application/json"

5. GREEN: Implement export view:
   - Add to dashboard/views.py:
     - ExportView:
       - Accept GET with format parameter (csv or json)
       - Apply current filter parameters (reuse filter_submissions)
       - Call appropriate export function
       - Return file download response
   - Update meetup dashboard template: export button with format dropdown
   - Wire up URL

6. Run `just check` to verify all tests pass
```

---

## Step 17: Dashboard — Super-Admin Views & Warnings

**Goal**: Build the super-admin dashboard with cross-meetup overview, warnings, and management views.

```text
Prompt for code-generation LLM:

### Step 17: Dashboard — Super-Admin Views & Warnings

Build the super-admin dashboard and warning system.

**NOTE**: Steps 1-16 complete. Per-meetup dashboards work fully. Export works.

1. RED: Write tests for dashboard warnings:
   - Create dashboard/tests/test_warnings.py:
     - Test get_meetup_warnings returns "no upcoming speaker" when no submission has status "scheduled" with a future date
     - Test get_meetup_warnings returns empty when a scheduled submission has a future date
     - Test get_meetup_warnings ignores past scheduled dates
     - Test get_all_warnings returns warnings for all active meetups

2. GREEN: Implement warning logic:
   - Create dashboard/warnings.py:
     - get_meetup_warnings(meetup) → list of warning strings
     - get_all_warnings() → dict of {meetup: [warnings]}

3. RED: Write tests for super-admin dashboard view:
   - Add to dashboard/tests/test_views.py:
     - Test GET "/dashboard/" as super-admin shows summary cards
     - Test summary cards show: total submissions, submissions this month, acceptance rate
     - Test per-meetup breakdown table shows correct counts
     - Test warning alerts are displayed for meetups with warnings
     - Test recent activity feed shows latest status changes
     - Test non-super-admin does not see the super-admin dashboard content

4. GREEN: Implement super-admin dashboard:
   - Update dashboard/views.py DashboardHomeView:
     - For super-admins:
       - Calculate total submissions, this-month submissions, acceptance rate
       - Get per-meetup breakdown (submission counts by status)
       - Get all warnings
       - Get recent activity (latest StatusChange entries across all meetups)
     - For regular users:
       - Show list of their meetups with basic stats
   - Create/update templates/dashboard/home.html:
     - Super-admin section: summary cards, per-meetup table, warning alerts, activity feed
     - Regular user section: meetup list with role badges

5. RED: Write tests for meetup management views (super-admin):
   - Create dashboard/tests/test_management.py:
     - Test super-admin can access meetup create/edit forms
     - Test non-super-admin cannot access meetup management (403)
     - Test meetup creation creates a new Meetup
     - Test meetup deactivation sets is_active=False

6. GREEN: Implement meetup management views:
   - Add to dashboard/views.py:
     - MeetupManagementView: list all meetups with create/edit/deactivate actions
     - MeetupCreateView, MeetupEditView
     - Global field management view (list/toggle global fields)
     - User role management view (assign roles to users per meetup)
   - Create corresponding templates
   - Wire up URLs

7. GREEN: Implement meetup admin views (per-meetup admin):
   - Add to dashboard/views.py:
     - MeetupSettingsView (admin role required):
       - Edit meetup info (name, description, logo, colors)
       - Toggle optional standard fields on/off
       - CRUD custom questions
     - EventManagementView (admin role required):
       - List events, create/edit/archive events
       - Manage event-specific custom questions
   - Create corresponding templates
   - Wire up URLs

8. Run `just check` to verify all tests pass
```

---

## Step 18: Management Commands & Data Seeding

**Goal**: Build remaining management commands and ensure the app can be bootstrapped cleanly.

```text
Prompt for code-generation LLM:

### Step 18: Management Commands & Data Seeding

Finalize management commands and ensure clean bootstrapping.

**NOTE**: Steps 1-17 complete. The application is functionally complete. seed_global_fields exists from Step 2.

1. RED: Write tests for seed_standard_fields idempotency:
   - Update core/tests/test_commands.py:
     - Test seed_global_fields is fully idempotent (run 3 times, same result)
     - Test it handles field updates gracefully (if a field label changes in seed data, update existing)

2. GREEN: Ensure seed_global_fields handles edge cases:
   - Update core/management/commands/seed_global_fields.py if needed

3. RED: Write tests for a create_test_data management command:
   - Create core/tests/test_commands.py (add to existing):
     - Test create_test_data creates sample meetups, submissions, and reviews
     - Test it's idempotent
     - Test it only runs when DEBUG=True

4. GREEN: Implement create_test_data command:
   - Create core/management/commands/create_test_data.py:
     - Create sample Organization
     - Create 2-3 sample Meetups with different CFP modes
     - Create sample Events
     - Create sample Submissions with multi-meetup targeting
     - Create sample users with various roles
     - Only runs when DEBUG=True (refuse in production)

5. Verify the full bootstrap sequence works:
   - Run: uv run python manage.py migrate
   - Run: uv run python manage.py seed_global_fields
   - Run: uv run python manage.py create_test_data
   - Run: uv run python manage.py runserver
   - Manually verify (or write a smoke test) that the landing page, submission form, and dashboard all load

6. Run `just check` to verify all tests pass
```

---

## Step 19: Docker & Production Configuration

**Goal**: Create Docker configuration for production deployment.

```text
Prompt for code-generation LLM:

### Step 19: Docker & Production Configuration

Set up Docker Compose for production deployment.

**NOTE**: Steps 1-18 complete. The application is fully functional in development.

1. Create Dockerfile:
   - Create Dockerfile:
     - Base image: python:3.12-slim
     - Install system deps (libpq-dev for psycopg)
     - Install uv
     - Copy pyproject.toml and uv.lock
     - Run uv sync --no-dev
     - Copy application code
     - Run collectstatic
     - Run tailwind build
     - Set ENTRYPOINT to gunicorn meetup_cfp.wsgi:application

2. Create docker-compose.yml:
   - Create docker-compose.yml:
     - web service: builds from Dockerfile, exposes 8000, depends on db, reads .env
     - db service: postgres:16, volume for data persistence, health check
     - nginx service: nginx:alpine, proxies to web, serves static/media files
     - Volumes: postgres_data, static_files, media_files

3. Create nginx configuration:
   - Create nginx/nginx.conf:
     - Upstream to web:8000
     - Serve /static/ from static_files volume
     - Serve /media/ from media_files volume
     - Proxy all other requests to upstream
     - Security headers

4. Create .env.example:
   - Create .env.example with all required environment variables and safe defaults:
     - DATABASE_URL, SECRET_KEY, ALLOWED_HOSTS, DEBUG
     - CAPTCHA_SITE_KEY, CAPTCHA_SECRET_KEY
     - GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
     - GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

5. Create entrypoint script:
   - Create docker/entrypoint.sh:
     - Wait for database to be ready
     - Run migrations
     - Run seed_global_fields
     - Run collectstatic (no input)
     - Start gunicorn

6. Update production settings:
   - Verify meetup_cfp/settings/prod.py handles:
     - DATABASE_URL parsing (use dj-database-url or manual parse)
     - STATIC_ROOT for collectstatic
     - MEDIA_ROOT for file uploads
     - Security settings: SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE
     - WhiteNoise for static file serving (as fallback)

7. Test Docker build:
   - Run `docker compose build` to verify the image builds
   - Run `docker compose up` to verify services start
   - Verify the app is accessible via nginx

8. Run `just check` one final time to ensure everything is clean
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
- Business logic in separate modules (`app/validation.py`, `app/services.py`, `app/transitions.py`)
- Tests in `app/tests/test_*.py` (not in model/view files)
- Factories in `tests/factories.py` at project root

### Testing Boundaries
- Test YOUR business logic: validation rules, permission checks, status transitions, duplicate detection, form assembly, export formatting
- Do NOT test Django: model creation, ORM queries returning results, form rendering, middleware
- Use factories for test data, not raw model creation
- Use `pytest.mark.django_db` for database tests

### Key Patterns
- Permission checks: always use `has_meetup_role` / helper functions, never raw role comparison
- Status transitions: always go through `transition_status`, never set status directly
- Submission creation: always use the service layer, never create records directly in views
- Branding: always use `effective_*` properties, never access raw fields in templates

---

## Success Metrics

1. **All tests pass**: `just check` exits 0
2. **Clean lint**: `ruff check .` reports no issues
3. **Clean formatting**: `ruff format --check .` reports no issues
4. **All business rules enforced**: duplicate detection, CFP windows, role hierarchy, status transitions
5. **Public pages work**: landing, meetup detail, event detail, submission forms, withdrawal
6. **Dashboard works**: auth, submissions list, detail, voting, notes, status changes, bulk actions, export
7. **Docker deploys**: `docker compose up` serves the full application
8. **Seed data works**: `seed_global_fields` and `create_test_data` run cleanly
