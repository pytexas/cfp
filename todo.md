# meetup-cfp Implementation Todo

## Step 1: Project Scaffolding & Configuration
- [ ] 1.1 Initialize pyproject.toml with uv (dependencies, dev deps, ruff, mypy, pytest config)
- [ ] 1.2 Run `uv sync` to install dependencies
- [ ] 1.3 Create Django project structure (`django-admin startproject meetup_cfp .`)
- [ ] 1.4 Split settings into base/dev/prod
- [ ] 1.5 Create the six app directories (core, meetups, submissions, reviews, users, dashboard)
- [ ] 1.6 Create minimal users app (CustomUser with is_superadmin)
- [ ] 1.7 Create Justfile with common commands
- [ ] 1.8 Run initial migrations
- [ ] 1.9 Create smoke test, base template, and root URL
- [ ] 1.10 Verify `just check` passes

## Step 2: Core App — Organization & Global Fields
- [ ] 2.1 RED: Write model tests for Organization singleton
- [ ] 2.2 GREEN: Implement Organization model
- [ ] 2.3 RED: Write model tests for GlobalFormField
- [ ] 2.4 GREEN: Implement GlobalFormField model
- [ ] 2.5 RED: Write model tests for StandardOptionalField
- [ ] 2.6 GREEN: Implement StandardOptionalField model
- [ ] 2.7 RED: Write tests for seed_global_fields management command
- [ ] 2.8 GREEN: Implement seed_global_fields management command
- [ ] 2.9 Run migrations and verify `just check` passes

## Step 3: Users App — Custom User & Role Model
- [ ] 3.1 RED: Write tests for role hierarchy
- [ ] 3.2 GREEN: Implement MeetupRole model and permission utilities
- [ ] 3.3 RED: Write tests for permission decorators/mixins
- [ ] 3.4 GREEN: Implement MeetupRoleRequiredMixin
- [ ] 3.5 Run migrations and verify `just check` passes

## Step 4: Meetups App — Meetup & Event Models
- [ ] 4.1 RED: Write tests for Meetup model and CFP logic
- [ ] 4.2 GREEN: Implement Meetup model
- [ ] 4.3 RED: Write tests for Event model and CFP logic
- [ ] 4.4 GREEN: Implement Event model
- [ ] 4.5 RED: Write tests for MeetupOptionalFieldConfig
- [ ] 4.6 GREEN: Implement MeetupOptionalFieldConfig
- [ ] 4.7 RED: Write tests for CustomQuestion
- [ ] 4.8 GREEN: Implement CustomQuestion model
- [ ] 4.9 Run migrations and verify `just check` passes

## Step 5: Submissions App — Submission & Field Response Models
- [ ] 5.1 RED: Write tests for Submission model
- [ ] 5.2 GREEN: Implement Submission model
- [ ] 5.3 RED: Write tests for SubmissionMeetup
- [ ] 5.4 GREEN: Implement SubmissionMeetup model
- [ ] 5.5 RED: Write tests for SubmissionFieldResponse
- [ ] 5.6 GREEN: Implement SubmissionFieldResponse model
- [ ] 5.7 RED: Write tests for FileUpload model
- [ ] 5.8 GREEN: Implement FileUpload model
- [ ] 5.9 Run migrations and verify `just check` passes

## Step 6: Reviews App — Voting, Notes, Status Transitions
- [ ] 6.1 RED: Write tests for valid status transitions
- [ ] 6.2 GREEN: Implement status transition logic
- [ ] 6.3 RED: Write tests for Review (Vote) model
- [ ] 6.4 GREEN: Implement Review model
- [ ] 6.5 RED: Write tests for Note model
- [ ] 6.6 GREEN: Implement Note model
- [ ] 6.7 GREEN: Implement StatusChange model
- [ ] 6.8 Run migrations and verify `just check` passes

## Step 7: Permission System — Hierarchy Enforcement
- [ ] 7.1 Create test factories for all models
- [ ] 7.2 RED: Write integration tests for permission checks across all role levels
- [ ] 7.3 GREEN: Create helper functions for common permission checks
- [ ] 7.4 REFACTOR: Clean up permission functions
- [ ] 7.5 Run `just check`

## Step 8: Public Pages — Org Landing & Meetup Pages
- [ ] 8.1 Set up Tailwind CSS and update base template
- [ ] 8.2 RED: Write view tests for org landing page
- [ ] 8.3 GREEN: Implement org landing page
- [ ] 8.4 RED: Write view tests for meetup page
- [ ] 8.5 GREEN: Implement meetup page
- [ ] 8.6 RED: Write view tests for event page
- [ ] 8.7 GREEN: Implement event page
- [ ] 8.8 Run `just check`

