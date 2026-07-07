# meetup-cfp Implementation Todo

## Step 1: Project Scaffolding & Configuration
- [ ] 1.1 Initialize pyproject.toml with uv (Django 6.0, temporalio, httpx, dev deps, ruff, mypy, pytest + pytest-asyncio config)
- [ ] 1.2 Create Django project structure (`django-admin startproject meetup_cfp .`)
- [ ] 1.3 Split settings into base/dev/prod (incl. TIME_ZONE and TEMPORAL_* env settings)
- [ ] 1.4 Create the six app directories (core, meetups, submissions, reviews, users, dashboard)
- [ ] 1.5 Create minimal users app (CustomUser with is_superadmin)
- [ ] 1.6 Create Justfile with common commands (incl. worker recipe)
- [ ] 1.7 Run initial migrations
- [ ] 1.8 Create smoke test, base template, and root URL
- [ ] 1.9 Verify `just check` passes

## Step 2: Core App — Organization & Global Fields
- [ ] 2.1 RED: Model tests for Organization singleton (pk=1 enforcement)
- [ ] 2.2 GREEN: Implement Organization model + data migration for pk=1 row
- [ ] 2.3 RED: Model tests for GlobalFormField (email/url types, is_core protection)
- [ ] 2.4 GREEN: Implement GlobalFormField model
- [ ] 2.5 RED: Model tests for StandardOptionalField
- [ ] 2.6 GREEN: Implement StandardOptionalField model
- [ ] 2.7 RED: Tests for seed_global_fields management command
- [ ] 2.8 GREEN: Implement seed_global_fields management command
- [ ] 2.9 Run migrations and verify `just check` passes

## Step 3: Users App — Custom User & Role Model
- [ ] 3.1 RED: Tests for role hierarchy
- [ ] 3.2 GREEN: Implement MeetupRole model and permission utilities
- [ ] 3.3 RED: Tests for permission decorators/mixins
- [ ] 3.4 GREEN: Implement MeetupRoleRequiredMixin
- [ ] 3.5 Run migrations and verify `just check` passes

## Step 4: Meetups App — Meetup & Event Models
- [ ] 4.1 RED: Tests for Meetup model, CFP logic, grace period, branding fallback
- [ ] 4.2 GREEN: Implement Meetup model (grace_period_minutes, webhook_url, webhook_secret)
- [ ] 4.3 RED: Tests for Event model, CFP logic, grace period
- [ ] 4.4 GREEN: Implement Event model
- [ ] 4.5 RED: Tests for MeetupOptionalFieldConfig (is_enabled + is_required)
- [ ] 4.6 GREEN: Implement MeetupOptionalFieldConfig
- [ ] 4.7 RED: Tests for CustomQuestion
- [ ] 4.8 GREEN: Implement CustomQuestion model
- [ ] 4.9 Run migrations and verify `just check` passes

## Step 5: Submissions App — Submission & Field Response Models
- [ ] 5.1 RED: Tests for Submission model
- [ ] 5.2 GREEN: Implement Submission model
- [ ] 5.3 RED: Tests for SubmissionMeetup (nulls_distinct-equivalent uniqueness)
- [ ] 5.4 GREEN: Implement SubmissionMeetup model (+ PG-only DB constraint migration)
- [ ] 5.5 RED: Tests for SubmissionFieldResponse (exactly-one-FK, value_text only)
- [ ] 5.6 GREEN: Implement SubmissionFieldResponse model
- [ ] 5.7 RED: Tests for FileUpload model (one-to-one, content_type, size_bytes)
- [ ] 5.8 GREEN: Implement FileUpload model
- [ ] 5.9 Run migrations and verify `just check` passes

## Step 6: Reviews App — Votes, Notes, Transition Table
- [ ] 6.1 RED: Tests encoding the full normative transition table (incl. undo paths, scheduled_date rules)
- [ ] 6.2 GREEN: Implement pure reviews/transitions.py (no Django imports)
- [ ] 6.3 RED: Tests for apply_transition persistence service
- [ ] 6.4 GREEN: Implement reviews/persistence.py
- [ ] 6.5 RED: Tests for Review (Vote) model + record_vote
- [ ] 6.6 GREEN: Implement Review model
- [ ] 6.7 GREEN: Implement Note and StatusChange models
- [ ] 6.8 Run migrations and verify `just check` passes

## Step 7: Permission System & Test Factories
- [ ] 7.1 Create test factories for all models
- [ ] 7.2 RED: Integration tests for permission checks across all role levels
- [ ] 7.3 RED: Tests for the role assignment matrix
- [ ] 7.4 GREEN: Permission helper functions incl. can_assign_role
- [ ] 7.5 REFACTOR: Clean up permission functions
- [ ] 7.6 Run `just check`

