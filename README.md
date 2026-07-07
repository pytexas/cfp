# cfp

Web application for managing CFPs for various meetups. See `spec.md` for the
full specification and `CLAUDE.md` for architecture notes.

## Stack

Django 6.0 · Tailwind CSS 4.x (`django-tailwind-cli`, no Node.js) · HTMX 2.x ·
Alpine.js 3.x · SQLite (dev) / PostgreSQL 16 (prod) · `uv`.

The frontend JS libraries are vendored as static files under `assets/js/`
(`htmx.min.js`, `alpine.min.js`) and loaded from `templates/base.html` — no
runtime CDN dependency. Tailwind is compiled from `assets/css/source.css` to
`assets/css/tailwind.css`.

## Local setup

```bash
uv sync
```

Fetch the standalone Tailwind CLI (this Python build can't auto-download it —
missing system CA certs — so `TAILWIND_CLI_AUTOMATIC_DOWNLOAD` is off and the
binary lives at `.tailwind/tailwindcss`, git-ignored):

```bash
mkdir -p .tailwind
curl -fsSL https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.3/tailwindcss-macos-arm64 \
  -o .tailwind/tailwindcss && chmod +x .tailwind/tailwindcss
```

(Swap the asset name for your platform, e.g. `tailwindcss-linux-x64`.)

Then:

```bash
uv run python manage.py migrate
uv run python manage.py tailwind build   # compile assets/css/tailwind.css
uv run python manage.py runserver
```

Visit http://127.0.0.1:8000/ — the landing page is a smoke test that Tailwind,
Alpine, and HTMX are all wired up. During development, `manage.py tailwind
watch` (or `tailwind runserver`) rebuilds CSS on change.

## Settings

Settings are a package under `meetup_cfp/settings/` (`base.py` + `dev.py`); the
active module defaults to `meetup_cfp.settings.dev`. Datetimes are stored in UTC
(`USE_TZ = True`) with a single org-wide display timezone via `TIME_ZONE`.
