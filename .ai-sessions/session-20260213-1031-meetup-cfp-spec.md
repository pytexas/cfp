# Session Summary: meetup-cfp Specification Design

**Date**: 2026-02-13 10:31
**Directory**: `/Users/masonegger/Code/PyTexas/cfp`

---

## Recap

Conducted an iterative brainstorming session to develop a comprehensive specification for **meetup-cfp** — a multi-meetup Call for Proposals platform. The session followed a structured Q&A format (13 questions) to capture all requirements before producing a detailed spec document.

## Key Decisions Made

| Area | Decision |
|------|----------|
| Tech Stack | Django 5.x + Tailwind CSS (django-tailwind-cli) + HTMX + Alpine.js |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | django-allauth with GitHub & Google OAuth |
| Deployment | Docker Compose on self-hosted VPS |
| Architecture | Single org, flat meetup hierarchy, 6 Django apps |
| Permissions | Read → Reviewer → Write → Admin → Super-Admin (per-meetup) |
| Public Surface | Minimal — submission forms only, no event listings or history |
| Communication | Manual — app tracks status only, no automated emails |
| Spam Prevention | CAPTCHA |
| File Storage | Local Docker volume mount |

## Session Flow (Prompts & Questions)

1. **Tech stack** → Django, Tailwind CLI, HTMX, Alpine.js, SQLite/PostgreSQL, django-allauth
2. **Org & meetup structure** → Single org, flat hierarchy, meetups have own identity
3. **CFP submission flow** → Org landing with multi-submit, individual meetup pages, no account needed
4. **Custom questions & form config** → Global base fields (super-admin), custom questions per meetup, HTMX dynamic loading
5. **Submission lifecycle** → Submitted → Under Review → Accepted/Rejected/Waitlisted/Withdrawn, then post-acceptance flow
6. **Communication & speaker mgmt** → Manual tracking, notes per meetup per submission, no auto-emails, bulk actions
7. **Permissions deep dive** → 5-tier hierarchy with clear capability boundaries
8. **Meetup events & CFP windows** → Year-round default, time-boxable, special events with custom URLs
9. **Dashboard & reporting** → Actionable dashboards, "no speaker scheduled" warnings, CSV/JSON export
10. **Public-facing pages** → Submission forms only, meetup branding (inherits from org by default)
11. **Project structure & deployment** → 6 Django apps, docker-compose, uv package management
12. **Data retention & security** → Manual retention, CAPTCHA, never-expiring withdrawal tokens, local file storage
13. **Multi-submit UX & edge cases** → Checkboxes + select all, block dupes, per-meetup withdrawal, meetup archival

## Deliverable

- **`spec.md`** — Comprehensive specification covering data models (14 models), submission lifecycle, permission model, public pages, dashboard views, HTMX dynamic form behavior, deployment config, and TDD-ready business logic components.

## Observations

- The iterative one-question-at-a-time approach was effective for teasing out edge cases (withdrawal scope, duplicate detection, multi-submit with different custom questions).
- The user had clear preferences and made fast decisions — minimal back-and-forth needed.
- HTMX dynamic form assembly for multi-submit is the most complex frontend feature and was documented in detail.
- The "no speaker scheduled" warning was a user-suggested feature that adds real operational value.
- Initially wrote spec.md to the wrong directory (2026 site project); corrected to cfp directory.

## Efficiency Insights

- **What went well**: Structured Q&A prevented scope creep. Each question built logically on the last.
- **Could improve**: Could have confirmed the target directory at the start of the session rather than writing to the wrong location.
- **Spec completeness**: The testable business logic section at the end maps directly to TDD test suites, which aligns with the user's development philosophy.

## Process Improvements

- Start brainstorming sessions by confirming the target project directory.
- Consider numbering spec sections with priority/implementation order for the planning phase.
- The spec could benefit from a data flow diagram or sequence diagram for the multi-submit HTMX flow.

## Metrics

- **Conversation turns**: ~28 (13 Q&A pairs + setup + summary)
- **Total cost**: ~$3-5 estimated (primarily Opus 4.6 for the full brainstorm session)
- **Time**: ~20 minutes of wall-clock interaction
- **Output**: 1 spec file (~400 lines)