## Step 8: Temporal Foundation — Client, Worker, Test Harness
- [ ] 8.1 GREEN: Create core/temporal.py client helper (get_temporal_client, sync_execute)
- [ ] 8.2 GREEN: Create core/worker.py registry and run_worker management command
- [ ] 8.3 RED: Harness smoke test with WorkflowEnvironment.start_time_skipping
- [ ] 8.4 GREEN: Make the smoke test pass (async config, sandbox setup)
- [ ] 8.5 Wire Justfile worker recipe and run `just check`

## Step 9: Submission Lifecycle Workflow & Transition Service
- [ ] 9.1 GREEN: persist_transition activity + reviews/messages.py dataclasses
- [ ] 9.2 RED: Lifecycle workflow tests (legal/illegal transitions, scheduled_date, unschedule, terminal completion, query)
- [ ] 9.3 GREEN: Implement SubmissionLifecycleWorkflow (update + validator) and register with worker
- [ ] 9.4 RED: Tests for the Django-side transition service (update-with-start, error translation)
- [ ] 9.5 GREEN: Implement reviews/services.request_transition
- [ ] 9.6 REFACTOR: Module hygiene check and `just check`

## Step 10: Submission Intake Workflow & Intake Service
- [ ] 10.1 RED: Tests for persist_intake (one transaction, idempotent on token)
- [ ] 10.2 GREEN: Implement submissions/persistence.py, activities.py, messages.py
- [ ] 10.3 RED: Intake workflow tests (child starts with ABANDON, duplicate start no-op, result shape)
- [ ] 10.4 GREEN: Implement SubmissionIntakeWorkflow and register with worker
- [ ] 10.5 RED: Tests for the Django-side intake service (file paths not bytes)
- [ ] 10.6 GREEN: Implement submissions/services.start_intake
- [ ] 10.7 Run `just check`

## Step 11: Webhook Delivery
- [ ] 11.1 RED: Tests for payload building and HMAC signing
- [ ] 11.2 GREEN: Implement meetups/webhooks.py (pure functions)
- [ ] 11.3 RED: Tests for the delivery activity function
- [ ] 11.4 GREEN: Implement deliver_webhook activity + retry policy
- [ ] 11.5 RED: Workflow integration tests (status_changed + submission.received scheduling, non-blocking failures)
- [ ] 11.6 GREEN: Wire delivery into lifecycle and intake workflows
- [ ] 11.7 Run `just check`

## Step 12: Public Pages — Org Landing & Meetup Pages
- [ ] 12.1 Set up Tailwind CSS and update base template (HTMX + Alpine)
- [ ] 12.2 RED: View tests for org landing page
- [ ] 12.3 GREEN: Implement org landing page
- [ ] 12.4 RED: View tests for meetup page
- [ ] 12.5 GREEN: Implement meetup page
- [ ] 12.6 RED: View tests for event page
- [ ] 12.7 GREEN: Implement event page
- [ ] 12.8 Run `just check`

## Step 13: Dynamic Multi-Submit Form (HTMX)
- [ ] 13.1 RED: Tests for dynamic field assembly (union, required-ORed, grouping)
- [ ] 13.2 GREEN: Implement dynamic field assembly
- [ ] 13.3 RED: Tests for HTMX dynamic fields endpoint (incl. tampered-id 400s)
- [ ] 13.4 GREEN: Implement HTMX dynamic fields endpoint
- [ ] 13.5 GREEN: Build multi-submit form page (Select All via Alpine)
- [ ] 13.6 GREEN: Build single-meetup and event submission forms
- [ ] 13.7 Run `just check`

## Step 14: Submission Validation & Intake Wiring
- [ ] 14.1 RED: Tests for duplicate detection (normalized, withdrawn excluded)
- [ ] 14.2 GREEN: Implement duplicate detection
- [ ] 14.3 RED: Tests for CFP window enforcement incl. grace period, all-or-nothing
- [ ] 14.4 GREEN: Implement validate_targets_open
- [ ] 14.5 RED: Tests for file validation and CAPTCHA verification
- [ ] 14.6 GREEN: Implement file validation and captcha module
- [ ] 14.7 RED: Tests for form submission views (validation pipeline, intake called, confirmation)
- [ ] 14.8 GREEN: Implement form submission POST handlers wired to start_intake
- [ ] 14.9 Run `just check`

