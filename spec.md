# meetup-cfp: Call for Proposals Platform Specification

## Overview

A multi-meetup Call for Proposals (CFP) platform that allows speakers to submit talk proposals to one or more meetups within a single organization. The system provides role-based dashboards for meetup organizers to review, manage, and track submissions through their full lifecycle.

The public surface is intentionally minimal — submission forms only, no event listings or talk history. All communication with speakers happens outside the platform; the app tracks status and notes.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x |
| Frontend | Tailwind CSS (`django-tailwind-cli`), HTMX, Alpine.js |
| Database | SQLite (development), PostgreSQL (production) |
| Auth | `django-allauth` (Django auth + GitHub & Google OAuth) |
| Spam Prevention | CAPTCHA (hCaptcha or Cloudflare Turnstile) |
| Deployment | Docker Compose on self-hosted VPS |
| Package Management | `uv` |
| File Storage | Local volume mount (Docker volume) |

---

## Django Project Structure

**Project name**: `meetup_cfp`

### Apps

| App | Responsibility |
|-----|---------------|
| `core` | Organization settings, global form field configuration, base models/mixins |
| `meetups` | Meetup models, branding, events, CFP window configuration, archival |
| `submissions` | Proposals, custom questions, form rendering, file uploads, withdrawal |
| `reviews` | Voting, notes, communication tracking, status management |
| `users` | Auth integration, role/permission models, per-meetup role assignment |
| `dashboard` | Admin views, reporting, filtering, export (CSV/JSON), warnings |

---

## Data Model

### Organization (singleton)

The organization is a single-instance configuration managed by super-admins.

- `name`: string
- `slug`: string (URL-friendly)
- `description`: text
- `logo`: image file
- `primary_color`: hex color (default branding)
- `secondary_color`: hex color

### Meetup

Each meetup belongs to the organization and has its own identity and configuration.

- `name`: string
- `slug`: string (unique, used in URLs like `/meetups/{slug}/`)
- `description`: text
- `logo`: image file (optional, falls back to org logo)
- `primary_color`: hex color (optional, inherits from org)
- `secondary_color`: hex color (optional, inherits from org)
- `is_active`: boolean (deactivated meetups stop accepting submissions, hidden from public)
- `cfp_mode`: enum (`year_round`, `time_boxed`)
- `cfp_open_date`: datetime (nullable, for time-boxed mode)
- `cfp_close_date`: datetime (nullable, for time-boxed mode)
- `created_at`: datetime
- `updated_at`: datetime

**Business rules:**
- Deactivated meetups retain all data but are hidden from public pages and stop accepting submissions.
- Only meetups with an open CFP appear in the multi-submit form.
- A meetup's branding cascades from the org unless explicitly overridden.

### Event (Special Event)

Events are time-boxed CFPs under a meetup with their own submission pool.

- `meetup`: FK → Meetup
- `name`: string
- `slug`: string (unique within meetup, URL: `/meetups/{meetup_slug}/events/{event_slug}/`)
- `description`: text
- `date`: date (event date)
- `cfp_open_date`: datetime
- `cfp_close_date`: datetime
- `is_archived`: boolean
- `created_at`: datetime

**Business rules:**
- Events inherit the meetup's standard questions but can have their own custom questions.
- Events are NOT included in the multi-submit flow — speakers must submit directly via the event URL.
- Archived events retain data but stop accepting submissions.

### GlobalFormField

Base fields enforced across all meetups, managed by super-admins.

- `label`: string
- `field_type`: enum (`short_text`, `long_text`, `single_select`, `multi_select`, `file_upload`)
- `is_required`: boolean
- `options`: JSON (for select types, stores list of choices)
- `sort_order`: integer
- `is_active`: boolean

**Default global fields (seeded on setup):**

| Field | Type | Required |
|-------|------|----------|
| Name | short_text | yes |
| Email | short_text (email) | yes |
| Talk Title | short_text | yes |
| Abstract | long_text | yes |
| Description | long_text | yes |
| Speaker Bio | long_text | yes |