## Step 9: Dynamic Multi-Submit Form (HTMX)
- [ ] 9.1 RED: Write tests for dynamic field assembly logic
- [ ] 9.2 GREEN: Implement dynamic field assembly
- [ ] 9.3 RED: Write tests for HTMX dynamic fields endpoint
- [ ] 9.4 GREEN: Implement HTMX dynamic fields endpoint
- [ ] 9.5 GREEN: Build multi-submit form page
- [ ] 9.6 GREEN: Build single-meetup submission form
- [ ] 9.7 GREEN: Build event submission form
- [ ] 9.8 Run `just check`

## Step 10: Submission Validation & Duplicate Detection
- [ ] 10.1 RED: Write tests for duplicate detection logic
- [ ] 10.2 GREEN: Implement duplicate detection
- [ ] 10.3 RED: Write tests for CFP window enforcement
- [ ] 10.4 GREEN: Implement CFP validation
- [ ] 10.5 RED: Write tests for submission creation service
- [ ] 10.6 GREEN: Implement submission creation service
- [ ] 10.7 RED: Write tests for form submission views
- [ ] 10.8 GREEN: Implement form submission views
- [ ] 10.9 Run `just check`

## Step 11: Withdrawal Flow
- [ ] 11.1 RED: Write tests for withdrawal logic
- [ ] 11.2 GREEN: Implement withdrawal logic
- [ ] 11.3 RED: Write tests for withdrawal views
- [ ] 11.4 GREEN: Implement withdrawal views
- [ ] 11.5 Run `just check`

## Step 12: Dashboard — Authentication & Layout
- [ ] 12.1 Configure django-allauth
- [ ] 12.2 RED: Write tests for dashboard access control
- [ ] 12.3 GREEN: Implement dashboard base views
- [ ] 12.4 REFACTOR: Create allauth template overrides
- [ ] 12.5 Run `just check`

## Step 13: Dashboard — Meetup Submissions View
- [ ] 13.1 RED: Write tests for submission filtering logic
- [ ] 13.2 GREEN: Implement submission filtering
- [ ] 13.3 RED: Write tests for submissions list view
- [ ] 13.4 GREEN: Implement submissions list view
- [ ] 13.5 Run `just check`

## Step 14: Dashboard — Submission Detail & Reviews
- [ ] 14.1 RED: Write tests for submission detail view
- [ ] 14.2 GREEN: Implement submission detail view
- [ ] 14.3 RED: Write tests for voting
- [ ] 14.4 GREEN: Implement voting
- [ ] 14.5 RED: Write tests for notes
- [ ] 14.6 GREEN: Implement notes
- [ ] 14.7 RED: Write tests for status management
- [ ] 14.8 GREEN: Implement status management
- [ ] 14.9 Run `just check`

## Step 15: Dashboard — Bulk Actions & Status Management
- [ ] 15.1 RED: Write tests for bulk status change
- [ ] 15.2 GREEN: Implement bulk status change logic
- [ ] 15.3 GREEN: Implement bulk action view
- [ ] 15.4 Run `just check`

## Step 16: Dashboard — Export (CSV/JSON)
- [ ] 16.1 RED: Write tests for CSV export
- [ ] 16.2 GREEN: Implement CSV export
- [ ] 16.3 RED: Write tests for JSON export
- [ ] 16.4 GREEN: Implement JSON export
- [ ] 16.5 GREEN: Implement export view and wire up UI
- [ ] 16.6 Run `just check`

## Step 17: Dashboard — Super-Admin Views & Warnings
- [ ] 17.1 RED: Write tests for dashboard warnings
- [ ] 17.2 GREEN: Implement warning logic
- [ ] 17.3 RED: Write tests for super-admin dashboard view
- [ ] 17.4 GREEN: Implement super-admin dashboard
- [ ] 17.5 RED: Write tests for meetup management views
- [ ] 17.6 GREEN: Implement meetup management views
- [ ] 17.7 GREEN: Implement meetup admin views (per-meetup settings, events)
- [ ] 17.8 Run `just check`

## Step 18: Management Commands & Data Seeding
- [ ] 18.1 RED: Write tests for seed_standard_fields idempotency
- [ ] 18.2 GREEN: Ensure seed_global_fields handles edge cases
- [ ] 18.3 RED: Write tests for create_test_data command
- [ ] 18.4 GREEN: Implement create_test_data command
- [ ] 18.5 Verify full bootstrap sequence
- [ ] 18.6 Run `just check`

## Step 19: Docker & Production Configuration
- [ ] 19.1 Create Dockerfile
- [ ] 19.2 Create docker-compose.yml
- [ ] 19.3 Create nginx configuration
- [ ] 19.4 Create .env.example
- [ ] 19.5 Create entrypoint script
- [ ] 19.6 Update production settings
- [ ] 19.7 Test Docker build and verify
- [ ] 19.8 Run final `just check`