## Step 15: Withdrawal Flow
- [ ] 15.1 RED: Tests for withdrawal logic (context, actionable flags, transition service routing)
- [ ] 15.2 GREEN: Implement withdrawal logic
- [ ] 15.3 RED: Tests for withdrawal views (404s, disabled entries, confirmation)
- [ ] 15.4 GREEN: Implement withdrawal views
- [ ] 15.5 Run `just check`

## Step 16: Dashboard — Authentication & Layout
- [ ] 16.1 Configure django-allauth
- [ ] 16.2 RED: Tests for dashboard access control (full access error contract)
- [ ] 16.3 GREEN: Implement dashboard base views
- [ ] 16.4 REFACTOR: Create allauth template overrides
- [ ] 16.5 Run `just check`

## Step 17: Dashboard — Meetup Submissions View
- [ ] 17.1 RED: Tests for submission filtering logic
- [ ] 17.2 GREEN: Implement submission filtering
- [ ] 17.3 RED: Tests for submissions list view
- [ ] 17.4 GREEN: Implement submissions list view
- [ ] 17.5 Run `just check`

## Step 18: Dashboard — Submission Detail & Reviews
- [ ] 18.1 RED: Tests for submission detail view (404 contract, other-meetups panel)
- [ ] 18.2 GREEN: Implement submission detail view
- [ ] 18.3 RED: Tests for voting
- [ ] 18.4 GREEN: Implement voting
- [ ] 18.5 RED: Tests for notes
- [ ] 18.6 GREEN: Implement notes
- [ ] 18.7 RED: Tests for status management via the transition service
- [ ] 18.8 GREEN: Implement status management (legal-transitions-only controls, history, Mark Email Sent)
- [ ] 18.9 Run `just check`

## Step 19: Dashboard — Bulk Actions
- [ ] 19.1 RED: Tests for bulk status change (all-or-nothing pre-validation, race reporting)
- [ ] 19.2 GREEN: Implement bulk_change_status
- [ ] 19.3 GREEN: Implement bulk action view + UI
- [ ] 19.4 Run `just check`

## Step 20: Dashboard — Export (CSV/JSON)
- [ ] 20.1 RED: Tests for CSV export (column naming, empty cells, privacy)
- [ ] 20.2 GREEN: Implement CSV export
- [ ] 20.3 RED: Tests for JSON export
- [ ] 20.4 GREEN: Implement JSON export
- [ ] 20.5 GREEN: Implement export view and wire up UI
- [ ] 20.6 Run `just check`

## Step 21: Dashboard — Super-Admin Views & Warnings
- [ ] 21.1 RED: Tests for dashboard warnings
- [ ] 21.2 GREEN: Implement warning logic
- [ ] 21.3 RED: Tests for metrics (acceptance rate, n/a case, month boundary)
- [ ] 21.4 GREEN: Implement metrics module
- [ ] 21.5 RED: Tests for super-admin dashboard view
- [ ] 21.6 GREEN: Implement super-admin dashboard (cards, breakdown, activity feed)
- [ ] 21.7 RED: Tests for management views (meetups, global fields, roles, settings, events)
- [ ] 21.8 GREEN: Implement management views
- [ ] 21.9 Run `just check`

## Step 22: Media Access Control
- [ ] 22.1 RED: Tests for upload path routing (headshots/ vs protected/)
- [ ] 22.2 GREEN: Implement upload path routing
- [ ] 22.3 RED: Tests for the protected media view (redirect/403/200, X-Accel-Redirect, dev fallback)
- [ ] 22.4 GREEN: Implement the protected media view
- [ ] 22.5 Run `just check`

## Step 23: Management Commands & Data Seeding
- [ ] 23.1 RED: Tests for seed_global_fields idempotency edge cases
- [ ] 23.2 GREEN: Harden seed_global_fields
- [ ] 23.3 RED: Tests for create_test_data command
- [ ] 23.4 GREEN: Implement create_test_data command
- [ ] 23.5 Verify full bootstrap sequence (incl. worker + dev server end-to-end)
- [ ] 23.6 Run `just check`

## Step 24: Docker & Production Configuration
- [ ] 24.1 Create Dockerfile
- [ ] 24.2 Create docker-compose.yml (web, worker, temporal, temporal-ui, db, nginx)
- [ ] 24.3 Create nginx configuration (public headshots, internal protected media)
- [ ] 24.4 Create .env.example (incl. TEMPORAL_* vars)
- [ ] 24.5 Create entrypoint scripts (web + worker)
- [ ] 24.6 Update production settings
- [ ] 24.7 Write README (setup, architecture, documented timezone behavior)
- [ ] 24.8 Test Docker build and verify all services
- [ ] 24.9 Run final `just check`