### StandardOptionalField

Optional standard fields that meetup admins can toggle on/off per meetup.

- `label`: string
- `field_type`: enum (same as above)
- `options`: JSON (for select types)
- `sort_order`: integer

**Available standard optional fields:**

| Field | Type |
|-------|------|
| Talk Length | single_select (15 min, 30 min, 45 min, 60 min) |
| Experience Level | single_select (Beginner, Intermediate, Advanced) |
| Speaker Headshot | file_upload |
| Speaker Links | short_text (URL) |
| Prior Speaking Experience | long_text |

### MeetupOptionalFieldConfig

Junction table: which standard optional fields a meetup has enabled.

- `meetup`: FK → Meetup
- `standard_field`: FK → StandardOptionalField
- `is_enabled`: boolean

### CustomQuestion

Per-meetup (or per-event) custom questions created by meetup admins.

- `meetup`: FK → Meetup
- `event`: FK → Event (nullable; if null, applies to the meetup's default CFP)
- `label`: string
- `field_type`: enum (`short_text`, `long_text`, `single_select`, `multi_select`, `file_upload`)
- `is_required`: boolean
- `options`: JSON (for select types)
- `sort_order`: integer
- `is_active`: boolean

### Submission

A single proposal from a speaker. One record regardless of how many meetups it targets.

- `speaker_name`: string
- `speaker_email`: email
- `withdrawal_token`: UUID (for secret withdrawal URL)
- `created_at`: datetime
- `updated_at`: datetime

**Populated from global fields:**
- `title`: string
- `abstract`: text
- `description`: text
- `speaker_bio`: text

### SubmissionMeetup

Junction table linking a submission to each targeted meetup. This is where per-meetup status lives — no data duplication.

- `submission`: FK → Submission
- `meetup`: FK → Meetup
- `event`: FK → Event (nullable; for event-specific submissions)
- `status`: enum (see Submission Lifecycle below)
- `scheduled_date`: date (nullable, set when status is "Scheduled")
- `created_at`: datetime
- `updated_at`: datetime

**Unique constraint**: (`submission`, `meetup`, `event`) — prevents duplicate submissions of the same proposal to the same meetup/event.

### SubmissionFieldResponse

Stores answers to optional standard fields and custom questions.

- `submission`: FK → Submission
- `global_field`: FK → GlobalFormField (nullable)
- `standard_field`: FK → StandardOptionalField (nullable)
- `custom_question`: FK → CustomQuestion (nullable)
- `value_text`: text (for text responses)
- `value_file`: file (for file uploads)

**Constraint**: Exactly one of `global_field`, `standard_field`, or `custom_question` must be set.

### Review (Vote)

- `submission_meetup`: FK → SubmissionMeetup
- `reviewer`: FK → User
- `vote`: enum (`thumbs_up`, `thumbs_down`)
- `created_at`: datetime

**Unique constraint**: (`submission_meetup`, `reviewer`) — one vote per reviewer per meetup-submission.

### Note

Internal notes per submission per meetup.

- `submission_meetup`: FK → SubmissionMeetup
- `author`: FK → User
- `body`: text
- `created_at`: datetime

### StatusChange (Audit Log)

- `submission_meetup`: FK → SubmissionMeetup
- `changed_by`: FK → User
- `old_status`: string
- `new_status`: string
- `changed_at`: datetime

### FileUpload

- `submission`: FK → Submission
- `field_response`: FK → SubmissionFieldResponse
- `file`: file field (stored on local volume)
- `original_filename`: string
- `uploaded_at`: datetime

---

## Submission Lifecycle

### Initial Review Phase

```
Submitted → Under Review → Accepted
                         → Rejected
                         → Waitlisted
                         → Withdrawn
```

### Post-Acceptance Phase

```
Accepted → Email Sent → Speaker Accepted → Scheduled → Presented
```

All status transitions are manual. The `scheduled_date` field on `SubmissionMeetup` is set when the status moves to "Scheduled."

### Withdrawal

- Each submission gets a unique `withdrawal_token` (UUID v4).
- The withdrawal URL format: `/withdraw/{withdrawal_token}/`
- The withdrawal page shows all meetups/events the submission targets.
- The speaker selects which meetup(s) to withdraw from via checkboxes.
- Withdrawal tokens never expire — valid as long as the submission exists.
- Withdrawing from all meetups effectively withdraws the entire submission.

### Duplicate Detection

When a speaker submits, the system checks for existing submissions with the same `speaker_email` + `title` targeting the same meetup.

- If a duplicate is found: block the submission and display a warning.
- This check runs per-meetup, so the same talk CAN be submitted to different meetups (that's the intended behavior via multi-submit).

---

## Permission Model

### Role Hierarchy

```
Read → Reviewer → Write → Admin → Super-Admin
```

Each level inherits all capabilities of the levels below it.

### Role Definitions

| Role | Scope | Capabilities |
|------|-------|-------------|
| **Super-Admin** | Global | Manage all meetups (CRUD, archive). Manage global form fields. Assign admins to meetups. View all submissions across all meetups. Full access to everything. |
| **Admin** | Per-meetup | Create/edit custom questions. Update meetup settings (name, description, logo, branding). Create and manage special events. Everything Write can do. |
| **Write** | Per-meetup | Manage submissions (change status, bulk actions). Add notes. Track communication status. Manage reviewers (assign/remove Reviewer role). Export data. |
| **Reviewer** | Per-meetup | View submissions for their meetup. Vote (thumbs up/down). Add internal notes. |
| **Read** | Per-meetup | View submissions and their statuses. View votes and notes. No modifications. |

### Implementation

- Roles are assigned per-meetup via a `MeetupRole` model:
  - `user`: FK → User
  - `meetup`: FK → Meetup
  - `role`: enum (`read`, `reviewer`, `write`, `admin`)
  - **Unique constraint**: (`user`, `meetup`)
- Super-Admin is a flag on the User model (`is_superadmin`: boolean), separate from Django's built-in `is_superuser`.
- Users can have different roles on different meetups (e.g., Admin on Dallas, Read on Houston).
- Auth is handled via `django-allauth` with GitHub and Google OAuth providers. Users must have an account to access any dashboard.

---

## Public-Facing Pages

The public surface is minimal — submission forms only.

### Org Landing Page (`/`)

- Organization name, logo, description.
- List of all **active** meetups (name, logo, short description).
- "Submit to Multiple Meetups" button.
- Each meetup links to its individual page.

### Multi-Submit Form (`/submit/`)

- Checkboxes for each active meetup with an open CFP.
- "Select All" button that checks all boxes.
- Global required fields always shown.
- **Dynamic behavior (HTMX):** When meetups are selected/deselected, the form dynamically loads:
  - Optional standard fields enabled by any selected meetup.
  - Custom questions for each selected meetup, grouped by meetup name.
- CAPTCHA at the bottom of the form.
- On success: confirmation page with the withdrawal link prominently displayed.

### Meetup Page (`/meetups/{slug}/`)

- Meetup name, logo, description (with meetup's branding/colors).
- Submission form for this meetup only (no multi-select).
- Shows global fields + meetup's enabled optional fields + meetup's custom questions.
- If CFP is closed (time-boxed mode, outside window): show a message instead of the form.
- If meetup is deactivated: 404.
- CAPTCHA on form.

### Event Page (`/meetups/{meetup_slug}/events/{event_slug}/`)

- Event name, description, date.
- CFP open/close dates displayed.
- Submission form scoped to this event.
- Shows global fields + meetup's enabled optional fields + event's custom questions.
- If CFP is closed: show a message.
- If event is archived: show archived message, no form.
- CAPTCHA on form.

### Withdrawal Page (`/withdraw/{token}/`)

- Shows the submission's talk title and speaker name.
- Lists all meetups/events this submission targets with checkboxes.
- Speaker selects which to withdraw from and confirms.
- Already-withdrawn entries shown as disabled/greyed out.

---

## Dashboard (Authenticated)

All dashboard pages require login via `django-allauth`.

### Super-Admin Dashboard (`/dashboard/`)

- **Summary cards**: Total submissions (all meetups), submissions this month, acceptance rate.
- **Per-meetup breakdown table**: Meetup name, submission count, status counts (submitted, under review, accepted, etc.).
- **Warning alerts**: Meetups with no upcoming scheduled speaker.
- **Recent activity feed**: Latest submissions, status changes, votes.
- **Quick links**: Manage meetups, manage global fields, manage users.

### Meetup Dashboard (`/dashboard/meetups/{slug}/`)

Visible to all roles assigned to that meetup. Content varies by role.

- **Warning alert**: "No upcoming speaker scheduled" if no submission has status "Scheduled" with a future date.
- **Submissions table** (all roles):
  - Columns: Title, Speaker, Status, Submitted Date, Scheduled Date, Vote Summary (thumbs up/down counts).
  - Filtering: by status, by date range, by search (title/speaker name).
  - Sorting: by date, by title, by vote count.
- **Bulk actions** (Write+ only):
  - Select multiple submissions via checkboxes.
  - Bulk status change (e.g., reject all selected).
- **Export button** (Write+ only): CSV or JSON export of current filtered view.
- **Meetup settings link** (Admin only): Edit meetup info, custom questions, optional field toggles.
- **Events section** (Admin only): Create/manage special events.

### Submission Detail (`/dashboard/meetups/{slug}/submissions/{id}/`)

- **Proposal info**: All submitted fields (title, abstract, description, bio, optional fields, custom question responses, uploaded files).
- **Status badge** with current status.
- **Status change controls** (Write+): Dropdown/buttons to transition status.
- **Review section**:
  - List of all votes with reviewer names (all roles can see).
  - Vote buttons for thumbs up/down (Reviewer+).
- **Notes section**:
  - Chronological list of internal notes with author and timestamp.
  - "Add note" form (Reviewer+).
- **Communication tracking** (Write+):
  - "Mark Email Sent" button.
  - Status history log (who changed what, when).
- **Other meetups** (Write+): List of other meetups/events this proposal was submitted to (without exposing other meetups' votes/notes).
- **Scheduled date** (Write+): Date picker, visible when status is "Scheduled" or later.

---

## Dynamic Form Behavior (HTMX)

The multi-submit form is the most interactive part of the public UI.

### Multi-Submit Form Flow

1. Speaker lands on `/submit/`.
2. Global required fields (name, email, title, abstract, description, bio) are always visible.
3. Speaker checks meetup boxes. Each change fires an HTMX request.
4. Server responds with a partial HTML fragment containing:
   - Union of all enabled optional standard fields for the selected meetups.
   - Custom questions grouped under each meetup's name heading.
   - If a meetup has required custom questions, those are marked as required.
5. Speaker fills out all fields and submits.
6. Server validates:
   - All global required fields present.
   - All enabled optional fields that are required by any selected meetup.
   - All required custom questions per meetup.
   - CAPTCHA valid.
   - No duplicate (same email + title + meetup).
7. On success: create `Submission` + `SubmissionMeetup` records + `SubmissionFieldResponse` records. Display confirmation with withdrawal link.

### HTMX Endpoint

- `POST /submit/dynamic-fields/` — accepts list of selected meetup IDs, returns HTML fragment of additional form fields.
- Uses `hx-post`, `hx-trigger="change"`, `hx-target="#dynamic-fields"` on each meetup checkbox.

---

## Export

- **CSV export**: Flat file with one row per submission-meetup combination. Columns include all global fields, status, scheduled date, vote counts, custom question responses.
- **JSON export**: Nested structure with submission as parent and meetup-specific data as children.
- Export respects the current filter state in the dashboard.
- Available to Write, Admin, and Super-Admin roles.

---

## Deployment

### Docker Compose Services

| Service | Image/Build |
|---------|------------|
| `web` | Django app (Gunicorn) |
| `db` | PostgreSQL 16 |
| `nginx` | Nginx (reverse proxy, static files, uploads) |

### Volumes

- `postgres_data`: PostgreSQL data persistence.
- `static_files`: Collected static files (Tailwind CSS output, etc.).
- `media_files`: User-uploaded files (headshots, file upload responses).

### Environment Configuration

- `DATABASE_URL`: PostgreSQL connection string (production) or SQLite path (development).
- `SECRET_KEY`: Django secret key.
- `ALLOWED_HOSTS`: Comma-separated hostnames.
- `CAPTCHA_SITE_KEY` / `CAPTCHA_SECRET_KEY`: CAPTCHA provider keys.
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`: GitHub OAuth.
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: Google OAuth.
- `DEBUG`: Boolean, false in production.

### Development Setup

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_global_fields  # Creates default global form fields
uv run python manage.py createsuperuser
uv run python manage.py tailwind build
uv run python manage.py runserver
```

---

## Key Business Rules Summary

1. **Global fields** are managed exclusively by super-admins and apply to all meetups and events.
2. **Optional standard fields** are toggled on/off per meetup by meetup admins.
3. **Custom questions** are per-meetup or per-event, created by meetup admins.
4. **Multi-submit** only targets default meetup CFPs (not special events).
5. **Special events** require direct URL submission and are not included in multi-submit.
6. **Duplicate detection**: Same email + title + same meetup = blocked. Same talk to different meetups = allowed.
7. **Withdrawal** is per-meetup — speaker chooses which meetups to withdraw from.
8. **Branding** cascades: org → meetup (override optional).
9. **CFP windows**: Default is year-round. Can be time-boxed per meetup. Events are always time-boxed.
10. **Deactivated meetups** retain data, hidden from public, stop accepting submissions.
11. **Archived events** retain data, stop accepting submissions, show archived status.
12. **No automated emails** — all communication happens outside the platform.
13. **File uploads** stored on local volume mount, served via nginx.

---

## Testable Business Logic Components

These are the core pieces of application logic that should be driven by tests (TDD):

### Submission Validation
- Global required field enforcement.
- Per-meetup required custom question enforcement.
- Duplicate detection (email + title + meetup).
- CAPTCHA validation.
- CFP window enforcement (reject submissions to closed CFPs).
- Event archival enforcement.
- Meetup active status enforcement.

### Dynamic Form Assembly
- Given a set of selected meetup IDs, produce the correct set of optional + custom fields.
- Handle overlapping optional fields across meetups (union, no duplicates).
- Custom questions grouped correctly by meetup.

### Permission Checks
- Role hierarchy enforcement (each role inherits lower roles).
- Per-meetup role scoping (user can only access meetups they have roles on).
- Super-admin bypass (access to everything).
- Action-level checks: who can vote, who can change status, who can edit meetup settings, etc.

### Status Transitions
- Valid transition enforcement (e.g., can't go from "Submitted" directly to "Presented").
- Audit log creation on every transition.
- Scheduled date required when moving to "Scheduled" status.

### Withdrawal Flow
- Token validation.
- Per-meetup withdrawal (not all-or-nothing).
- Already-withdrawn entries shown but not actionable.

### Export Generation
- CSV format correctness with proper column handling for custom questions.
- JSON nested structure correctness.
- Filter state respected in export output.
- Role-based export access.

### Dashboard Warnings
- "No scheduled speaker" detection per meetup.
- Correct scoping (only future dates count).

### Bulk Actions
- Status changes applied to all selected submissions.
- Permission checks on bulk operations.
- Audit log entries created for each individual change in bulk.
