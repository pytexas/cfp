# Session: 2026-07-02, Portfolio Audit Step 13, CFP Spec Review

Adversarial review of `spec.md` (P2 stage of the portfolio audit).
Repo is planning-only; no code exists, so staleness was checked against the named stack instead.
Work done on branch `portfolio-audit`.

## What Changed in spec.md

Contradictions fixed:

- `SubmissionFieldResponse.global_field` vs the dedicated `Submission` columns: core six global fields now map to columns (explicit mapping table, `is_core` flag, protected from deletion); only non-core global fields store responses.
- `SubmissionFieldResponse.value_file` vs the separate `FileUpload` model: `value_file` removed, `FileUpload` (one-to-one to the response) is the single file store.
- Multi-submit validation referenced "optional fields required by a meetup" but no model carried a required flag: added `is_required` to `MeetupOptionalFieldConfig`.
- Seeded fields used types ("email", "URL") missing from the field_type enum: added `email` and `url` types with Django validator semantics.
- `StatusChange.changed_by` was non-nullable but speakers (no account) change status via withdrawal: now nullable, null = speaker.
- Event forms: clarified they show event custom questions only, not the meetup's default-CFP questions.

Testability and error contracts added:

- Normative status transition table (Mermaid diagram plus table); invalid transitions rejected with no side effects and no audit row.
- Duplicate detection scope pinned to normalized (email, title, meetup, event), all-or-nothing on multi-submit.
- `SubmissionMeetup` unique constraint needs `nulls_distinct=False` or it is a no-op for default-CFP rows.
- File upload limits (10 MB, allowed types) and auth-gated media serving via nginx `X-Accel-Redirect`.
- Access error contract for dashboards (login redirect, 403, empty state), 404 rules for deactivated meetups/unknown slugs/bad tokens.
- CAPTCHA failure, zero-meetups-selected, and render-to-submit race condition contracts.
- Dashboard metric definitions (acceptance rate formula, calendar-month boundary, 20-item activity feed, scheduled-speaker warning uses today-or-future).
- Role assignment matrix (who can grant which roles); app import-boundary rule.
- Bulk actions are atomic; one illegal transition rejects the batch.
- Vote changes update in place (added `updated_at`); Event slug uniqueness scoped to (meetup, slug); Organization singleton enforced via data migration + pk=1.

Staleness updates (planning doc from 2026-02, stack checked 2026-07):

- Pinned Django 5.2 LTS (6.0 exists; raised as Open Question 9).
- Noted allauth 65.x `AccountMiddleware` requirement (65.18.0 current, supports Django 6.0).
- Noted django-tailwind-cli 4.2+ is Tailwind 4 only, CSS-based config, no Node.
- Confirmed HTMX 2.x attribute syntax; added `hx-include` for the checkbox group.
- Added `CSRF_TRUSTED_ORIGINS` and `TIME_ZONE` env vars; startup contract (migrate/collectstatic in entrypoint, tailwind build at image build).
- Gave Alpine.js an explicit job or the door (Open Question 1).

Structure and style:

- Added "## Available Tooling" declaring the `python:python` skill.
- Added "## Open Questions" with 11 items for /bpe:brainstorm.
- Writing rules applied: one sentence per line, em-dashes removed, horizontal-rule separators removed, plain voice.

## Known Issue Left Alone

`commit-msg.md` is tracked and not in `.gitignore`.
Flagged for the plan-regeneration step per the audit contract; not fixed here.

## Follow-Ups

- `plan.md` and `todo.md` were generated from the old spec and are now stale against these changes; regenerate after Mason resolves the Open Questions.
- `CLAUDE.md` still says "Django 5.x" and describes the old lifecycle prose; update alongside plan regeneration.
